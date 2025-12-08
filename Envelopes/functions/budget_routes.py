from functions import db_utils

from flask import render_template, request, redirect, url_for
from flask_login import current_user

def budget_home():
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    #check for default budget
    cur.execute("""
        SELECT pk_user_default_budget_id
        FROM user_default_budget
        WHERE fk_users_id = %s
    """, (current_user.id,))
    
    existing = cur.fetchone()
    print(existing)

    if existing:
        return render_template('budget_home.html')
    else:
        return render_template('budget_select_default.html')

def budget_create():
    if request.method == 'POST':
        budget_name = request.form.get('budget_name')

        conn = db_utils.get_db_connection()
        cur = conn.cursor()
        #insert new budget to budgets
        cur.execute("""
                INSERT INTO budgets (name)
                VALUES (%s)
            """, (budget_name,))
        #get the new budget id
        cur.execute("""
            SELECT pk_budgets_id
            FROM budgets WHERE name = %s
            """, (budget_name,))
        pk = cur.fetchone()
        #insert new budget to user default budgets
        cur.execute("""
                INSERT INTO user_default_budget (fk_budgets_id, fk_users_id)
                VALUES (%s, %s)
            """, (pk, current_user.id))
        #insert new budget to budgets_users (table of who is allowed to access which budgets)
        cur.execute("""
                INSERT INTO budget_users (fk_budgets_id, fk_users_id)
                VALUES (%s, %s)
            """, (pk, current_user.id))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('home_route'))
    return render_template('budget_create.html')

def budget_select_default():
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

    return render_template('budget_select_default.html', budgets=budgets)

def budget_invite_users():
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        selected_user_id = request.form.get('selected_user')
        print(selected_user_id)
        if not selected_user_id:
            return "No user selected", 400
        
        # Get the id of the current budget
        cur.execute("""
            SELECT fk_budgets_id
            FROM user_default_budget
            WHERE fk_users_id = %s
        """, (current_user.id,))
        current_budget = cur.fetchone()

        # Check if the user already has a default budget
        cur.execute("""
            SELECT fk_budgets_id
            FROM user_default_budget
            WHERE fk_users_id = %s
        """, (selected_user_id,))
        existing = cur.fetchone()

        if existing:
            # Update existing record
            cur.execute("""
                UPDATE user_default_budget
                SET fk_budgets_id = %s
                WHERE fk_users_id = %s
            """, (current_budget, selected_user_id))
        else:
            # Insert new default record
            cur.execute("""
                INSERT INTO user_default_budget (fk_users_id, fk_budgets_id)
                VALUES (%s, %s)
            """, (selected_user_id, current_budget))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('budget_home_route'))

    # GET request – show user selection
    cur.execute("""
        SELECT u.pk_users_id, u.name
        FROM users u
        WHERE u.pk_users_id != %s
    """, (current_user.id,))
    users = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('budget_invite_users.html', users=users)