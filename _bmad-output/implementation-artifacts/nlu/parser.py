import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

PARSER_VERSION = "1.0"
RULES_PATH = Path(__file__).parent / 'nlu_rules.json'

with open(RULES_PATH, 'r', encoding='utf-8') as f:
    RULES = json.load(f)


def parse_age(text):
    """
    Extract and normalize age from text to standard age ranges.
    Returns tuple: (age_range, raw_age_value, ambiguities)
    """
    ambiguities = []
    
    # Look for explicit numbers
    matches = list(re.finditer(r"\b(\d{1,2})\s*(?:years?\s*old)?\b", text, re.I))
    
    if matches:
        # Check for multiple age values (ambiguity)
        if len(matches) > 1:
            ages = [int(m.group(1)) for m in matches]
            ambiguities.append({
                "reason": "AMBIGUOUS_AGE",
                "value": ", ".join(str(a) for a in ages),
                "suggestion": "Are they all the same age, or did you mention multiple people?"
            })
        
        age = int(matches[0].group(1))
        
        # Check for out-of-range ages
        if age > 120:
            ambiguities.append({
                "reason": "AGE_OUT_OF_RANGE",
                "value": str(age),
                "suggestion": f"Did you mean {age % 100}?"
            })
            return None, age, ambiguities
        
        # Normalize to ranges: teen, 20s, 30s, 40s, 50s, 60+
        if age < 13:
            return 'teen', age, ambiguities
        elif age < 20:
            return 'teen', age, ambiguities
        elif age < 30:
            return '20s', age, ambiguities
        elif age < 40:
            return '30s', age, ambiguities
        elif age < 50:
            return '40s', age, ambiguities
        elif age < 60:
            return '50s', age, ambiguities
        else:
            return '60+', age, ambiguities
    
    # Fallback: keywords for age
    if re.search(r"\b(child|kid|son|daughter|toddler|preschool)\b", text, re.I):
        return 'teen', None, ambiguities
    if re.search(r"\b(teen|teenager|adolescent)\b", text, re.I):
        return 'teen', None, ambiguities
    if re.search(r"\b(senior|elderly|retired|grandfather|grandmother)\b", text, re.I):
        return '60+', None, ambiguities
    
    return None, None, ambiguities


def parse_recipient(text):
    for r, keys in RULES.get('recipient_keywords', {}).items():
        for k in keys:
            if re.search(r"\b" + re.escape(k) + r"\b", text, re.I):
                return r, []
    # default to self
    return 'self', []


def parse_genres(text):
    found = set()
    ambiguities = []
    text_lower = text.lower()
    # detect positive/negative context for genre keywords
    for genre, keys in RULES.get('genre_keywords', {}).items():
        for k in keys:
            for m in re.finditer(r"\b" + re.escape(k) + r"\b", text_lower):
                start = max(0, m.start() - 15)
                prefix = text_lower[start:m.start()]
                # negative context (e.g., "no politics") -> skip here; captured in parse_avoid
                if re.search(r"\b(no|not|don't|dont|avoid|without)\b", prefix):
                    continue
                # positive context near the keyword -> treat as genre
                if re.search(r"\b(like|likes|love|loves|enjoy|enjoys|fond of)\b", prefix):
                    found.add(genre)
                else:
                    # default to positive when no explicit negative marker present
                    found.add(genre)
    
    # Check if any genre keywords were found at all
    if not found and 'genre' in text_lower and len(text_lower) > 10:
        ambiguities.append({
            "reason": "GENRE_UNRECOGNIZED",
            "value": text,
            "suggestion": "Can you name a specific genre? E.g., mystery, romance, sci-fi, fantasy, memoir..."
        })
    
    return list(found), ambiguities


def parse_avoid(text):
    found = []
    text_lower = text.lower()
    # check for negative mentions of explicit avoid keywords
    for k in RULES.get('avoid_keywords', []):
        for m in re.finditer(r"\b" + re.escape(k) + r"\b", text_lower):
            start = max(0, m.start() - 15)
            prefix = text_lower[start:m.start()]
            if re.search(r"\b(no|not|don't|dont|avoid|without)\b", prefix):
                found.append(k)
    # detect negative mentions of genre keywords (e.g., "no politics")
    for genre, keys in RULES.get('genre_keywords', {}).items():
        for k in keys:
            for m in re.finditer(r"\b" + re.escape(k) + r"\b", text_lower):
                start = max(0, m.start() - 15)
                prefix = text_lower[start:m.start()]
                if re.search(r"\b(no|not|don't|dont|avoid|without)\b", prefix):
                    found.append(genre)
    return list(dict.fromkeys(found))


