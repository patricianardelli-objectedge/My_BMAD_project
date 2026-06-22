NLU test harness for Blind Date Book Experience

Files:
- `nlu_rules.json` : Keyword lists and simple patterns used by the parser.
- `parser.py` : Lightweight rule-based parser that extracts recipient, age_range, genres, avoid, and surprise_level from short natural-language inputs.
- `test_parser.py` : Simple runner that prints parsed outputs for sample sentences.

Run the test harness:

```bash
python c:\Patricia\BMAD_project\_bmad-output\implementation-artifacts\nlu\test_parser.py
```

Notes:
- This is a lightweight, rule-based prototype intended for pilot testing. For production, consider replacing or augmenting with a small NLU service or library.
