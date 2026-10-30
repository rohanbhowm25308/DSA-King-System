# Multi-language execution and expandable practice bank

## Status (read before demo)
- Python uses the existing development-only subprocess runner. DO NOT expose it to public internet users; it is not a hardened sandbox.
- 15 additional languages are routed through an external Judge0-compatible sandbox: JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, Scala, Dart, R. The service is NOT bundled. Execution only works after configuring a compatible Judge0 instance in `.env` (`JUDGE0_URL`, optionally `JUDGE0_API_KEY`). No language is claimed to be tested on a live Judge0 server.
- Language IDs depend on your Judge0 version; verify via your provider's `/languages` endpoint and update `LANGUAGE_IDS` in `app.py` if needed.
- Remote execution contract: your full program reads **one JSON array of arguments from stdin** and prints **one JSON value** to stdout. E.g. for Two Sum, stdin `[ [2,7,11,15], 9 ]`, stdout `[0,1]`. The existing editor templates for non-Python languages are illustrative and need a full program/main entry point and JSON parsing. They are NOT automatically wrapped as `solve` functions.
- Judge0 `wait=true` must be enabled; provider must permit per-submission CPU/memory limits. Errors and unavailable service are reported clearly. The backend compares JSON outputs strictly. Test cases stop at first failure.
- The **Load 40 More Challenges** button adds parameterized instances of the four original algorithm families. Up to 100,000 reproducible variants are addressable. These are NOT 100,000 independently curated DSA problems, and they are NOT infinite distinct algorithms. They are intended as scalable practice until a validated diverse question bank is added.
- Question IDs are reproducible and the server generates tests from seeded random inputs. The original four questions remain unchanged.

## Deploy safely
Use an isolated execution service with no network access from submitted code, resource quotas, authentication, rate limiting, and per-user quotas. Never deploy the local Python runner to untrusted public traffic. Set your `.env` credentials locally and never commit them. Verify Judge0 language IDs and perform real cross-language tests before a hackathon demo.
