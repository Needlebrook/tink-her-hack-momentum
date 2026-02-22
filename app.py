import os
import sqlite3
import random
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, session, jsonify, g

app = Flask(__name__)
app.secret_key = 'momentum-womens-hackathon-2025'  

# DATABASE HELPERS
DATABASE = 'momentum.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # dictionary-like rows
    return db

def init_db_on_startup():
    """Initialize database with schema and seed data ONLY if empty"""
    db_path = 'momentum.db'
    print(f"📁 Checking database at: {db_path}")
    
    # Check if database exists and has tables
    db_exists = os.path.exists(db_path)
    has_tables = False
    
    if db_exists:
        try:
            conn = sqlite3.connect(db_path)
            # Check if questions table exists and has data
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'").fetchone()
            if result:
                count = conn.execute("SELECT COUNT(*) as count FROM questions").fetchone()[0]
                has_tables = (count > 0)
            conn.close()
        except:
            has_tables = False
    
    # Only recreate if database is missing or empty
    if not db_exists or not has_tables:
        print("⚙️ Database missing or empty. Creating fresh database...")
        
        # Remove old DB if it exists but is empty
        if db_exists:
            os.remove(db_path)
            print("🗑️ Removed empty database")
        
        conn = sqlite3.connect(db_path)
        
        # Create tables from schema.sql
        print("📝 Creating tables...")
        conn.executescript('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_key TEXT UNIQUE,
                question_text TEXT,
                input_type TEXT,
                is_mandatory BOOLEAN DEFAULT 0,
                category TEXT
            );

            CREATE TABLE answer_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER,
                display_text TEXT,
                value_min INTEGER,
                value_max INTEGER,
                sort_order INTEGER,
                FOREIGN KEY(question_id) REFERENCES questions(id)
            );

            CREATE TABLE comments_pool (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                answer_option_id INTEGER,
                comment_text TEXT,
                FOREIGN KEY(answer_option_id) REFERENCES answer_options(id)
            );

            CREATE TABLE responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question_id INTEGER,
                answer_option_id INTEGER,
                answer_value INTEGER,
                comment_used TEXT,
                session_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(question_id) REFERENCES questions(id),
                FOREIGN KEY(answer_option_id) REFERENCES answer_options(id)
            );

            CREATE TABLE metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT,
                burnout_score INTEGER,
                balance_score INTEGER,
                mental_load_you INTEGER,
                mental_load_partner INTEGER,
                recovery_index TEXT,
                calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE INDEX idx_responses_user_session ON responses(user_id, session_id);
            CREATE INDEX idx_metrics_user_session ON metrics(user_id, session_id);
            CREATE INDEX idx_comments_pool_option ON comments_pool(answer_option_id);
        ''')
        
        # Insert questions
        print("🌱 Inserting 12 questions...")
        conn.executescript('''
            INSERT INTO questions (question_key, question_text, input_type, is_mandatory, category) VALUES
            ('sleep_hours', 'How many hours of sleep do you average per night?', 'buttons', 1, 'burnout'),
            ('work_hours', 'How many hours do you work per week (paid work)?', 'slider', 1, 'burnout'),
            ('overload_streak', 'How many days in a row have you felt overwhelmed?', 'buttons', 1, 'burnout'),
            ('housework_hours', 'How many hours of housework do you do daily?', 'slider', 1, 'balance'),
            ('childcare_hours', 'How many hours of childcare daily?', 'slider', 1, 'balance'),
            ('personal_time', 'How much personal time do you get daily?', 'buttons', 1, 'balance'),
            ('mental_planning', 'Who handles family planning (appointments, schedules)?', 'buttons', 1, 'mental'),
            ('mental_emotional', 'Who manages emotional well-being of family members?', 'buttons', 1, 'mental'),
            ('mental_household', 'Who tracks household needs (groceries, supplies)?', 'buttons', 1, 'mental'),
            ('me_time_quality', 'How would you rate your "me time" quality?', 'buttons', 1, 'recovery'),
            ('weekend_rest', 'How restful are your weekends?', 'buttons', 1, 'recovery'),
            ('break_frequency', 'How often do you take breaks during work?', 'buttons', 1, 'recovery');
        ''')
        
        # Insert answer options for sleep_hours (id=1)
        conn.executescript('''
            INSERT INTO answer_options (question_id, display_text, value_min, value_max, sort_order) VALUES
            (1, 'Less than 4 hours', 0, 4, 1),
            (1, '4-5 hours', 4, 5, 2),
            (1, '5-6 hours', 5, 6, 3),
            (1, '6-7 hours', 6, 7, 4),
            (1, '7-8 hours', 7, 8, 5),
            (1, '8+ hours', 8, 24, 6);
        ''')
        
        # Add more options as needed - for brevity, I'll add just one more
        conn.executescript('''
            INSERT INTO answer_options (question_id, display_text, value_min, value_max, sort_order) VALUES
            (2, 'Less than 20 hours', 0, 20, 1),
            (2, '20-30 hours', 20, 30, 2),
            (2, '30-40 hours', 30, 40, 3),
            (2, '40-50 hours', 40, 50, 4),
            (2, '50-60 hours', 50, 60, 5),
            (2, '60+ hours', 60, 100, 6);
        ''')
        
        # Add a few comments
        conn.executescript('''
            INSERT INTO comments_pool (answer_option_id, comment_text) VALUES
            (1, 'Mama, that''s survival mode. Even 15 minutes more helps.'),
            (1, 'You''re running on fumes. Can you nap when they nap?'),
            (2, 'Close to the goal! Consistency is key.'),
            (2, 'You''re doing great. Small adjustments add up.');
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully with seed data")
    else:
        print("✅ Database already exists and has data - keeping it")
    
    # Verify final state
    try:
        conn = sqlite3.connect(db_path)
        q_count = conn.execute("SELECT COUNT(*) as count FROM questions").fetchone()[0]
        opt_count = conn.execute("SELECT COUNT(*) as count FROM answer_options").fetchone()[0]
        comm_count = conn.execute("SELECT COUNT(*) as count FROM comments_pool").fetchone()[0]
        conn.close()
        print(f"📊 Final database stats: {q_count} questions, {opt_count} options, {comm_count} comments")
    except:
        print("⚠️ Could not verify database")


