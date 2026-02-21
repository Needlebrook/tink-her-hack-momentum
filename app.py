import sqlite3
import random
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, session, jsonify, g

app = Flask(__name__)
app.secret_key = 'momentum-womens-hackathon-2025'  # Change in production

# ------------------------------------------------------------------------------
# DATABASE HELPERS
# ------------------------------------------------------------------------------

DATABASE = 'momentum.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # This gives us dictionary-like rows
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = get_db()
    cur = conn.execute(query, args)
    conn.commit()
    return cur.lastrowid

# ------------------------------------------------------------------------------
# USER SESSION HELPERS
# ------------------------------------------------------------------------------

def get_current_user():
    """Get current user from session"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)

def generate_session_id():
    """Generate unique session ID for a group of responses"""
    return str(uuid.uuid4())

# ------------------------------------------------------------------------------
# METRICS CALCULATION ENGINE (Your Differentiator)
# ------------------------------------------------------------------------------

def calculate_burnout(responses):
    """🔥 Burnout Risk Meter (0-100)"""
    sleep = responses.get('sleep_hours', 7)
    work = responses.get('work_hours', 40)
    housework = responses.get('housework_hours', 2)
    
    # Mental load average (0-2 scale) - Using your 3 new mental load questions
    mental_keys = [
        'mental_planning',    # Who handles planning?
        'mental_emotional',   # Who manages emotions?
        'mental_household'    # Who tracks household needs?
    ]
    mental_values = [responses.get(k, 1) for k in mental_keys if k in responses]
    mental_avg = sum(mental_values) / len(mental_values) if mental_values else 1
    
    # Calculate components
    sleep_deficit = max(0, 8 - sleep) * 10      # 0-40
    work_overload = max(0, work - 40) * 2       # 0-40
    housework_load = min(housework * 5, 25)     # 0-25 (new: housework contributes to burnout)
    mental_component = mental_avg * 12.5        # 0-25
    
    burnout = (sleep_deficit * 0.3) + (work_overload * 0.25) + (housework_load * 0.2) + (mental_component * 0.25)
    return min(100, round(burnout))


def calculate_balance(responses):
    """⚖️ Work-Life Balance Score (0-100, higher = better)"""
    personal = responses.get('personal_time', 30) / 60  # Convert minutes to hours
    sleep = responses.get('sleep_hours', 7)
    work = responses.get('work_hours', 40) / 8          # Normalize to 0-10 scale
    housework = responses.get('housework_hours', 2)
    childcare = responses.get('childcare_hours', 4)
    
    numerator = personal + sleep
    denominator = work + housework + childcare + 0.1    # Avoid division by zero
    
    balance = (numerator / denominator) * 50
    return min(100, round(balance))


def calculate_mental_load(responses):
    """🧠 Mental Load Distribution (Your % vs Partner %)"""
    mental_keys = [
        'mental_planning',    # Who handles planning?
        'mental_emotional',   # Who manages emotions?
        'mental_household'    # Who tracks household needs?
    ]
    
    mental_sum = sum([responses.get(k, 1) for k in mental_keys if k in responses])
    max_possible = len([k for k in mental_keys if k in responses]) * 2
    
    if max_possible == 0:
        return 50, 50  # Default if no data
    
    your_percent = (mental_sum / max_possible) * 100
    return round(your_percent), round(100 - your_percent)


def calculate_recovery(responses):
    """🌿 Recovery Index"""
    sleep = responses.get('sleep_hours', 7)
    me_time_quality = responses.get('me_time_quality', 2)      # New: 1-4 scale
    weekend_rest = responses.get('weekend_rest', 2)            # New: 1-4 scale
    break_freq = responses.get('break_frequency', 2)           # New: 1-4 scale
    overload = responses.get('overload_streak', 1)
    
    # Combine recovery factors (each 1-4 scale, normalize to 0-10)
    recovery_score = (me_time_quality + weekend_rest + break_freq) / 1.2  # Converts 3-12 to ~2.5-10
    
    recovery_raw = (sleep + recovery_score) / overload
    
    if recovery_raw > 12:
        return "High Recovery"
    elif recovery_raw > 6:
        return "Moderate"
    else:
        return "Depleted"

def calculate_all_metrics(user_id, session_id):
    """Calculate and store all metrics for a user session"""
    # Get all responses for this session
    responses_rows = query_db("""
        SELECT q.question_key, r.answer_value 
        FROM responses r
        JOIN questions q ON r.question_id = q.id
        WHERE r.user_id = ? AND r.session_id = ?
    """, [user_id, session_id])
    
    # Convert to dictionary
    responses = {row['question_key']: row['answer_value'] for row in responses_rows}
    
    # Calculate metrics
    burnout = calculate_burnout(responses)
    balance = calculate_balance(responses)
    mental_you, mental_partner = calculate_mental_load(responses)
    recovery = calculate_recovery(responses)
    
    # Store in metrics table
    execute_db("""
        INSERT INTO metrics 
        (user_id, session_id, burnout_score, balance_score, 
         mental_load_you, mental_load_partner, recovery_index)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [user_id, session_id, burnout, balance, mental_you, mental_partner, recovery])
    
    return {
        'burnout': burnout,
        'balance': balance,
        'mental_you': mental_you,
        'mental_partner': mental_partner,
        'recovery': recovery
    }

