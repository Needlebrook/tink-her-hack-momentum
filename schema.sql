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

-- FIRST, CLEAR EXISTING DATA 
DELETE FROM comments_pool;
DELETE FROM answer_options;
DELETE FROM questions;
DELETE FROM sqlite_sequence;

-- 1. INSERT ALL 12 QUESTIONS
INSERT INTO questions (question_key, question_text, input_type, is_mandatory, category) VALUES
-- BURNOUT METER QUESTIONS (3)
('sleep_hours', 'How many hours of sleep do you average per night?', 'buttons', 1, 'burnout'),
('work_hours', 'How many hours do you work per week (paid work)?', 'slider', 1, 'burnout'),
('overload_streak', 'How many days in a row have you felt overwhelmed?', 'buttons', 1, 'burnout'),

-- WORK-LIFE BALANCE QUESTIONS (3)
('housework_hours', 'How many hours of housework do you do daily?', 'slider', 1, 'balance'),
('childcare_hours', 'How many hours of childcare daily?', 'slider', 1, 'balance'),
('personal_time', 'How much personal time do you get daily?', 'buttons', 1, 'balance'),

-- MENTAL LOAD QUESTIONS (3) - YOUR DIFFERENTIATOR
('mental_planning', 'Who handles family planning (appointments, schedules)?', 'buttons', 1, 'mental'),
('mental_emotional', 'Who manages emotional well-being of family members?', 'buttons', 1, 'mental'),
('mental_household', 'Who tracks household needs (groceries, supplies)?', 'buttons', 1, 'mental'),

-- RECOVERY INDEX QUESTIONS (3)
('me_time_quality', 'How would you rate your "me time" quality?', 'buttons', 1, 'recovery'),
('weekend_rest', 'How restful are your weekends?', 'buttons', 1, 'recovery'),
('break_frequency', 'How often do you take breaks during work?', 'buttons', 1, 'recovery');

-- 2. ANSWER OPTIONS FOR EACH QUESTION

-- sleep_hours (question_id = 1)
INSERT INTO answer_options (question_id, display_text, value_min, value_max, sort_order) VALUES
(1, 'Less than 4 hours', 0, 4, 1),
(1, '4-5 hours', 4, 5, 2),
(1, '5-6 hours', 5, 6, 3),
(1, '6-7 hours', 6, 7, 4),
(1, '7-8 hours', 7, 8, 5),
(1, '8+ hours', 8, 24, 6);

-- work_hours (question_id = 2)
INSERT INTO answer_options (question_id, display_text, value_min, value_max, sort_order) VALUES
(2, 'Less than 20 hours', 0, 20, 1),
(2, '20-30 hours', 20, 30, 2),
(2, '30-40 hours', 30, 40, 3),
(2, '40-50 hours', 40, 50, 4),
(2, '50-60 hours', 50, 60, 5),
(2, '60+ hours', 60, 100, 6);

-- overload_streak (question_id = 3)
INSERT INTO answer_options (question_id, display_text, value_min, value_max, sort_order) VALUES
(3, 'None', 0, 0, 1),
(3, '1-2 days', 1, 2, 2),
(3, '3-4 days', 3, 4, 3),
(3, '5-6 days', 5, 6, 4),
(3, '7+ days', 7, 30, 5);

-- housework_hours (question_id = 4)
INSERT INTO answer_options (question_id, display_text, value_min, value_max, sort_order) VALUES
(4, 'Less than 1 hour', 0, 1, 1),
(4, '1-2 hours', 1, 2, 2),
(4, '2-3 hours', 2, 3, 3),
(4, '3-4 hours', 3, 4, 4),
(4, '4+ hours', 4, 24, 5);

-- childcare_hours (question_id = 5)
INSERT INTO answer_options (question_id, display_text, value_min, value_max, sort_order) VALUES
(5, 'Less than 2 hours', 0, 2, 1),
(5, '2-4 hours', 2, 4, 2),
(5, '4-6 hours', 4, 6, 3),
(5, '6-8 hours', 6, 8, 4),
(5, '8+ hours', 8, 24, 5);

-- personal_time (question_id = 6)
INSERT INTO answer_options (question_id, display_text, value_min, value_max, sort_order) VALUES
(6, 'None', 0, 0, 1),
(6, '15-30 minutes', 15, 30, 2),
(6, '30-60 minutes', 30, 60, 3),
(6, '1-2 hours', 60, 120, 4),
(6, '2+ hours', 120, 480, 5);

-- mental_planning (question_id = 7)
INSERT INTO answer_options (question_id, display_text, value_min, value_max, sort_order) VALUES
(7, 'Mostly me', 2, 2, 1),
(7, 'Shared equally', 1, 1, 2),
(7, 'Mostly partner', 0, 0, 3);

-- mental_emotional (question_id = 8)
INSERT INTO answer_options (question_id, display_text, value_min, value_max, sort_order) VALUES
(8, 'Mostly me', 2, 2, 1),
(8, 'Shared equally', 1, 1, 2),
(8, 'Mostly partner', 0, 0, 3);