init_db_on_startup()

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

# USER SESSION HELPERS
def get_current_user():
    """Get current user from session"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)

def generate_session_id():
    """Generate unique session ID for a group of responses"""
    return str(uuid.uuid4())

# METRICS CALCULATION ENGINE (Your Differentiator)

def calculate_burnout(responses):
    """🔥 Burnout Risk Meter (0-100)"""
    sleep = responses.get('sleep_hours', 7)
    work = responses.get('work_hours', 40)
    housework = responses.get('housework_hours', 2)
    
    mental_keys = [
        'mental_planning',    # Who handles planning?
        'mental_emotional',   # Who manages emotions?
        'mental_household'    # Who tracks household needs?
    ]
    mental_values = [responses.get(k, 1) for k in mental_keys if k in responses]
    mental_avg = sum(mental_values) / len(mental_values) if mental_values else 1
    
    sleep_deficit = max(0, 8 - sleep) * 10    
    work_overload = max(0, work - 40) * 2       
    housework_load = min(housework * 5, 25)     
    mental_component = mental_avg * 12.5        
    
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
        return 50, 50 
    
    your_percent = (mental_sum / max_possible) * 100
    return round(your_percent), round(100 - your_percent)


def calculate_recovery(responses):
    """🌿 Recovery Index"""
    sleep = responses.get('sleep_hours', 7)
    me_time_quality = responses.get('me_time_quality', 2)
    weekend_rest = responses.get('weekend_rest', 2)
    break_freq = responses.get('break_frequency', 2)
    overload = responses.get('overload_streak', 1)
    
    if overload == 0:
        overload = 1
    
    recovery_score = (me_time_quality + weekend_rest + break_freq) / 1.2
    
    recovery_raw = (sleep + recovery_score) / overload
    
    if recovery_raw > 12:
        return "High Recovery"
    elif recovery_raw > 6:
        return "Moderate"
    else:
        return "Depleted"

def calculate_all_metrics(user_id, session_id):
    """Calculate and store all metrics for a user session"""
    responses_rows = query_db("""
        SELECT q.question_key, r.answer_value 
        FROM responses r
        JOIN questions q ON r.question_id = q.id
        WHERE r.user_id = ? AND r.session_id = ?
    """, [user_id, session_id])
    
    responses = {row['question_key']: row['answer_value'] for row in responses_rows}
    
    burnout = calculate_burnout(responses)
    balance = calculate_balance(responses)
    mental_you, mental_partner = calculate_mental_load(responses)
    recovery = calculate_recovery(responses)
    
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
            'recovery_index': 'Moderate',
            'calculated_at': 'Just now'  
        }
    
    # Convert Row to dictionary 
    return dict(metrics)

def count_unanswered_questions(user_id):
    """Count how many questions user hasn't answered yet"""
    total_questions = query_db("SELECT COUNT(*) as count FROM questions", one=True)['count']
    answered = query_db("""
        SELECT COUNT(DISTINCT question_id) as count 
        FROM responses 
        WHERE user_id = ?
    """, [user_id], one=True)['count']
    
    return total_questions - answered