def parse_surprise_level(text):
    for level, keys in RULES.get('surprise_level_keywords', {}).items():
        for k in keys:
            if re.search(re.escape(k), text, re.I):
                return level
    return None


def calculate_confidence(parsed_dict: Dict) -> float:
    """
    Calculate confidence score (0.0-1.0) based on field completeness.
    - Full parse (all 6 fields): 0.95
    - 5 fields: 0.85
    - 4 fields: 0.75
    - 3 fields: 0.60
    - <3 fields: 0.40 or lower
    """
    fields_present = sum([
        parsed_dict.get('recipient') is not None,
        parsed_dict.get('age_range') is not None,
        len(parsed_dict.get('genres', [])) > 0,
        parsed_dict.get('mood') is not None,
        len(parsed_dict.get('avoid', [])) > 0,
        parsed_dict.get('surprise_level') is not None
    ])
    
    if fields_present >= 6:
        return 0.95
    elif fields_present == 5:
        return 0.85
    elif fields_present == 4:
        return 0.75
    elif fields_present == 3:
        return 0.60
    elif fields_present == 2:
        return 0.45
    else:
        return 0.30


def parse_input(text: str) -> Dict:
    """
    Parse free-text gift intent into structured preference object.
    Returns dict with normalized fields and metadata.
    """
    text = text.strip()
    
    if not text:
        return {
            'recipient': 'self',
            'age_range': None,
            'genres': [],
            'avoid': [],
            'surprise_level': None,
            'mood': None,
            'raw': text,
            'confidence': 0.0,
            'parser_version': PARSER_VERSION,
            'ambiguities': [{
                'reason': 'EMPTY_INPUT',
                'value': '',
                'suggestion': 'Could you tell me a bit about who this is for and what they like?'
            }]
        }
    
    all_ambiguities = []
    
    # Parse each field
    recipient, recipient_ambiguities = parse_recipient(text)
    all_ambiguities.extend(recipient_ambiguities)
    
    age_range, raw_age, age_ambiguities = parse_age(text)
    all_ambiguities.extend(age_ambiguities)
    
    genres, genre_ambiguities = parse_genres(text)
    all_ambiguities.extend(genre_ambiguities)
    
    avoid = parse_avoid(text)
    
    surprise_level, surprise_ambiguities = parse_surprise_level(text)
    all_ambiguities.extend(surprise_ambiguities)
    
    # Infer mood from text if not explicitly parsed as surprise_level
    mood = None
    mood_keywords = {
        'adventurous': ['adventure', 'exciting', 'thrilling'],
        'cozy': ['cozy', 'comfort', 'warm', 'relaxing'],
        'thought-provoking': ['thought-provoking', 'philosophical', 'deep'],
        'light': ['light', 'fun', 'funny', 'humorous']
    }
    for m, keywords in mood_keywords.items():
        for kw in keywords:
            if kw in text.lower():
                mood = m
                break
        if mood:
            break
    
    # Detect conflicting signals
    if surprise_level and mood and surprise_level == 'light_hint' and mood == 'adventurous':
        all_ambiguities.append({
            'reason': 'CONFLICTING_MOOD',
            'value': f"{surprise_level} vs {mood}",
            'suggestion': "Should this be a safe pick or an adventurous one?"
        })
    
    parsed = {
        'recipient': recipient,
        'age_range': age_range,
        'genres': genres,
        'avoid': avoid,
        'surprise_level': surprise_level or 'balanced',
        'mood': mood,
        'raw': text,
        'parser_version': PARSER_VERSION,
        'ambiguities': all_ambiguities
    }
    
    # Calculate confidence
    parsed['confidence'] = calculate_confidence(parsed)
    
    # Check for partial parse (multiple fields empty)
    empty_fields = sum([
        parsed['recipient'] is None,
        parsed['age_range'] is None,
        len(parsed['genres']) == 0,
        len(parsed['avoid']) == 0,
        parsed['surprise_level'] is None
    ])
    
    if empty_fields >= 3:
        all_ambiguities.append({
            'reason': 'PARTIAL_PARSE',
            'value': text,
            'suggestion': 'Could you give me a bit more detail about who this is for and what they like?'
        })
        parsed['ambiguities'] = all_ambiguities
    
    return parsed


if __name__ == '__main__':
    samples = [
        "I am looking for a gift for my friend who is 40 years old and likes horror books",
        "I want a gift for my son who is 8 and loves dinosaurs",
        "Surprise me — full surprise, no politics please",
        "I need something romantic for my wife, hint please"
    ]
    for s in samples:
        print('INPUT:', s)
        print('PARSE:', parse_input(s))
        print('---')
