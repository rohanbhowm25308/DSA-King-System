# DSA King System — Mock Interview & Innovation Lab Upgrade

## Updated
- Replaced the one-question, four-keyword mock interview with a dynamic question bank and topic/difficulty variations.
- AI evaluation now uses the server-side Groq API, returning a score out of 10, strengths, improvements, a model answer, and a follow-up question.
- Interview replay records AI feedback locally in the browser (up to 100 records); this is not cross-device or durable database persistence.
- Improved Innovation Lab Knowledge Galaxy to reflect curated topic completion instead of only four demo IDs.
- Added Gunicorn to requirements.txt for Render deployment.
- Disabled unsafe local Python execution in the Innovation Lab timeline/verifier on public servers unless explicitly enabled. Do not enable unsafe execution on Render.
- Disabled the main local Python judge on Render by default for public safety. Configure a properly sandboxed remote judge before allowing public code execution.

## Installation
1. Extract this ZIP into a fresh directory.
2. Copy your existing private `.env` into the extracted project directory. Do not upload secrets to GitHub.
3. Back up your `users.sqlite3` database if using local accounts; on Render, use persistent database storage.
4. In Render, set GROQ_API_KEY and optionally GROQ_MODEL=openai/gpt-oss-20b.
5. Push changed files to GitHub and redeploy Render.

## Verified
- Python files compile; JavaScript files pass node syntax checks.
- Six Innovation Lab Python handlers returned structured outputs for representative test inputs.
- The archive passes ZIP integrity validation.

## Not verified / limitations
- Full browser end-to-end testing was not possible in this environment.
- Live Groq API evaluation could not be tested without your API credentials and internet access.
- Existing Code Arena, Company Prep, Engineering and other sections include demo/illustrative features; they have not been transformed into production-grade services.
- Public execution of arbitrary user code requires strong isolation, resource limits, and network controls. Python execution is disabled on Render by default for safety.
- SQLite and localStorage are not a substitute for a persistent, account-scoped production data store.
- Question variations are numerous but are not guaranteed globally unique.
