import json
from app import app

samples = [
    "I am looking for a gift for my friend who is 40 years old and likes horror books",
    "I want a gift for my son who is 8 and loves dinosaurs",
    "Surprise me — full surprise, no politics please"
]

with app.test_client() as c:
    for s in samples:
        rv = c.post('/api/parse', json={'text': s})
        print('INPUT:', s)
        print('RESPONSE:', json.dumps(rv.get_json(), indent=2))
        print()