def generate_feedback(burnout, balance, mental_you, recovery):
    """Generate personalized feedback based on metrics"""
    feedback = []
    
    # Burnout feedback
    if burnout >= 70:
        feedback.append("🔴 **High Burnout Risk:** Your body is signaling overload. Consider taking a personal day and delegating non-essential tasks.")
    elif burnout >= 40:
        feedback.append("🟡 **Moderate Strain:** You're managing, but barely. Try to carve out 15 minutes of uninterrupted rest daily.")
    else:
        feedback.append("🟢 **Low Burnout:** You're maintaining well! Keep protecting your boundaries.")
    
    # Balance feedback
    if balance < 40:
        feedback.append("⚖️ **Overloaded:** Work and duties are consuming your time. Can you automate or outsource one household task?")
    elif balance < 70:
        feedback.append("⚖️ **Slightly Imbalanced:** You're close to balance. Try a 'power down' hour before bed with no screens.")
    else:
        feedback.append("⚖️ **Well-Balanced:** Your time distribution looks healthy! You're modeling sustainable habits.")
    
    # Mental load feedback
    if mental_you > 70:
        feedback.append("🧠 **Heavy Mental Load:** You're carrying most cognitive labor. Have a conversation about sharing school tracking or meal planning.")
    elif mental_you < 40:
        feedback.append("🧠 **Shared Mental Load:** True partnership! Your cognitive labor is well distributed.")
    else:
        feedback.append("🧠 **Mixed Mental Load:** You're sharing some tasks. Identify one mental load item to delegate this week.")
    
    # Recovery feedback
    if recovery == "Depleted":
        feedback.append("🌿 **Depleted:** Your rest isn't matching your effort. Even 10 minutes of guilt-free me-time helps reset.")
    elif recovery == "Moderate":
        feedback.append("🌿 **Moderate Recovery:** You're getting some rest. Try a tech-free Sunday morning to recharge.")
    else:
        feedback.append("🌿 **High Recovery:** Your rest habits are excellent! You're protecting your well-being.")
    
    # Pick 2-3 most relevant based on extreme scores
    priority_feedback = []
    
    # Always include highest priority issues
    if burnout >= 70:
        priority_feedback.append(feedback[0])
    if balance < 40:
        priority_feedback.append(feedback[1])
    if mental_you > 70:
        priority_feedback.append(feedback[2])
    if recovery == "Depleted":
        priority_feedback.append(feedback[3])
    
    # If nothing extreme, give general encouragement
    if len(priority_feedback) == 0:
        priority_feedback = [
            "✨ You're doing well! Small consistent actions maintain momentum.",
            feedback[0],  # Burnout
            feedback[3]   # Recovery
        ]
    
    return priority_feedback[:3]  # Return top 3

# QUESTIONNAIRE LOGIC
def get_next_questions(user_id, count=5, mode='random'):
    """Get next set of questions based on mode:
       - 'new_user': 12 random questions
       - 'unanswered': random unanswered questions
       - 'random': mix of unanswered and repeats
    """
    
    all_questions = query_db("SELECT * FROM questions")
    
    answered = query_db("""
        SELECT DISTINCT question_id FROM responses 
        WHERE user_id = ?
    """, [user_id])
    answered_ids = [row['question_id'] for row in answered]
    
    if answered_ids:
        placeholders = ','.join(['?'] * len(answered_ids))
        unanswered = query_db(f"""
            SELECT * FROM questions 
            WHERE id NOT IN ({placeholders})
            ORDER BY RANDOM()
        """, answered_ids)
    else:
        unanswered = all_questions
    
    if mode == 'new_user':
        return list(unanswered)[:12] if len(unanswered) >= 12 else list(unanswered)
    
    elif mode == 'unanswered':
        return list(unanswered)[:count]
    
    else:  
        if len(unanswered) >= count:
            return list(unanswered)[:count]
        else:
            result = list(unanswered)
            remaining = count - len(result)

            if answered_ids:
                repeat_placeholders = ','.join(['?'] * len(answered_ids))
                repeats = query_db(f"""
                    SELECT * FROM questions 
                    WHERE id IN ({repeat_placeholders})
                    ORDER BY RANDOM() LIMIT ?
                """, answered_ids + [remaining])
                result.extend(list(repeats))
            
            random.shuffle(result)
            return result

