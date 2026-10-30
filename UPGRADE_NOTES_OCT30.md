# DSA King System: AI Lab / Innovation / Catalog update

- Innovation Lab: added language selector (Python, C, C++, Java, JavaScript, Rust, Ruby, Go, C#, TypeScript, Kotlin, Swift, PHP). Non-Python code is sent to the existing Groq-powered mentor for **advisory analysis only**. It is **not compiled or executed**. Without Groq, offline generic guidance is returned. Python-only timeline/verifier execution is unchanged and disabled on public Render unless a safe execution service is configured.
- AI Lab: Bug Detective, Counterexample Generator, and Coding Mentor open code input panels and use the existing mentor endpoint. These are AI suggestions, not verified bug detection or guaranteed counterexamples.
- Company Prep: 24 illustrative company tracks; not verified interview question banks.
- Engineering: 20 independent engineering design briefs; not completed implementations.
- Existing interview grading and all other modules preserved.
- Verified JS syntax and archive integrity. No full browser, authenticated Groq, or production execution tests were performed.
- Before updating Render, back up your `.env` and user database; do not commit either to GitHub. Public code execution needs proper isolation.
