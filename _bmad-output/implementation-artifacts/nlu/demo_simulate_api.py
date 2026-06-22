import json
from parser import parse_input

samples = [
    "I am looking for a gift for my friend who is 40 years old and likes horror books",
    "I want a gift for my son who is 8 and loves dinosaurs",
    "Surprise me — full surprise, no politics please"
]

for s in samples:
    parsed = parse_input(s)
    print(json.dumps({'input': s, 'parsed': parsed}, indent=2))
    print()
