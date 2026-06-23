"""
User Service for Blind Date Book
Handles user registration, authentication, preferences, and avoid-list management
"""

import jwt
import bcrypt
import uuid
import os
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, List

USER_VERSION = "1.0"
JWT_EXPIRY_DAYS = 30


@dataclass
class User:
    """User data model"""
    user_id: str
    email: str
    name: Optional[str]
    created_at: str


@dataclass
class UserPreferences:
    """User preferences data model"""
    user_id: str
    preferred_genres: List[str]
    mood_keywords: List[str]
    age_min: int
    age_max: int
    surprise_level: str
    recipient_type: str


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def generate_jwt_token(user_id: str, email: str) -> str:
    """Generate JWT token for user session"""
    secret = os.environ.get('JWT_SECRET', 'dev-secret-key-change-in-production')
    
    payload = {
        'sub': user_id,
        'email': email,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=JWT_EXPIRY_DAYS)
    }
    
    return jwt.encode(payload, secret, algorithm='HS256')


def verify_jwt_token(token: str) -> Tuple[Optional[str], Optional[str]]:
    """Verify JWT token and return user_id, email"""
    try:
        secret = os.environ.get('JWT_SECRET', 'dev-secret-key-change-in-production')
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload.get('sub'), payload.get('email')
    except jwt.ExpiredSignatureError:
        return None, None
    except jwt.InvalidTokenError:
        return None, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validate email format"""
    if not email or '@' not in email or '.' not in email.split('@')[-1]:
        return False, "Invalid email format"
    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """Validate password strength"""
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters"
    return True, None


def validate_preferences(prefs: dict) -> Tuple[bool, Optional[str]]:
    """Validate preferences object"""
    required_fields = ['preferred_genres', 'mood_keywords', 'age_min', 'age_max', 'surprise_level', 'recipient_type']
    
    for field in required_fields:
        if field not in prefs:
            return False, f"Missing required field: {field}"
    
    # Validate genres - must not be empty
    genres = prefs.get('preferred_genres', [])
    if not genres or len(genres) == 0:
        return False, "At least one genre must be selected"
    
    # Validate mood keywords - must not be empty
    moods = prefs.get('mood_keywords', [])
    if not moods or len(moods) == 0:
        return False, "At least one mood keyword must be selected"
    
    # Validate age range
    age_min = prefs.get('age_min', 0)
    age_max = prefs.get('age_max', 0)
    if not isinstance(age_min, int) or not isinstance(age_max, int):
        return False, "Age range must be integers"
    
    if age_min < 0 or age_max > 120 or age_min > age_max:
        return False, "Invalid age range"
    
    # Validate surprise level
    if prefs.get('surprise_level') not in ['minimal', 'balanced', 'maximum']:
        return False, "Invalid surprise level"
    
    # Validate recipient type
    if prefs.get('recipient_type') not in ['self', 'gift']:
        return False, "Invalid recipient type"
    
    return True, None


def parse_register_request(request_data: dict) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Validate and parse user registration request
    Returns (user_dict, error_message)
    """
    email = request_data.get('email', '').strip()
    password = request_data.get('password', '')
    name = request_data.get('name', 'Guest').strip()
    
    # Validate email
    valid, error = validate_email(email)
    if not valid:
        return None, error
    
    # Validate password
    valid, error = validate_password(password)
    if not valid:
        return None, error
    
    if not name:
        name = 'Guest'
    
    # Hash password
    password_hash = hash_password(password)
    
    user = {
        'user_id': str(uuid.uuid4()),
        'email': email,
        'password_hash': password_hash,
        'name': name,
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'updated_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    return user, None


def parse_login_request(request_data: dict, user_record: Optional[Dict]) -> Tuple[Optional[str], Optional[str]]:
    """
    Validate login request and return jwt_token
    Returns (jwt_token, error_message)
    """
    email = request_data.get('email', '').strip()
    password = request_data.get('password', '')
    
    if not user_record:
        return None, "Invalid email or password"
    
    # Verify password
    if not verify_password(password, user_record.get('password_hash', '')):
        return None, "Invalid email or password"
    
    # Generate token
    token = generate_jwt_token(user_record['user_id'], email)
    return token, None


def parse_preferences_request(request_data: dict) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Validate and parse user preferences
    Returns (preferences_dict, error_message)
    """
    # Validate preferences
    valid, error = validate_preferences(request_data)
    if not valid:
        return None, error
    
    prefs = {
        'preference_id': str(uuid.uuid4()),
        'preferred_genres': request_data.get('preferred_genres', []),
        'mood_keywords': request_data.get('mood_keywords', []),
        'age_min': request_data.get('age_min', 0),
        'age_max': request_data.get('age_max', 120),
        'surprise_level': request_data.get('surprise_level', 'balanced'),
        'recipient_type': request_data.get('recipient_type', 'self'),
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'updated_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    return prefs, None


def parse_avoid_list_request(request_data: dict) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Validate and parse avoid-list entry
    Returns (avoid_entry_dict, error_message)
    """
    book_id = request_data.get('book_id', '').strip()
    reason = request_data.get('reason', 'dislike')
    
    if not book_id:
        return None, "book_id required"
    
    if reason not in ['read', 'dislike', 'already-gifted']:
        return None, "Invalid reason. Must be: read, dislike, or already-gifted"
    
    entry = {
        'avoid_id': str(uuid.uuid4()),
        'book_id': book_id,
        'reason': reason,
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    return entry, None
