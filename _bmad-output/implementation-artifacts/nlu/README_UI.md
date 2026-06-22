Demo UI for the conversational NLU parser

To run locally:

1. Install dependencies (use a virtualenv if you like):

```bash
pip install -r c:\Patricia\BMAD_project\_bmad-output\implementation-artifacts\nlu\requirements.txt
```

2a. To run a quick test (no server):

```bash
python c:\Patricia\BMAD_project\_bmad-output\implementation-artifacts\nlu\test_client.py
```

2b. To run the demo server and open the UI:

```bash
python c:\Patricia\BMAD_project\_bmad-output\implementation-artifacts\nlu\app.py
# then open http://127.0.0.1:5000/ in your browser
```

Notes:
- This is a minimal demo for pilot testing. For production, secure the API and host the app behind a proper web server.
