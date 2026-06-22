import re
import json
from pathlib import Path

RULES_PATH = Path(__file__).parent / 'nlu_rules.json'

with open(RULES_PATH, 'r', encoding='utf-8') as f:
    RULES = json.load(f)


def parse_age(text):
    # look for explicit numbers
    m = re.search(r"\b(\d{1,2})\s*(?:years?\s*old)?\b", text, re.I)
    if m:
        age = int(m.group(1))
        if age < 12:
            return 'under-12'
        if age < 18:
            return 'under-18'
        if age < 25:
            return '18-24'
        if age < 35:
            return '25-34'
        if age < 45:
            return '35-44'
        return '45+'
    # fallback: keywords
    if re.search(r"\b(child|kid|son|daughter)\b", text, re.I):
        return 'under-12'
    return None


def parse_recipient(text):
    for r, keys in RULES.get('recipient_keywords', {}).items():
        for k in keys:
            if re.search(r"\b" + re.escape(k) + r"\b", text, re.I):
                return r
    # default to self
    return 'self'


def parse_genres(text):
    found = set()
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
    return list(found)


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


def parse_input(text):
    text = text.strip()
    return {
        'raw': text,
        'recipient': parse_recipient(text),
        'age_range': parse_age(text),
        'genres': parse_genres(text),
        'avoid': parse_avoid(text),
        'surprise_level': parse_surprise_level(text)
    }


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
