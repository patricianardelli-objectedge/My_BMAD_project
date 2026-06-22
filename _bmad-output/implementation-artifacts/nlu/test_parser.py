from parser import parse_input

# Example cases and expected rough outputs for manual verification
cases = [
    ("I am looking for a gift for my friend who is 40 years old and likes horror books", 'gift friend 40 horror'),
    ("I want a gift for my son who is 8 and loves dinosaurs", 'gift son 8 dinosaurs'),
    ("Surprise me — full surprise, no politics please", 'full surprise avoid politics'),
]

for text, _ in cases:
    result = parse_input(text)
    print('INPUT:', text)
    print('OUTPUT:', result)
    print()
