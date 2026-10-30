# Interview and feature-navigation fix

- AI interview reports now show INCORRECT ANSWER (0–2), PARTIALLY CORRECT (3–5), GOOD ATTEMPT (6–7), or STRONG ANSWER (8–10).
- Very short, non-explanatory responses receive zero without calling Groq. Short superficial answers cannot exceed 2/10.
- Skip/Next Question uses a blue-purple styled button.
- AI Lab, Company Prep, Engineering, and Arena placeholder buttons now show their actual module scope or limitations instead of silently redirecting to Problems. Some are still demonstrations and not complete AI services.
- The backend still needs GROQ_API_KEY and a working GROQ_MODEL for meaningful AI assessment.
- Testing: static syntax, archive validation. Live Groq and browser integration not tested.
- Never publish .env or local databases. Public code execution requires secure isolation.
