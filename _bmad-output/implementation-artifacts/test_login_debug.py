import requests
import json
from datetime import datetime

BASE_URL = 'http://127.0.0.1:5000'
TEST_PASSWORD = 'SecurePassword123'
TEST_EMAIL = f'test-{datetime.now().timestamp()}@test.com'

# Step 1: Register
print("=== Step 1: Register ===")
reg_response = requests.post(
    f'{BASE_URL}/api/users/register',
    json={
        'name': 'Test User',
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD
    }
)
print(f"Status: {reg_response.status_code}")
print(f"Response: {json.dumps(reg_response.json(), indent=2)}")

if reg_response.status_code == 201:
    user_id = reg_response.json()['user_id']
    
    # Step 2: Login
    print("\n=== Step 2: Login ===")
    login_response = requests.post(
        f'{BASE_URL}/api/users/login',
        json={
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD
        }
    )
    print(f"Status: {login_response.status_code}")
    print(f"Response: {json.dumps(login_response.json(), indent=2)}")