-- mental_household (question_id = 9)
INSERT INTO answer_options (question_id, display_text, value_min, value_max, sort_order) VALUES
(9, 'Mostly me', 2, 2, 1),
(9, 'Shared equally', 1, 1, 2),
(9, 'Mostly partner', 0, 0, 3);

-- me_time_quality (question_id = 10)
INSERT INTO answer_options (question_id, display_text, value_min, value_max, sort_order) VALUES
(10, 'Poor - constantly interrupted', 1, 1, 1),
(10, 'Fair - sometimes interrupted', 2, 2, 2),
(10, 'Good - mostly uninterrupted', 3, 3, 3),
(10, 'Excellent - truly restorative', 4, 4, 4);

-- weekend_rest (question_id = 11)
INSERT INTO answer_options (question_id, display_text, value_min, value_max, sort_order) VALUES
(11, 'Not restful - just as busy', 1, 1, 1),
(11, 'Somewhat restful', 2, 2, 2),
(11, 'Restful', 3, 3, 3),
(11, 'Very restful - recharge fully', 4, 4, 4);

-- break_frequency (question_id = 12)
INSERT INTO answer_options (question_id, display_text, value_min, value_max, sort_order) VALUES
(12, 'Rarely take breaks', 1, 1, 1),
(12, '1-2 breaks per day', 2, 2, 2),
(12, '3-4 breaks per day', 3, 3, 3),
(12, 'Regular breaks + lunch away', 4, 4, 4);

-- 3. COMMENTS FOR VARIETY (3-5 per answer option)

-- sleep_hours comments (ids 1-6)
INSERT INTO comments_pool (answer_option_id, comment_text) VALUES
(1, 'Mama, that''s survival mode. Even 15 minutes more helps.'),
(1, 'You''re running on fumes. Can you nap when they nap?'),
(1, 'The 4am club is overrated. Let''s find you 30 more minutes.'),
(1, 'Sleep deprivation is real. What''s one thing you can drop?'),
(2, 'Close to the goal! Consistency is key.'),
(2, 'You''re doing great. Small adjustments add up.'),
(2, 'Every hour counts. Proud of you for trying.'),
(2, '4-5 hours is tough. Can you rest this weekend?'),
(3, 'Solid sleep! Your future self thanks you.'),
(3, 'Look at you, modeling healthy habits!'),
(3, 'Rest is productive. Keep it up!'),
(3, '5-6 hours is a good baseline.'),
(4, '6-7 hours is solid! You''re in a good place.'),
(4, 'Almost there! Can you protect this sleep?'),
(4, 'Consistent sleep = better days. Keep it up!'),
(5, '7-8 hours is ideal! You''re thriving.'),
(5, 'Look at you, prioritizing rest!'),
(5, 'This is how we prevent burnout.'),
(6, '8+ hours? Queen behavior!'),
(6, 'You''ve cracked the sleep code.'),
(6, 'Rest is your superpower.');

-- work_hours comments (ids 7-12)
INSERT INTO comments_pool (answer_option_id, comment_text) VALUES
(7, 'That''s a manageable pace. Well done.'),
(7, 'Work-life balance starts here.'),
(7, 'Part-time work + family = smart choice.'),
(8, 'You''re putting in the hours. Take breaks.'),
(8, 'Remember to step away sometimes.'),
(8, '20-30 hours is a sweet spot.'),
(9, 'Full-time work + family = superhero.'),
(9, 'That''s a full plate. Let''s check your recovery.'),
(9, '30-40 hours is standard, but how do YOU feel?'),
(10, 'Long hours. Can you delegate anything?'),
(10, 'Your hard work is seen. Protect your rest.'),
(10, '40-50 hours + family = intense.'),
(11, 'That''s intense. Burnout risk is real.'),
(11, 'Please take care of YOU too.'),
(11, '50-60 hours is a lot. Let''s talk boundaries.'),
(12, 'This is unsustainable long-term. Let''s talk.'),
(12, 'You''re burning bright. Don''t burn out.'),
(12, '60+ hours is heroic but costly.');

-- overload_streak comments (ids 13-17)
INSERT INTO comments_pool (answer_option_id, comment_text) VALUES
(13, 'Great! You''re managing stress well.'),
(13, 'No overload days? That''s wonderful.'),
(14, 'A few tough days. You''ve got this.'),
(14, '1-2 days is normal. Rest up.'),
(15, 'Several days is tough. Be gentle with yourself.'),
(15, '3-4 days means you need support.'),
(16, 'Almost a week. Time to pause.'),
(16, '5-6 days is a red flag. Let''s talk.'),
(17, 'This is serious. Please reach out.'),
(17, 'You''ve been carrying too long. Let''s lighten the load.');

