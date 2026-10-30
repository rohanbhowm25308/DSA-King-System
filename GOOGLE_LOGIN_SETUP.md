# Google Sign-in setup (DSA King System)

1. Visit https://console.cloud.google.com/apis/credentials and create a Google Cloud project.
2. Configure Google Auth Platform / OAuth consent screen (external or internal as appropriate). Add your own Google account as a test user if the app is in testing mode.
3. Create an OAuth 2.0 Client ID of type **Web application**.
4. Authorized redirect URI: `http://127.0.0.1:5000/auth/google/callback` (exact match). If you use `localhost` instead, configure that as a separate URI.
5. Copy Client ID and Client Secret into the project `.env` as `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
6. Run `START_ZIA.bat`. The launcher installs Python dependencies if necessary. Click **Continue with Google**.

The Google button is present even before configuration; without credentials it explains that setup is required. Do not share `.env` or credentials publicly. Google sign-in is OAuth, not a simulation. Existing email/password accounts are not automatically linked by matching email, for security. Public deployment requires HTTPS, a production secret key, secure cookies, CSRF protections, rate limiting, and account-linking flow.