# ROUTES: AUTH
@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page (simple email-only auth for hackathon)"""
    if request.method == 'POST':
        email = request.form['email']
        user = query_db('SELECT * FROM users WHERE email = ?', [email], one=True)
        
        if not user:
            user_id = execute_db(
                'INSERT INTO users (email) VALUES (?)', 
                [email]
            )
            session['user_id'] = user_id
            session['is_new_user'] = True
            return redirect('/questions')
        else:
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
    
    return render_template('login.html')  

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ROUTES: QUESTIONNAIRE
@app.route('/questions')
def questions():
    """Show questionnaire - SIMPLIFIED FOR RENDER"""
    user = get_current_user()
    if not user:
        return redirect('/login')
    
    # Get ONE random question
    question_row = query_db("SELECT * FROM questions ORDER BY RANDOM() LIMIT 1", one=True)
    if not question_row:
        return "No questions in database!", 500
    
    # FORCE CONVERSION TO DICTIONARY
    current_question = {
        'id': question_row['id'],
        'question_text': question_row['question_text'],
        'question_key': question_row['question_key'],
        'input_type': question_row['input_type'],
        'category': question_row['category']
    }
    
    # Get options and force to list of dicts
    option_rows = query_db("SELECT * FROM answer_options WHERE question_id = ? ORDER BY sort_order", [current_question['id']])
    answer_options = []
    for row in option_rows:
        answer_options.append({
            'id': row['id'],
            'display_text': row['display_text'],
            'value_min': row['value_min'],
            'value_max': row['value_max']
        })
    
    # Simple session tracking
    if 'current_session_id' not in session:
        session['current_session_id'] = generate_session_id()
    
    # Count answers in this session
    answered_count = query_db("""
        SELECT COUNT(*) as count FROM responses 
        WHERE user_id = ? AND session_id = ?
    """, [user['id'], session['current_session_id']], one=True)['count']
    
    print(f"✅ Questions page loaded - Question: {current_question['question_text']}, Options: {len(answer_options)}")
    
    return render_template(
        'questions.html',
        current_question=current_question,
        answer_options=answer_options,
        answered_count=answered_count,
        total_in_session=5,
        is_new_user=False
    )

@app.route('/debug-routes')
def debug_routes():
    """List all registered routes"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    return jsonify(routes)