def get_latest_metrics(user_id):
    """Get most recent metrics for user"""
    metrics = query_db("""
        SELECT * FROM metrics 
        WHERE user_id = ? 
        ORDER BY calculated_at DESC LIMIT 1
    """, [user_id], one=True)
    
    if not metrics:
        return {
            'burnout_score': 50,
            'balance_score': 50,
            'mental_load_you': 50,
            'mental_load_partner': 50,
            'recovery_index': 'Moderate'
        }
    return metrics

# ------------------------------------------------------------------------------
# QUESTIONNAIRE LOGIC
# ------------------------------------------------------------------------------

def get_next_questions(user_id, count=5):
    """Get next set of questions for user (70% new, 30% repeats)"""
    
    # Get questions already answered by this user in ANY session
    answered = query_db("""
        SELECT DISTINCT q.id, q.question_key 
        FROM responses r
        JOIN questions q ON r.question_id = q.id
        WHERE r.user_id = ?
    """, [user_id])
    
    answered_ids = [row['id'] for row in answered]
    print(f"Answered IDs: {answered_ids}")  # Debug line
    
    if not answered_ids:
        # First time user: show all mandatory questions
        questions = query_db("""
            SELECT * FROM questions 
            WHERE is_mandatory = 1 
            ORDER BY id
        """)
        return questions[:count]
    
    # Returning user: mix of new and repeat
    # NEW QUESTIONS (questions they've NEVER answered)
    placeholders = ','.join(['?'] * len(answered_ids))
    new_questions = query_db(f"""
        SELECT * FROM questions 
        WHERE id NOT IN ({placeholders})
        ORDER BY RANDOM() LIMIT ?
    """, answered_ids + [count])
    
    # If we don't have enough new questions, fill with repeats
    if len(new_questions) < count:
        remaining = count - len(new_questions)
        repeat_questions = query_db(f"""
            SELECT * FROM questions 
            WHERE id IN ({placeholders})
            ORDER BY RANDOM() LIMIT ?
        """, answered_ids + [remaining])
        
        # Combine and shuffle
        all_selected = list(new_questions) + list(repeat_questions)
    else:
        all_selected = list(new_questions)
    
    random.shuffle(all_selected)
    return all_selected[:count]

# ------------------------------------------------------------------------------
# ROUTES: AUTH
# ------------------------------------------------------------------------------

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page (simple email-only auth for hackathon)"""
    if request.method == 'POST':
        email = request.form['email']
        
        # Check if user exists
        user = query_db('SELECT * FROM users WHERE email = ?', [email], one=True)
        
        if not user:
            # Create new user
            user_id = execute_db(
                'INSERT INTO users (email) VALUES (?)', 
                [email]
            )
            session['user_id'] = user_id
            session['is_new_user'] = True
            return redirect('/questions')
        else:
            # Existing user
            session['user_id'] = user['id']
            session['is_new_user'] = False
            return redirect('/dashboard')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register page (just uses login logic for simplicity)"""
    if request.method == 'POST':
        email = request.form['email']
        
        # Check if exists
        user = query_db('SELECT * FROM users WHERE email = ?', [email], one=True)
        
        if user:
            session['user_id'] = user['id']
            session['is_new_user'] = False
            return redirect('/dashboard')
        else:
            user_id = execute_db(
                'INSERT INTO users (email) VALUES (?)', 
                [email]
            )
            session['user_id'] = user_id
            session['is_new_user'] = True
            return redirect('/questions')
    
    return render_template('login.html')  # Reuse login template

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ------------------------------------------------------------------------------
# ROUTES: QUESTIONNAIRE
# ------------------------------------------------------------------------------

