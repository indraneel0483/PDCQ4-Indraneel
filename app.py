from flask import Flask, redirect, url_for, session, render_template, request, jsonify
from authlib.integrations.flask_client import OAuth
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv

load_dotenv()


def get_required_env(var_name: str) -> str:
    """Fetch a required environment variable and fail fast if missing."""
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {var_name}. "
            "Create a .env file or export it before starting the app."
        )
    return value.strip()


SECRET_KEY = get_required_env('SECRET_KEY')
GOOGLE_CLIENT_ID = get_required_env('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = get_required_env('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Google OAuth setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
    redirect_uri=GOOGLE_REDIRECT_URI
)

# Get Indian Standard Time
def get_indian_time():
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    return current_time.strftime('%A, %d %B %Y, %I:%M:%S %p IST')

# Generate character-based diamond pattern
def generate_pattern(n):
    if n <= 0:
        return []

    pattern_source = "FORMULAQSOLUTIONS"
    source_length = len(pattern_source)
    mid = (n + 1) // 2
    lines = []
    line_number = 1

    def build_line(i, current_line_number):
        prefix_spaces = " " * (mid - i)
        k = current_line_number - 1
        total_chars = i * 2
        chars = []

        for j in range(1, total_chars):
            current_char = pattern_source[k % source_length]
            if i % 2 == 1:
                chars.append(current_char)
            else:
                if j == 1 or j == total_chars - 1:
                    chars.append(current_char)
                else:
                    chars.append("-")
            k += 1

        return prefix_spaces + "".join(chars)

    for i in range(1, mid + 1):
        lines.append(build_line(i, line_number))
        line_number += 1

    for i in range(mid - 1, 0, -1):
        lines.append(build_line(i, line_number))
        line_number += 12  # mirrors the provided reference logic

    return lines

# Home page
@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# Start Google login
@app.route('/login')
def login():
    redirect_uri = GOOGLE_REDIRECT_URI or url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

# Google OAuth callback
@app.route('/callback')
def authorize():
    try:
        token = google.authorize_access_token()
        resp = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
        user_info = resp.json()
        session['user'] = {
            'name': user_info.get('name'),
            'email': user_info.get('email'),
            'picture': user_info.get('picture')
        }
        return redirect(url_for('dashboard'))
    except Exception:
        # Log exception to console for easier debugging
        import traceback
        traceback.print_exc()
        return redirect(url_for('index'))

# Dashboard after login
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', user=session['user'], indian_time=get_indian_time())

# Pattern generator API
@app.route('/generate-pattern', methods=['POST'])
def generate_pattern_route():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        num_lines = int(request.get_json().get('lines', 0))
        if not (1 <= num_lines <= 100):
            return jsonify({'error': 'Number of lines must be between 1 and 100'}), 400
        return jsonify({'pattern': generate_pattern(num_lines)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
