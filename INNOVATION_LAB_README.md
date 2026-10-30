# DSA King System — Six Innovation Lab Modules

Open `START_ZIA.bat`, register/login, and select **Innovation Lab** in the sidebar. No NPM needed.

1. **AI Thought Mirror**: deterministic AST + explanation coaching, with questions. It does not read hidden thoughts or use a trained student model.
2. **Code Time Machine**: runs a Python `solve(...)` function with JSON arguments and records up to 120 executed source lines and local variable representations. This is a forward-recorded replay, not true reverse execution.
3. **Algorithm Debate Arena**: evidence-conscious two-perspective debate based on observed syntax. It does not claim to infer precise complexity or use two independently hosted LLMs.
4. **Real-World DSA Simulator**: reproducible weighted graph generation, Dijkstra shortest path, cost and graph-edge display. Data is simulated, not real traffic.
5. **DSA Knowledge Galaxy**: topic/prerequisite cards and mastery derived from four existing demo problem IDs; not a full 3D engine.
6. **AI Solution Verifier**: independent seeded generated tests for four curated Python problems, showing concrete failing inputs when found. Not a proof of correctness. Tests are limited and the Two Sum verifier accepts any valid distinct-index pair.

## Critical safety and accuracy notes
- This is a functional local hackathon prototype, **not production-ready**. Python execution in Code Time Machine, Solution Verifier, and the original Judge is only subprocess-isolated; do not expose it to arbitrary public users. For a public hackathon deployment use OS-level containers with no network, resource limits, filesystem restrictions, and a vetted judge service.
- Login and Google OAuth are inherited from the existing website. Google sign-in requires user-owned OAuth credentials.
- No hardcoded API keys or existing Flask session secret are included in this ZIP. Fill in `.env` using `.env.example` if you need Groq or Google integration.
- Existing features, original Cosmic Orb login, and footer are preserved.