-- housework_hours comments (ids 18-22)
INSERT INTO comments_pool (answer_option_id, comment_text) VALUES
(18, 'Minimal housework? Winning!'),
(18, 'Less than an hour is ideal.'),
(19, '1-2 hours is reasonable.'),
(19, 'You''re keeping things tidy.'),
(20, '2-3 hours is significant.'),
(20, 'That''s a part-time job right there.'),
(21, '3-4 hours is exhausting.'),
(21, 'Can you get help with this?'),
(22, '4+ hours is unsustainable.'),
(22, 'This is too much. Let''s redistribute.');

-- childcare_hours comments (ids 23-27)
INSERT INTO comments_pool (answer_option_id, comment_text) VALUES
(23, 'Less than 2 hours? Enjoy this phase!'),
(23, 'Quality over quantity matters.'),
(24, '2-4 hours is balanced.'),
(24, 'You''re present and engaged.'),
(25, '4-6 hours is full-on parenting.'),
(25, 'That''s a lot of little human time.'),
(26, '6-8 hours is intense.'),
(26, 'You''re deeply involved. Remember you too.'),
(27, '8+ hours? You''re superhuman.'),
(27, 'Full-time parenting is real work.');

-- personal_time comments (ids 28-32)
INSERT INTO comments_pool (answer_option_id, comment_text) VALUES
(28, 'None? Let''s find you 5 minutes.'),
(28, 'You deserve time too.'),
(29, '15 minutes counts!'),
(29, 'Small pockets add up.'),
(30, '30-60 minutes is great!'),
(30, 'An hour to yourself? Winning.'),
(31, '1-2 hours is luxurious.'),
(31, 'You prioritize yourself. Love it.'),
(32, '2+ hours? Teach us your ways!'),
(32, 'This is how you thrive.');

-- mental_planning comments (ids 33-35)
INSERT INTO comments_pool (answer_option_id, comment_text) VALUES
(33, 'You''re the family CEO. Can you share?'),
(33, 'That''s heavy mental load.'),
(33, 'Planning everything is exhausting.'),
(34, 'Teamwork makes the dream work!'),
(34, 'Shared planning = shared sanity.'),
(34, 'Love to see partnership.'),
(35, 'Lucky you! Partner handles it.'),
(35, 'That''s true partnership.');

-- mental_emotional comments (ids 36-38)
INSERT INTO comments_pool (answer_option_id, comment_text) VALUES
(36, 'Emotional labor is real work.'),
(36, 'Being the emotional center is draining.'),
(36, 'Who holds YOU?'),
(37, 'Shared emotional load = healthy family.'),
(37, 'You''re in this together.'),
(38, 'Partner carries emotions? Beautiful.'),
(38, 'Emotional support matters.');

-- mental_household comments (ids 39-41)
INSERT INTO comments_pool (answer_option_id, comment_text) VALUES
(39, 'Tracking household needs is invisible work.'),
(39, 'The mental load of "we''re out of milk" is real.'),
(40, 'Shared household tracking is ideal.'),
(40, 'You both know what''s needed.'),
(41, 'Partner handles supplies? Amazing.'),
(41, 'Less mental clutter for you.');

-- me_time_quality comments (ids 42-45)
INSERT INTO comments_pool (answer_option_id, comment_text) VALUES
(42, 'Interrupted time isn''t restorative.'),
(42, 'Can you protect your me-time?'),
(43, 'Sometimes interrupted is okay.'),
(43, 'Fair quality is a start.'),
(44, 'Good quality me-time matters.'),
(44, 'You''re learning to protect it.'),
(45, 'Excellent! This is self-care.'),
(45, 'Restorative time = better parent.');

-- weekend_rest comments (ids 46-49)
INSERT INTO comments_pool (answer_option_id, comment_text) VALUES
(46, 'Weekends shouldn''t feel like weekdays.'),
(46, 'Can you carve out Sunday rest?'),
(47, 'Somewhat restful is progress.'),
(47, 'Better than nothing!'),
(48, 'Restful weekends recharge you.'),
(48, 'This is the goal.'),
(49, 'Very restful? You''ve cracked the code.'),
(49, 'Weekend reset is powerful.');

-- break_frequency comments (ids 50-53)
INSERT INTO comments_pool (answer_option_id, comment_text) VALUES
(50, 'No breaks leads to burnout.'),
(50, 'Even 2 minutes helps.'),
(51, '1-2 breaks is standard.'),
(51, 'Can you add one more?'),
(52, '3-4 breaks is healthy.'),
(52, 'You''re pacing yourself well.'),
(53, 'Regular breaks = sustainable work.'),
(53, 'This is how professionals do it.');

-- 4. VERIFY EVERYTHING
SELECT 'QUESTIONS' as type, COUNT(*) as count FROM questions
UNION ALL
SELECT 'ANSWER OPTIONS', COUNT(*) FROM answer_options
UNION ALL
SELECT 'COMMENTS', COUNT(*) FROM comments_pool;

-- Show sample of each
SELECT q.question_key, a.display_text, c.comment_text
FROM comments_pool c
JOIN answer_options a ON c.answer_option_id = a.id
JOIN questions q ON a.question_id = q.id
LIMIT 20;