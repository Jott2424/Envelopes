from functions import db_utils

from flask import render_template, request, redirect, url_for
from flask_login import current_user

def budget_home():
    return render_template('budget_home.html')

def budget_create():
    return render_template('budget_create.html')

def budget_select():
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        selected_budget_id = request.form.get('selected_budget')

        if not selected_budget_id:
            return "No budget selected", 400

        # Check if the user already has a default budget
        cur.execute("""
            SELECT pk_user_default_budget_id
            FROM user_default_budget
            WHERE fk_users_id = %s
        """, (current_user.id,))
        
        existing = cur.fetchone()

        if existing:
            # Update existing record
            cur.execute("""
                UPDATE user_default_budget
                SET fk_budgets_id = %s
                WHERE fk_users_id = %s
            """, (selected_budget_id, current_user.id))
        else:
            # Insert new default record
            cur.execute("""
                INSERT INTO user_default_budget (fk_users_id, fk_budgets_id)
                VALUES (%s, %s)
            """, (current_user.id, selected_budget_id))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('budget_home_route'))

    # GET request – show budget selection
    cur.execute("""
        SELECT b.pk_budgets_id, b.name
        FROM budgets b
        JOIN budget_users bu ON b.pk_budgets_id = bu.fk_budgets_id
        WHERE bu.fk_users_id = %s
    """, (current_user.id,))
    budgets = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('budget_select.html', budgets=budgets)