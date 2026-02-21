import sqlite3

conn = sqlite3.connect('momentum.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=== QUESTIONS ===")
questions = cursor.execute("SELECT id, question_key, question_text FROM questions").fetchall()
for q in questions:
    print(f"{q['id']}: {q['question_key']} - {q['question_text']}")
    
    # Get options for this question
    options = cursor.execute("""
        SELECT id, display_text, value_min, value_max 
        FROM answer_options 
        WHERE question_id = ?
    """, [q['id']]).fetchall()
    
    for opt in options:
        # Count comments for this option
        comment_count = cursor.execute("""
            SELECT COUNT(*) as count FROM comments_pool 
            WHERE answer_option_id = ?
        """, [opt['id']]).fetchone()['count']
        
        print(f"  └─ {opt['display_text']} (value: {opt['value_min']}-{opt['value_max']}) - {comment_count} comments")
    
    print()

print("=== USERS ===")
users = cursor.execute("SELECT id, email, created_at FROM users").fetchall()
for u in users:
    print(f"{u['id']}: {u['email']} - {u['created_at']}")

conn.close()