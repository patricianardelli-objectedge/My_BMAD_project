Blind Date Book — Plain HTML/CSS component library

What’s here:
- `styles.css` — CSS tokens and component styles based on DESIGN.md
- `index.html` — Simple demo page showing hero, story cards, agent modal, and mini cart

How to run:
1. Open `index.html` in a browser. Note: some YouTube Shorts disallow embedding and can trigger a "player configuration" error; in that case the demo displays a clickable thumbnail that opens the video on YouTube.

Notes:
- This is a static prototype for rapid frontend handoff.
- Agent modal now uses the local NLU demo at `http://127.0.0.1:5000/api/parse`.

How to run locally:
1. Start the NLU demo server:
   ```powershell
   cd _bmad-output\implementation-artifacts\nlu
   .\.venv\Scripts\activate
   python app.py
   ```
2. Open `design-artifacts/E-Development/ux-blind-date-book-2026-06-22/frontend/index.html` in a browser.
3. Enter a natural preference phrase in the agent modal and submit.

Integration example (fetch):

```javascript
// inside submitAgent()
const resp = await fetch('http://127.0.0.1:5000/api/parse', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text })
});
const data = await resp.json();
```

Accessibility & next steps:
- Add ARIA roles and test with screen readers.
- Implement keyboard trap for the modal.
- Implement server-side subscription handling and delivered_books tracking.