@app.route('/debug-render')
def debug_render():
    """Check what's different on Render"""
    import os
    import sqlite3
    
    info = {
        'platform': os.environ.get('RENDER', 'not set'),
        'working_dir': os.getcwd(),
        'files_in_dir': os.listdir('.'),
        'templates_exist': os.path.exists('templates/questions.html'),
        'database_exists': os.path.exists('momentum.db'),
    }
    
    # Check database content
    if os.path.exists('momentum.db'):
        try:
            conn = sqlite3.connect('momentum.db')
            questions = conn.execute("SELECT COUNT(*) as count FROM questions").fetchone()[0]
            info['question_count'] = questions
            
            # Check a sample question
            sample = conn.execute("SELECT * FROM questions LIMIT 1").fetchone()
            info['sample_question'] = dict(sample) if sample else None
            conn.close()
        except Exception as e:
            info['db_error'] = str(e)
    
    return jsonify(info)

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

    comments = query_db("""
        SELECT comment_text FROM comments_pool 
        WHERE answer_option_id = ?
    """, [answer_option_id])
    
    if comments:
        selected_comment = random.choice(comments)['comment_text']
    else:
        selected_comment = "Thanks for sharing. 💜"
    
    if 'current_session_id' not in session:
        session['current_session_id'] = generate_session_id()
    existing = query_db("""
        SELECT id FROM responses 
        WHERE user_id = ? AND question_id = ? AND session_id = ?
    """, [user['id'], question_id, session['current_session_id']], one=True)
    
    if existing:
        execute_db("""
            UPDATE responses 
            SET answer_option_id = ?, answer_value = ?, comment_used = ?, created_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, [answer_option_id, answer_value, selected_comment, existing['id']])
    else:

        execute_db("""
            INSERT INTO responses 
            (user_id, question_id, answer_option_id, answer_value, comment_used, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [user['id'], question_id, answer_option_id, answer_value, selected_comment, session['current_session_id']])

    answered_count = query_db("""
        SELECT COUNT(*) as count FROM responses 
        WHERE user_id = ? AND session_id = ?
    """, [user['id'], session['current_session_id']], one=True)['count']
    
    total_expected = session.get('total_in_session', 5)
    
    print(f"📝 Session {session['current_session_id']} - Answer {answered_count}/{total_expected} saved")
    
    if answered_count >= 3:  
        try:
            responses_rows = query_db("""
                SELECT q.question_key, r.answer_value 
                FROM responses r
                JOIN questions q ON r.question_id = q.id
                WHERE r.user_id = ? AND r.session_id = ?
            """, [user['id'], session['current_session_id']])
            
            responses_dict = {row['question_key']: row['answer_value'] for row in responses_rows}
            
            # Calculate current scores
            burnout = calculate_burnout(responses_dict)
            balance = calculate_balance(responses_dict)
            mental_you, mental_partner = calculate_mental_load(responses_dict)
            recovery = calculate_recovery(responses_dict)
            
            print(f"   🔥 Burnout: {burnout}, ⚖️ Balance: {balance}, 🧠 Mental: {mental_you}/{mental_partner}, 🌿 Recovery: {recovery}")
        except Exception as e:
            print(f"   ⚠️ Couldn't calculate interim metrics: {e}")

    session_complete = (answered_count >= total_expected)
    
    if session_complete:
        print(f"✅ SESSION COMPLETE! Storing metrics for {answered_count} answers")
        try:
            metrics = calculate_all_metrics(user['id'], session['current_session_id'])
            print(f"   STORED: 🔥 {metrics['burnout']}, ⚖️ {metrics['balance']}, 🧠 {metrics['mental_you']}/{metrics['mental_partner']}, 🌿 {metrics['recovery']}")
        except Exception as e:
            print(f"   ❌ Error storing metrics: {e}")
    
    return jsonify({
        'success': True,
        'comment': selected_comment,
        'session_complete': session_complete,
        'answered_count': answered_count,
        'total_expected': total_expected
    })

@app.route('/next-question')
def next_question():
    """Get next question or show completion in same page"""
    user = get_current_user()
    if not user:
        return redirect('/login')
    current_questions = session.get('current_questions', [])
    
    if len(current_questions) > 1:
        session['current_questions'] = current_questions[1:]
        return redirect('/questions')

    return redirect('/questions')

@app.route('/more-questions')
def more_questions():
    """Load another batch of 5 questions"""
    user = get_current_user()
    if not user:
        return redirect('/login')
    
    # Start a new session
    session['current_session_id'] = generate_session_id()
    session['question_session_active'] = True
    session['questions_remaining'] = 5
    session['total_in_session'] = 5 
    
    return redirect('/questions')

# ROUTES: DASHBOARD
@app.route('/dashboard')
def dashboard():
    """Show user dashboard with metrics"""
    user = get_current_user()
    if not user:
        return redirect('/login')
    
    # Get latest metrics (returns dict)
    metrics = get_latest_metrics(user['id'])
    
    # For burnout ring, convert score to degrees (0-360)
    burnout_deg = (metrics['burnout_score'] / 100) * 360
    
    # Generate personalized feedback
    feedback_list = generate_feedback(
        metrics['burnout_score'],
        metrics['balance_score'],
        metrics['mental_load_you'],
        metrics['recovery_index']
    )
    
    return render_template(
        'dashboard.html',
        user=user,
        burnout_score=metrics['burnout_score'],
        burnout_deg=burnout_deg,
        balance_score=metrics['balance_score'],
        mental_load_you=metrics['mental_load_you'],
        mental_load_partner=metrics['mental_load_partner'],
        recovery_index=metrics['recovery_index'],
        last_updated=metrics.get('calculated_at', 'Just now'),
        feedback=feedback_list  # ← NEW
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

# HEALTH CHECK
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'time': datetime.now().isoformat()})
 
# MAIN
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) 
    app.run(host='0.0.0.0', port=port, debug=False)