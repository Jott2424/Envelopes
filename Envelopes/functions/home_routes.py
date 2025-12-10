from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT
from functions import db_utils, queries

from flask import render_template, redirect, url_for
from flask_login import current_user

def home():
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    # Query budgets for the current user
    cur.execute(queries.GET_DEFAULT_BUDGET_BY_USER_ID, (current_user.id,))

    default_budget = cur.fetchone()[0]
    cur.close()
    conn.close()

    if default_budget == None or not default_budget:
        # No budgets found, redirect or prompt
        return redirect(url_for('getting_started_create_budget_route'))

    return render_template('home.html', user=current_user, budget_id=default_budget)