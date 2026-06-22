OpenAPI TypeScript client (lightweight)

Files:
- `openapi-client.ts` — a small hand-written TypeScript client for the pilot APIs.

How to use (quick):
1. Install TypeScript locally: `npm install -D typescript`
2. Compile: `npx tsc openapi-client.ts --target ES2017 --module commonjs --outDir ./dist`
3. Import the compiled JS into the frontend build or copy `dist/openapi-client.js` into `public/` and include with a script tag.

Example usage in a bundler-based app:
```ts
import { ApiClient } from './openapi-client'
const api = new ApiClient('https://api.local');
api.parseAgent('gift for my son, 8, loves dinosaurs').then(console.log)
```

For the static HTML prototype, see `api-example.js` for example calls using `fetch`.
