# AI Lab language validation and empty-response fix

- AI Bug Detective, AI Counterexample Generator and AI Coding Mentor now check for recognizable mismatches between the selected language and the pasted source code before calling Groq.
- The optional context box is optional; code is required.
- Empty Groq replies trigger a retry using `GROQ_TEXT_MODEL` (default `llama-3.3-70b-versatile`) with a larger completion allowance. Your Groq account must have access to the configured model.
- Supported selections: Python, C, C++, Java, JavaScript, TypeScript, Rust, Ruby, Go, C#, Kotlin, Swift, PHP.
- **Important limitation:** heuristic language detection cannot prove that arbitrary code is valid, and ambiguous snippets may not be identifiable. AI analysis does not compile or execute code. For true per-language compilation/execution, connect a secure Judge0 service with appropriate language IDs and resource limits. Never execute arbitrary user code directly in the Flask server process.
- Never commit `.env` or API keys to GitHub. Keep your existing `.env` and user database separately.
