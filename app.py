from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from datetime import date, datetime

app = Flask(__name__, static_folder='static', template_folder='templates')

def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            due_time TEXT,
            completed BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def serve_index():
    return send_from_directory('templates', 'index.html')

@app.route('/api/tasks')
def get_tasks():
    conn = get_db_connection()
    c = conn.cursor()
    today = date.today().isoformat()

    c.execute("SELECT * FROM tasks WHERE completed=0 AND due_date=? ORDER BY due_time ASC", (today,))
    today_tasks = [dict(row) for row in c.fetchall()]

    c.execute("SELECT * FROM tasks WHERE completed=0 AND due_date > ? ORDER BY due_date ASC, due_time ASC", (today,))
    upcoming_tasks = [dict(row) for row in c.fetchall()]

    c.execute("SELECT * FROM tasks WHERE completed=1 ORDER BY id DESC")
    completed_tasks = [dict(row) for row in c.fetchall()]

    conn.close()
    return jsonify({
        "today": today_tasks,
        "upcoming": upcoming_tasks,
        "completed": completed_tasks
    })

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    due_date_raw = request.form.get('due_date')
    due_time = request.form.get('due_time')

    try:
        due_date = datetime.strptime(due_date_raw, '%Y-%m-%d').date().isoformat()
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO tasks (title, description, due_date, due_time)
        VALUES (?, ?, ?, ?)
    """, (title, description, due_date, due_time))
    conn.commit()
    conn.close()
    return ('', 204)

@app.route('/complete/<int:task_id>', methods=['GET'])
def complete_task(task_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return ('', 204)

@app.route('/delete/<int:task_id>', methods=['GET'])
def delete_task(task_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return ('   ', 204) 

if __name__ == '__main__':
    init_db()
    app.run(debug=True)