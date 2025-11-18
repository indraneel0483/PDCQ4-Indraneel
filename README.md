# FormulaQ Solutions Coding Assessment

Flask web application that authenticates users with Google OAuth 2.0, shows the current Indian Standard Time, and exposes an API that returns a custom diamond pattern built from `FORMULAQSOLUTIONS`.

---

## Stack Overview

- **Flask 3** – lightweight Python web framework serving HTML templates and JSON endpoints.
- **Authlib** – handles the Google OAuth/OpenID Connect flow and token exchange.
- **googleapis** – provides user profile info (`/userinfo`) once authenticated.
- **python-dotenv** – loads environment variables from `.env`.
- **pytz** – generates localized IST timestamps.

---

## Prerequisites

- Python 3.12 (matches the provided `venv`, but any 3.10+ version should work)
- Git
- Google Cloud project with OAuth consent screen configured

---

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/indraneel0483/PDCQ4-Indraneel.git
   cd PDCQ4-Indraneel
   ```

2. **Create and activate a virtual environment (optional if you use the bundled `venv`)**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate       # Windows PowerShell
   # source .venv/bin/activate    # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Google OAuth credentials**
   - In Google Cloud Console → APIs & Services → Credentials → “Create Credentials” → “OAuth client ID”.
   - Choose “Web application”.
   - Authorized JavaScript origins: `http://localhost:5000`
   - Authorized redirect URIs: `http://localhost:5000/callback`
   - Download the client secrets (or copy values) for the next step.

5. **Set environment variables**
   - Copy `.env.example` to `.env`.
   - Fill in the real values:
     ```
     SECRET_KEY=generate-a-long-random-string
     GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
     GOOGLE_CLIENT_SECRET=your-client-secret
     GOOGLE_REDIRECT_URI=http://localhost:5000/callback
     ```

---

## Running the Application

```bash
python app.py
```

Flask starts on `http://127.0.0.1:5000` (configured to bind on all interfaces for container/cloud use). Visit the URL in a browser:

1. Click **Login with Google**.
2. Complete the OAuth prompt; once redirected back, the dashboard shows:
   - Your Google profile name/email/photo.
   - Current IST time (auto-updated on page load).
   - A form to request the diamond pattern.

---

## Pattern Generator API

- Endpoint: `POST /generate-pattern`
- Body: `{"lines": <odd positive integer up to 100>}`
- Returns JSON: `{"pattern": [" ... ", "..."]}`

The backend uses the `generate_pattern` function (see `app.py`) to create the character diamond. Odd rows print consecutive characters from `FORMULAQSOLUTIONS`; even rows outline the row with characters and fill the interior with `-`.

---

## How It Works

1. **OAuth Flow**
   - `/login` builds the redirect using Authlib.
   - `/callback` exchanges the authorization code for tokens, then calls Google’s UserInfo endpoint.
   - User details are stored in the Flask session (cookie signed with `SECRET_KEY`).

2. **Dashboard Rendering**
   - `dashboard.html` receives `user` and `indian_time`.
   - JavaScript (if any) can call `/generate-pattern` via fetch/AJAX.

3. **Pattern API**
   - Validates that the user is authenticated.
   - Coerces `lines` to `int` and ensures it sits between 1 and 100.
   - Generates the pattern and returns it as JSON.

---

## Deployment Notes

- Set all environment variables through your hosting provider; never commit the real `.env`.
- Disable `debug=True` in production.
- Consider HTTPS everywhere for OAuth redirects (required by Google outside localhost).

---

## Common Issues

| Symptom | Fix |
| --- | --- |
| `invalid_client` from Google | Ensure `GOOGLE_CLIENT_ID/SECRET` match the Google Cloud project and redirect URI matches exactly. |
| Runtime error “Missing required environment variable …” | Confirm `.env` exists and `python-dotenv` can load it (file is in same directory as `app.py`). |
| 401 when calling `/generate-pattern` | You must authenticate first; the session stores `user`. |

---

## Running Tests

No automated tests are defined. You can manually verify:

1. `python app.py`
2. Use browser + Developer Tools (Network tab) to inspect `/generate-pattern`.
3. Optionally write unit tests for `generate_pattern` using `pytest`.