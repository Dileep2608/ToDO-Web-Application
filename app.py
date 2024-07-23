from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2
from psycopg2 import sql
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_generated_secret_key')  # Get from environment or use default

def connect_to_db():
    conn = psycopg2.connect(
        dbname='todo_app',
        user='postgres',
        password='dileep',
        host='localhost'
    )
    return conn

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def handle_login():
    user_id = request.form['userId']
    password = request.form['password']

    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("SELECT user_name, user_id FROM users WHERE user_id = %s AND password = %s", (user_id, password))
    user = cursor.fetchone()

    conn.close()

    if user:
        session['user_name'] = user[0]
        session['user_id'] = user[1]
        return redirect(url_for('main'))
    else:
        return "Invalid credentials, please go back and try again."

@app.route('/createaccount', methods=['POST'])
def handle_signup():
    user_name = request.form['username']
    password = request.form['password']

    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (user_name, password) VALUES (%s, %s)", (user_name, password))
    conn.commit()
    conn.close()
    

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_name = %s AND password = %s", (user_name, password))
    user = cursor.fetchone()
    conn.close()

    return "New account for {} created sucessfully. Your user id is {} \n Login to continue..".format(user_name,user[0])
    
@app.route('/main')
def main():
    if 'user_name' in session and 'user_id' in session:
        user_name = session['user_name']
        user_id = session['user_id']

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.task_id, t.task, t.create_date, t.status, 
            st.subtask_id, st.subtask, st.status 
            FROM todo_list t 
            LEFT JOIN sub_task st ON t.task_id = st.task_id 
            WHERE t.user_id = %s 
            ORDER BY t.create_date DESC, st.subtask_id ASC
        """, (user_id,))
        tasks = cursor.fetchall()
        conn.close()

        tasks_dict = {}
        for task in tasks:
            if task[0] not in tasks_dict:
                tasks_dict[task[0]] = {
                    'task_id': task[0],
                    'task': task[1],
                    'create_date': task[2],
                    'status': task[3],
                    'subtasks': []
                }
            if task[4]:
                tasks_dict[task[0]]['subtasks'].append({
                    'subtask_id': task[4],
                    'subtask': task[5],
                    'status': task[6]
                })
        
        return render_template('main.html', user_name=user_name, tasks=tasks_dict.values())
    else:
        return redirect(url_for('login'))

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    task = request.form['task']

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO todo_list (task, create_date, status, user_id) VALUES 
                   (%s, %s, %s, (SELECT user_id FROM users WHERE user_id = %s))''',(task, datetime.now(), 'incomplete', user_id))
    conn.commit()
    conn.close()

    return redirect(url_for('main'))

@app.route('/edit_task', methods=['POST'])
def edit_task():
    task_id = request.form['task_id']
    new_task = request.form['new_task']

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE todo_list SET task = %s WHERE task_id = %s", (new_task, task_id))
    conn.commit()
    conn.close()

    return jsonify(success=True)

@app.route('/delete_task', methods=['POST'])
def delete_task():
    task_id = request.form['task_id']

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todo_list WHERE task_id = %s", (task_id,))
    cursor.execute("DELETE FROM sub_task WHERE task_id = %s", (task_id,))
    conn.commit()
    conn.close()

    return jsonify(success=True)

@app.route('/add_subtask', methods=['POST'])
def add_subtask():
    task_id = request.form['task_id']
    subtask = request.form['subtask']

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sub_task (task_id, subtask, status) VALUES (%s, %s, %s)",(task_id, subtask, 'incomplete'))
    conn.commit()
    conn.close()

    return jsonify(success=True)

@app.route('/edit_subtask', methods=['POST'])
def edit_subtask():
    subtask_id = request.form['subtask_id']
    new_subtask = request.form['new_subtask']

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE sub_task SET subtask = %s WHERE subtask_id = %s", (new_subtask, subtask_id))
    conn.commit()
    conn.close()

    return jsonify(success=True)

@app.route('/delete_subtask', methods=['POST'])
def delete_subtask():
    subtask_id = request.form['subtask_id']

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sub_task WHERE subtask_id = %s", (subtask_id,))
    conn.commit()
    conn.close()

    return jsonify(success=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
