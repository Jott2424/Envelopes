from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT
from functions import db_utils

from flask import render_template, redirect, url_for, request
from flask_login import current_user

def getting_started_home():
    return render_template('getting_started_home.html')

def getting_started_create_budget_route():
    return render_template('getting_started_create_budget.html')

def getting_started_create_budget_route():
    if request.method == 'POST':

        budget_name = request.form.get('budget_name')
        print(budget_name)

        conn = db_utils.get_db_connection()
        cur = conn.cursor()

        cur.execute("""
                INSERT INTO budgets (name)
                VALUES (%s)
            """, (budget_name,))

        cur.execute("""
            SELECT pk_budgets_id
            FROM budgets WHERE name = %s
            """, (budget_name,))
        pk = cur.fetchone()

        cur.execute("""
                INSERT INTO user_default_budget (fk_budgets_id, fk_users_id)
                VALUES (%s, %s)
            """, (pk, current_user.id))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('home_route'))
    
    else:
        return render_template('getting_started_create_budget.html')