CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_key TEXT UNIQUE,
    question_text TEXT,
    input_type TEXT,  -- 'slider', 'buttons', 'boolean'
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
    answer_value INTEGER,  -- The NUMERIC value for calculations
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