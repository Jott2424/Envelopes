from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT
from functions import db_utils

from flask import render_template, redirect, url_for
from flask_login import current_user

def home():
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    # Query budgets for the current user
    cur.execute("""
        SELECT *
        FROM budgets
    """)

    budgets = cur.fetchall()
    cur.close()
    conn.close()

    if not budgets:
        # No budgets found, redirect or prompt
        return redirect(url_for('getting_started_create_budget_route'))

    return render_template('home.html', user=current_user)