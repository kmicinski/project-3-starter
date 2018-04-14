# Starter code for 311 Project 3I.
#
# First, install flask
# pip install flask
#
# Then, to initialize the database, run the following:
#     python app.py init
# Then run the app itself as:
#     python app.py
#
# Largely taken from https://gist.github.com/hackeris/fa2bfd20e6bec08c8d5240efe87d4687
import os
import sqlite3
import sys

from flask import Flask
from flask import redirect
from flask import jsonify
from flask import request
from flask import session
from flask import render_template
from flask import send_from_directory
from jinja2 import Template

app = Flask(__name__)

app.secret_key = 'schrodinger cat'

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def connect_db():
    return sqlite3.connect(DATABASE_PATH)

def create_tables():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
            CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(32),
            password VARCHAR(32)
            )''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        content TEXT,
        FOREIGN KEY (`user_id`) REFERENCES `user`(`id`)
        )''')
    conn.commit()
    conn.close()

def init_data():
    users = [
        ('user1', '123456'),
        ('user2', '123456')
    ]
    lines = [
        (1, 'First Post'),
        (1, 'Another Post'),
        (2, 'Here\'s my third post'),
        (2, 'Last post here.')
    ]
    conn = connect_db()
    cur = conn.cursor()
    cur.executemany('INSERT INTO `user` VALUES(NULL,?,?)', users)
    cur.executemany('INSERT INTO `chats` VALUES(NULL,?,?)', lines)
    conn.commit()
    conn.close()

def init():
    create_tables()
    init_data()

def get_user_from_username_and_password(username, password):
    conn = connect_db()
    cur = conn.cursor()
    print(username,password)
    cur.execute('SELECT id, username FROM `user` WHERE username=\'%s\' AND password=\'%s\'' % (username, password))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    print(row)
    return {'id': row[0], 'username': row[1]} if row is not None else None

def create_user(username, password):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO `user` VALUES(NULL,?,?);', (username, password))
    row = cur.fetchone()
    conn.commit()
    conn.close()
    return {'id': row[0], 'username': row[1]} if row is not None else None

def get_user_from_id(uid):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, username FROM `user` WHERE id=%d' % uid)
    row = cur.fetchone()
    conn.commit()
    conn.close()
    return {'id': row[0], 'username': row[1]}

def create_chat(uid, content):
    conn = connect_db()
    cur = conn.cursor()
    # ...
    stmt = 'INSERT INTO `chats` VALUES (NULL,' + str(uid) + ",\'" + content + '\')'
    print(stmt)
    cur.executescript(stmt)
    row = cur.fetchone()
    conn.commit()
    conn.close()
    return row

def get_chats(n):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, user_id, content FROM `chats` WHERE id>=%d ORDER BY id ASC' % n)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return list(map((lambda row: {'id': row[0],
                       'user_id': row[1],
                       'content': row[2],
                       'username': get_user_from_id(row[1])['username']}),
                    rows))

def user_delete_chat_of_id(uid, tid):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM `chat` WHERE  user_id=%s AND id=%s' % (uid, tid))
    conn.commit()
    conn.close()

def render_login_page():
    return '''
<div style="width: 500px; margin: 80px auto;">
<center><h1> Welcome to FakeSquirrelChat! </h1></center>
<form method="POST" style="margin: 60px auto; width: 140px;">
    <p>Username: <input name="username" type="text" /></p>
    <p>Password: <input name="password" type="password" /></p>
    <p><input value="Login" type="submit" /></p>
</form>
<a href="/create_account">Create account</a>
</div>
    '''

def render_create_account():
    return '''
<div style="width: 500px; margin: 80px auto;">
<center><h1> Welcome to FakeSquirrelChat! </h1></center>
<p>Select your username and password</p>
<form method="POST" style="margin: 60px auto; width: 140px;">
    <p>Username: <input name="username" type="text" /></p>
    <p>Password: <input name="password" type="password" /></p>
    <p><input value="Login" type="submit" /></p>
</form>
</div>
'''

@app.route('/changepassword/<newpassword>')
def changepassword(newpassword):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('UPDATE `user` SET password=\'%s\' WHERE id=\'%d\'' % (newpassword, session['uid']))
    conn.commit()
    conn.close()
    return "success", 200

@app.route('/getpassword')
def getpassword():
    if 'uid' in session:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT password FROM `user` WHERE id=\'%d\'' % (session['uid']))
        row = cur.fetchone()
        conn.commit()
        conn.close()
        print(row)
        return jsonify({'password': row[0]})
    else:
        return jsonify("Not logged in")

@app.route('/chats', methods=['GET'])
def chats():
    if 'uid' in session:
        return jsonify(get_chats(0))
    else:
        return jsonify("Error: not logged in!")

@app.route('/chats/from/<n>', methods=['GET'])
def chats_from(n):
    if 'uid' in session:
        return jsonify(get_chats(int(n)))
    else:
        return jsonify("Error: not logged in!")

def render_home_page(uid):
    user = get_user_from_id(uid)
    return render_template('chats.html', uid=uid, user=user['username'])

def do_login(user):
    if user is not None:
        session['uid'] = user['id']
        return redirect('/')
    else:
        return redirect('/login')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'GET':
        return render_create_account()
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username,password)
        user = create_user(username, password)
        return do_login(user)

@app.route('/')
def index():
    if 'uid' in session:
        return render_home_page(session['uid'])
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_login_page()
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_from_username_and_password(username, password)
        return do_login(user)

@app.route('/chat', methods=['POST'])
def chat():
    if 'uid' in session:
        uid = session['uid']
        json = request.get_json()
        print(json)
        create_chat(json['uid'], json['content'])
        return "success", 200
    return redirect('/')

@app.route('/chat/<cid>/delete')
def delete_chat(cid):
    user_delete_chat_of_id(session['uid'], cid)
    return redirect('/')

@app.route('/logout')
def logout():
    if 'uid' in session:
        session.pop('uid')
    return redirect('/login')

# Static files
@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def serve_css(path):
    return send_from_directory('css', path)

if len(sys.argv) > 1 and sys.argv[1] == "init":
    init()
    exit(0)

if __name__ == '__main__':
    app.run(debug=True)
