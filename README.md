# DSA King System — No NPM edition

## Windows: one-click startup

Double-click **START_DSA KING.bat**. Python 3 is required. The first launch installs Flask, python-dotenv and requests automatically if missing. It starts the website at **http://127.0.0.1:5000** and opens your browser. No Node.js, `npm install`, or `npm run dev` is required. Subsequent launches reuse installed packages. Keep the command window open.

Alternative: `python app.py` (after `pip install -r requirements.txt`).

## Groq API setup

Copy `.env.example` to `.env` and set `GROQ_API_KEY=your_key`. Never place the key in HTML or JS. The Flask backend calls Groq server-side. Without a key the mentor uses clearly labeled offline guidance. The name **Grok** usually refers to xAI's model, while **Groq** is a different inference API. This package implements **Groq**; no API key is included.

## Scope and limitations

Static HTML/CSS/JavaScript frontend and Python Flask backend. The original WebP frames and portrait assets are included, and all 22 feature names appear in organized sections. Functional local prototypes include Python judge (4 curated problems), XP, mistake history, recommendations, AI mentor (Groq when configured), visual sorting, flowchart example, complexity chart, interview practice, portfolio export, dungeons, and solo contest practice. Real-time PvP, actual voice interview, arbitrary-code visualization, authenticated global leaderboards and production-grade judge isolation are **not implemented**. The code runner executes user Python locally: use only with trusted code on your own computer, never deploy this judge to a public server.

The site is not completely installation-free: Python 3 and initial Python dependencies are needed, but the launcher handles the dependencies automatically. For Groq assistance an internet connection and API key are required.


## Full-screen thunder update
- AWAKEN and SHADOW MONARCH use edge-to-edge scroll animations; ARISE now uses full-viewport cover imagery.
- AWAKEN has a fullscreen animated lightning overlay and synthesized thunder rumble.
- Browsers block autoplay audio: click **THUNDER SOUND OFF** to enable thunder sound. Visual thunder works without audio permission.
- Reduce Motion system preference disables the flashing lightning animation.
- No npm required; double-click START_DSA KING.bat (Python required).


## 2026-10-29 UI fixes
- Site renamed DSA King System throughout primary UI.
- Top navigation is no longer fixed while scrolling.
- AWAKEN and SHADOW MONARCH titles reduced and moved toward the lower corners, to avoid obscuring character faces and prevent text overflow.
- ARISE cursor reveal throttled to one update per animation frame; CSS clip transition disabled.
- Thunder toggle removed; thunder gain increased.
- **Audio autoplay limitation:** Chrome/Edge commonly block audio on initial page load. The site attempts to start audio immediately, and unlocks it automatically upon the visitor's first scroll, click, touch, or keypress. Sound before interaction cannot be guaranteed without browser-specific permissions.
- `.env` is included, with an empty `GROQ_API_KEY` field. Add your own key; never share it or commit it.
- No npm: run `START_ZIA.bat` on Windows (Python required).

## Global thunder and ARISE cursor audio
- Lightning and thunder now operate across the entire website, including the platform section.
- Moving the mouse within the ARISE section plays a gentle, throttled synth chime distinct from thunder.
- Browser audio autoplay restrictions still apply: the first user interaction may be needed to unlock audio.
- The lightning overlay is noninteractive and does not block buttons or links.


## Original Solo Leveling animation fidelity update
- ARISE uses a full-canvas portrait reveal with eased pointer tracking, a feathered 16-frame trailing lens, and cyan aura, adapted from the uploaded RevealStage.jsx without requiring React/npm.
- AWAKEN uses a canvas falling-glyph effect adapted from the uploaded GlyphRain.jsx, masked to keep the face readable.
- The original DSA King System functionality and Flask backend remain in place.


## Voice, languages, and visual theme
- AI mentor chat has a microphone button using browser SpeechRecognition (Chrome/Edge recommended); dictated words appear in the input. Press Enter or ➤ to send. Permission and browser support are required.
- Language picker includes 16 languages: Python, JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, Scala, Dart, R. The bundled judge **only executes Python**. Other languages provide editable templates and show an explicit unavailable message. A compatible remote judge and language-specific test harness are required for actual execution.
- The coding dashboard uses navy/blue/black to match the animated landing pages.
- No npm. Launch with START_ZIA.bat.

## New Login / Signup screen
- The website now opens to a responsive, two-panel animated authentication screen modeled on the provided recording.
- Login and signup switch inside the same screen; includes email, password, password visibility, terms checkbox, and error feedback.
- User accounts are stored locally in `users.sqlite3` with hashed passwords. Flask session cookies keep users signed in across page reloads.
- A logout control appears in the application header after login.
- This is a local prototype. Before public deployment, add HTTPS, CSRF protection, login rate limiting, password recovery, email verification, and production database configuration.
- Google sign-in is not included because it requires your Google OAuth client credentials and redirect setup.
- To reset local test accounts, stop the server and delete `users.sqlite3`.
- No NPM required. Run `START_ZIA.bat` (existing launcher).

## Sliding login update
- The dark welcome panel slides from left to right on Sign Up, and back on Login, as in the supplied reference video.
- Mobile users see a compact stacked version with fade transitions.
- Thunder lightning and audio are suppressed while the authentication overlay is visible.
- After successful login, the page attempts to enable thunder audio (subject to browser autoplay policy).


## Cosmic Orb login integration
The approved dark navy-blue Cosmic Orb sliding Login / Sign Up page is now at `static/login.html`. It is displayed on first visit as a full-screen login gate, and its forms use the existing Flask `/api/auth/login` and `/api/auth/register` endpoints. Google sign-in redirects to the existing `/auth/google` endpoint (requires OAuth credentials in `.env`). After authentication, the existing Solo Leveling website appears and thunder audio can activate, subject to browser autoplay restrictions. No NPM needed.
