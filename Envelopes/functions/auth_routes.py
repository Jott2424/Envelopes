from classes.user import User

from flask import request, render_template, redirect, url_for
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from functions import db_utils

def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = db_utils.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT pk_users_id, name, password FROM users WHERE name = %s", (username,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            user_id, db_username, db_password_hash = row
            if check_password_hash(db_password_hash, password):
                user = User(user_id, db_username)
                login_user(user)
                return redirect(url_for('home_route'))
        return "Invalid credentials", 401
    return render_template('login.html')

def logout():
    logout_user()
    return redirect(url_for('login'))

def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_hash = generate_password_hash(password)

        conn = db_utils.get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, password) VALUES (%s, %s) RETURNING pk_users_id",
                    (username, password_hash))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        user = User(user_id, username)
        login_user(user)
        return redirect(url_for('home_route'))

    return render_template('register.html')