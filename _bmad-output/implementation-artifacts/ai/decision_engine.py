"""
Decision Engine for Book Recommendation
Scores and ranks book candidates based on user preferences
"""

import json
import os
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from datetime import datetime

PARSER_VERSION = "2.0"

# Scoring weights
GENRE_WEIGHT = 0.4
MOOD_WEIGHT = 0.3
AGE_WEIGHT = 0.2
PENALTY_WEIGHT = 0.1

# Duplicate penalty
DELIVERED_PENALTY = 0.15

# Candidate pool size
MAX_CANDIDATES = 10


@dataclass
class Book:
    """Represents a book in the catalog"""
    book_id: str
    title: str
    author: str
    genres: List[str]
    mood_keywords: List[str]
    min_age: str
    max_age: str
    avoid_keywords: List[str]
    cover_url: str
    price: float
    description: str


@dataclass
class Preference:
    """User preference profile"""
    recipient_type: str
    recipient_age_range: str
    genres: List[str]
    avoid: List[str]
    surprise_level: str
    mood: Optional[str] = None


def load_book_catalog() -> List[Book]:
    """Load books from JSON catalog"""
    catalog_path = os.path.join(os.path.dirname(__file__), 'book_catalog.json')
    with open(catalog_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    books = []
    for book_data in data['books']:
        books.append(Book(
            book_id=book_data['book_id'],
            title=book_data['title'],
            author=book_data['author'],
            genres=book_data['genres'],
            mood_keywords=book_data['mood_keywords'],
            min_age=book_data['min_age'],
            max_age=book_data['max_age'],
            avoid_keywords=book_data['avoid_keywords'],
            cover_url=book_data['cover_url'],
            price=book_data['price'],
            description=book_data['description']
        ))
    return books


def age_range_order() -> Dict[str, int]:
    """Define ordering for age ranges"""
    return {
        'teen': 0,
        '20s': 1,
        '30s': 2,
        '40s': 3,
        '50s': 4,
        '60+': 5
    }


def is_age_in_range(user_age: str, book_min: str, book_max: str) -> bool:
    """Check if user age is within book's recommended range"""
    order = age_range_order()
    user_idx = order.get(user_age, 2)  # Default to 30s if unknown
    min_idx = order.get(book_min, 0)
    max_idx = order.get(book_max, 5)
    return min_idx <= user_idx <= max_idx


def calculate_genre_match(user_genres: List[str], book_genres: List[str]) -> float:
    """Calculate Jaccard similarity for genres"""
    if not user_genres and not book_genres:
        return 0.5  # No preference and no genres → neutral
    
    user_set = set(user_genres)
    book_set = set(book_genres)
    
    if not (user_set | book_set):
        return 0.0
    
    intersection = len(user_set & book_set)
    union = len(user_set | book_set)
    
    return intersection / union if union > 0 else 0.0


def calculate_mood_match(user_mood: Optional[str], mood_keywords: List[str]) -> float:
    """Calculate mood match via keyword matching"""
    if not user_mood:
        return 0.5  # No mood preference → neutral
    
    if not mood_keywords:
        return 0.0  # Book has no mood keywords
    
    user_words = set(user_mood.lower().split())
    mood_set = set(kw.lower() for kw in mood_keywords)
    
    matches = len(user_words & mood_set)
    return matches / len(user_words) if user_words else 0.0


def calculate_age_safety(user_age: str, book: Book) -> float:
    """Calculate age appropriateness score"""
    if is_age_in_range(user_age, book.min_age, book.max_age):
        return 1.0
    else:
        return 0.3  # Out of range but not blocked


def calculate_avoid_penalty(description: str, avoid_list: List[str]) -> bool:
    """Check if book contains avoided keywords (0 = exclude, no penalty applied)"""
    description_lower = description.lower()
    for avoid_keyword in avoid_list:
        if avoid_keyword.lower() in description_lower:
            return True  # Should be excluded
    return False


def score_candidate(
    book: Book,
    preferences: Preference,
    exclude_books: List[str]
) -> Tuple[float, Dict]:
    """
    Score a single book candidate
    Returns (score, reason_dict)
    """
    reason = {
        'genre_match': 0.0,
        'mood_match': 0.0,
        'age_safety': 0.0,
        'delivered_penalty': 0.0,
        'avoided': False
    }
    
    # Hard exclude: if book is in exclude list, return 0.0
    if book.book_id in exclude_books:
        reason['avoided'] = True
        return 0.0, reason
    
    # Check avoid list (hard exclude)
    if calculate_avoid_penalty(book.description, preferences.avoid):
        reason['avoided'] = True
        return 0.0, reason
    
    # Genre matching
    genre_match = calculate_genre_match(preferences.genres, book.genres)
    reason['genre_match'] = genre_match
    
    # Mood matching
    mood_match = calculate_mood_match(preferences.mood, book.mood_keywords)
    reason['mood_match'] = mood_match
    
    # Age safety
    age_safety = calculate_age_safety(preferences.recipient_age_range, book)
    reason['age_safety'] = age_safety
    
    # Calculate weighted score (no penalty needed since we hard-exclude above)
    total_score = (
        (genre_match * GENRE_WEIGHT) +
        (mood_match * MOOD_WEIGHT) +
        (age_safety * AGE_WEIGHT)
    )
    
    # Clamp to 0.0-1.0
    total_score = max(0.0, min(1.0, total_score))
    
    return total_score, reason


def rank_candidates(
    books: List[Book],
    preferences: Preference,
    exclude_books: List[str] = None
) -> List[Tuple[Book, float, Dict]]:
    """
    Rank all books by score
    Returns list of (book, score, reason) tuples sorted by score descending
    """
    if exclude_books is None:
        exclude_books = []
    
    candidates = []
    for book in books:
        score, reason = score_candidate(book, preferences, exclude_books)
        candidates.append((book, score, reason))
    
    # Sort by score descending
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    return candidates


def calculate_confidence(top_score: float, runner_up_score: float) -> float:
    """
    Calculate confidence based on score gap
    Larger gap = higher confidence
    """
    score_gap = top_score - runner_up_score
    
    # Confidence formula: base score + gap bonus
    # If top is 0.8 and runner-up is 0.7 (gap 0.1), confidence ~0.88
    confidence = min(1.0, top_score + (score_gap * 0.5))
    
    return confidence


def select_best_fit(
    books: List[Book],
    preferences: Preference,
    exclude_books: List[str] = None,
    allow_out_of_range: bool = False
) -> Optional[Dict]:
    """
    Select the best-fit book with full metadata
    Returns dict with book data and reasoning, or None if no suitable books
    """
    if exclude_books is None:
        exclude_books = []
    
    # Rank all candidates
    candidates = rank_candidates(books, preferences, exclude_books)
    
    # Filter for age-appropriate or use top candidate anyway
    suitable_candidates = candidates
    
    if not suitable_candidates:
        return None
    
    # Get top candidate
    best_book, best_score, best_reason = suitable_candidates[0]
    
    # Get runner-up for comparison
    runner_up_score = suitable_candidates[1][1] if len(suitable_candidates) > 1 else 0.0
    runner_up_book = suitable_candidates[1][0] if len(suitable_candidates) > 1 else None
    
    # Calculate confidence
    confidence = calculate_confidence(best_score, runner_up_score)
    
    # Build selection reason
    selection_reason = "strong_match"
    if best_reason['genre_match'] > 0.7:
        selection_reason += "_good_genre"
    if best_reason['mood_match'] > 0.6:
        selection_reason += "_good_mood"
    if best_reason['age_safety'] == 1.0:
        selection_reason += "_age_appropriate"
    
    # Get top candidates for alternative options
    top_candidates = [
        {
            'book_id': cand[0].book_id,
            'title': cand[0].title,
            'author': cand[0].author,
            'score': cand[1]
        }
        for cand in suitable_candidates[:3]
    ]
    
    return {
        'book_id': best_book.book_id,
        'title': best_book.title,
        'author': best_book.author,
        'cover_url': best_book.cover_url,
        'price': best_book.price,
        'description': best_book.description,
        'score': round(best_score, 2),
        'confidence': round(confidence, 2),
        'reason': {
            'genre_match': round(best_reason['genre_match'], 2),
            'mood_match': round(best_reason['mood_match'], 2),
            'age_safety': round(best_reason['age_safety'], 2),
            'delivered_penalty': round(best_reason['delivered_penalty'], 2),
            'selected_for': selection_reason,
            'candidates_considered': len(suitable_candidates),
            'runner_up_title': runner_up_book.title if runner_up_book else None,
            'runner_up_score': round(runner_up_score, 2) if runner_up_book else None
        },
        'candidates': top_candidates,
        'parser_version': PARSER_VERSION
    }


def parse_input(
    preferences_dict: Dict,
    exclude_books: List[str] = None,
    session_id: str = None
) -> Optional[Dict]:
    """
    Main entry point for decision engine
    Input: preferences dict, exclude_books list, session_id
    Output: Decision dict with book selection and reasoning
    """
    # Validate preferences
    if not preferences_dict.get('recipient_age_range'):
        return {
            'error': 'recipient_age_range required',
            'confidence': 0.0,
            'parser_version': PARSER_VERSION
        }
    
    # Build preference object
    pref = Preference(
        recipient_type=preferences_dict.get('recipient_type', 'self'),
        recipient_age_range=preferences_dict.get('recipient_age_range'),
        genres=preferences_dict.get('genres', []),
        avoid=preferences_dict.get('avoid', []),
        surprise_level=preferences_dict.get('surprise_level', 'balanced'),
        mood=preferences_dict.get('mood')
    )
    
    # Load catalog
    books = load_book_catalog()
    
    # Select best fit
    decision = select_best_fit(books, pref, exclude_books or [])
    
    if not decision:
        return {
            'error': 'No suitable books found',
            'confidence': 0.0,
            'parser_version': PARSER_VERSION
        }
    
    # Add metadata
    decision['parsed_at'] = datetime.utcnow().isoformat() + 'Z'
    if session_id:
        decision['session_id'] = session_id
    
    return decision