@app.route('/questions')
def questions():
    """Show questionnaire"""
    user = get_current_user()
    if not user:
        return redirect('/login')
    
    # Get or create session ID
    if 'current_session_id' not in session:
        session['current_session_id'] = generate_session_id()
    
    # Get questions for this session
    questions_list = get_next_questions(user['id'], count=5)
    
    if not questions_list:
        # No questions left? Redirect to dashboard
        return redirect('/dashboard')
    
    # Get current question (first in list)
    current_q = questions_list[0]
    
    # Get answer options for this question
    answer_options = query_db("""
        SELECT * FROM answer_options 
        WHERE question_id = ? 
        ORDER BY sort_order
    """, [current_q['id']])
    
    # Count answered in this session
    answered_count = query_db("""
        SELECT COUNT(*) as count FROM responses 
        WHERE user_id = ? AND session_id = ?
    """, [user['id'], session['current_session_id']], one=True)['count']
    
    return render_template(
        'questions.html',
        current_question=current_q,
        answer_options=answer_options,
        answered_count=answered_count,
        total_in_session=5,
        is_new_user=session.get('is_new_user', False)
    )

@app.route('/save_response', methods=['POST'])
def save_response():
    """Save answer and return random comment"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    question_id = data['question_id']
    answer_option_id = data['answer_option_id']
    answer_value = data['answer_value']
    
    # Get random comment from comments_pool
    comments = query_db("""
        SELECT comment_text FROM comments_pool 
        WHERE answer_option_id = ?
    """, [answer_option_id])
    
    if comments:
        selected_comment = random.choice(comments)['comment_text']
    else:
        selected_comment = "Thanks for sharing. 💜"
    
    # Ensure session exists
    if 'current_session_id' not in session:
        session['current_session_id'] = generate_session_id()
    
    # Check if already answered this question in this session
    existing = query_db("""
        SELECT id FROM responses 
        WHERE user_id = ? AND question_id = ? AND session_id = ?
    """, [user['id'], question_id, session['current_session_id']], one=True)
    
    if existing:
        # Update existing
        execute_db("""
            UPDATE responses 
            SET answer_option_id = ?, answer_value = ?, comment_used = ?, created_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, [answer_option_id, answer_value, selected_comment, existing['id']])
    else:
        # Insert new
        execute_db("""
            INSERT INTO responses 
            (user_id, question_id, answer_option_id, answer_value, comment_used, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [user['id'], question_id, answer_option_id, answer_value, selected_comment, session['current_session_id']])
    
    # Count answers in this session
    answered_count = query_db("""
        SELECT COUNT(*) as count FROM responses 
        WHERE user_id = ? AND session_id = ?
    """, [user['id'], session['current_session_id']], one=True)['count']
    
    print(f"Session {session['current_session_id']} has {answered_count} answers")
    
    session_complete = (answered_count >= 5)
    
    return jsonify({
        'success': True,
        'comment': selected_comment,
        'session_complete': session_complete,
        'answered_count': answered_count
    })

@app.route('/next-question')
def next_question():
    """Get next question or redirect to dashboard if done"""
    user = get_current_user()
    if not user:
        return redirect('/login')
    
    # Check if session complete
    answered_count = query_db("""
        SELECT COUNT(*) as count FROM responses 
        WHERE user_id = ? AND session_id = ?
    """, [user['id'], session.get('current_session_id', '')], one=True)
    
    if answered_count and answered_count['count'] >= 5:
        # Session complete - calculate metrics and redirect
        metrics = calculate_all_metrics(user['id'], session['current_session_id'])
        # Clear session
        session.pop('current_session_id', None)
        session['is_new_user'] = False
        return redirect('/dashboard')
    
    # Otherwise go back to questions
    return redirect('/questions')

# ------------------------------------------------------------------------------
# ROUTES: DASHBOARD
# ------------------------------------------------------------------------------

@app.route('/dashboard')
def dashboard():
    """Show user dashboard with metrics"""
    user = get_current_user()
    if not user:
        return redirect('/login')
    
    # Get latest metrics
    metrics = get_latest_metrics(user['id'])
    
    # For burnout ring, convert score to degrees (0-360)
    burnout_deg = (metrics['burnout_score'] / 100) * 360
    
    return render_template(
        'dashboard.html',
        user=user,
        burnout_score=metrics['burnout_score'],
        burnout_deg=burnout_deg,
        balance_score=metrics['balance_score'],
        mental_load_you=metrics['mental_load_you'],
        mental_load_partner=metrics['mental_load_partner'],
        recovery_index=metrics['recovery_index'],
        last_updated=metrics.get('calculated_at', 'Just now')
    )

@app.route('/api/metrics/latest')
def api_latest_metrics():
    """API endpoint for AJAX updates"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    
    metrics = get_latest_metrics(user['id'])
    return jsonify({
        'burnout': metrics['burnout_score'],
        'balance': metrics['balance_score'],
        'mental_you': metrics['mental_load_you'],
        'mental_partner': metrics['mental_load_partner'],
        'recovery': metrics['recovery_index']
    })

# ------------------------------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------------------------------

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'time': datetime.now().isoformat()})

    
    # ... rest of code ...
# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)