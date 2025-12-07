from functions import db_utils

from flask import render_template
from flask_login import current_user

def budget_home():
    return render_template('budget_home.html')

def budget_create():
    return render_template('budget_create.html')

def budget_select():
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    # Get budgets for the current user
    cur.execute("""
        SELECT b.name
        FROM budgets b
        JOIN budget_users bu ON b.pk_budgets_id = bu.fk_budgets_id
        WHERE bu.fk_users_id = %s
    """, (current_user.id,))

    budgets = cur.fetchall()  # returns a list of tuples
    cur.close()
    conn.close()

    # Convert list of tuples to list of names
    budget_names = [b[0] for b in budgets]

    return render_template('budget_select.html', budgets=budget_names)
    