from functions import db_utils, queries

from flask import render_template, request, redirect, url_for
from flask_login import current_user

def budget_home(budget_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    # OPTIONAL: validate this budget belongs to the current user
    cur.execute("""
        SELECT pk_budgets_id 
        FROM budgets_users 
        WHERE fk_users_id = %s AND fk_budgets_id = %s
    """, (current_user.id, budget_id))

    authorized = cur.fetchone()
    if not authorized:
        return "Unauthorized", 403

    conn.close()

    # pass budget_id into template
    return render_template('budget_home.html', budget_id=budget_id)

def budget_create():
    if request.method == 'POST':
        budget_name = request.form.get('budget_name')
        
        conn = db_utils.get_db_connection()
        cur = conn.cursor()

        #insert new budget to budgets and get ID
        cur.execute(queries.INSERT_INTO_BUDGETS_RETURN_PK, (budget_name,))
        pk = cur.fetchone()[0]

        # Check if the user already has a default budget
        cur.execute(queries.GET_DEFAULT_BUDGET_BY_USER_ID, (current_user.id,))
        existing = cur.fetchone()[0]


        if existing:
            # Update existing record
            cur.execute(queries.UPDATE_USER_DEFAULT_BUDGET_BY_USER_ID, (pk, current_user.id))
        else:
            # Insert new default record
            cur.execute(queries.INSERT_INTO_USER_DEFAULT_BUDGETS, (current_user.id, selected_budget_id))

        #insert new budget to budgets_users (table of who is allowed to access which budgets)
        cur.execute(queries.INSERT_INTO_BUDGET_USERS, (pk, current_user.id))

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
        cur.execute(queries.GET_DEFAULT_BUDGET_BY_USER_ID, (current_user.id,))
        
        existing = cur.fetchone()[0]

        if existing:
            # Update existing record
            cur.execute(queries.UPDATE_USER_DEFAULT_BUDGET_BY_USER_ID, (selected_budget_id, current_user.id))
        else:
            # Insert new default record
            cur.execute(queries.INSERT_INTO_USER_DEFAULT_BUDGETS, (current_user.id, selected_budget_id))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('budget_home_route'))

    # GET request – show budget selection
    cur.execute(queries.GET_BUDGET_NAME_BY_BUDGET_USERS, (current_user.id,))
    budgets = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('budget_select_default.html', budgets=budgets)

def budget_invite_users():
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        selected_user_id = request.form.get('selected_user')
        if not selected_user_id:
            return "No user selected", 400
        
        # Get the id of the current budget
        cur.execute(queries.GET_DEFAULT_BUDGET_BY_USER_ID, (current_user.id,))
        current_budget = cur.fetchone()[0]

        # Check if the selected user already has a default budget
        cur.execute(queries.GET_DEFAULT_BUDGET_BY_USER_ID, (selected_user_id,))
        existing = cur.fetchone()[0]

        if existing != None:
            # Update existing record
            cur.execute(queries.UPDATE_USER_DEFAULT_BUDGET_BY_USER_ID, (selected_budget_id, selected_user_id))
        else:
            # Insert new default record
            cur.execute(queries.INSERT_INTO_USER_DEFAULT_BUDGETS, (selected_user_id, current_budget))
        
        #insert user to allowed budgets table
        cur.execute(queries.INSERT_INTO_USER_DEFAULT_BUDGETS, (current_budget, selected_user_id))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('budget_home_route'))

    # GET request – show user selection
    # Get the id of the current budget
    cur.execute(queries.GET_DEFAULT_BUDGET_BY_USER_ID, (current_user.id,))
    current_budget = cur.fetchone()[0]

    cur.execute(queries.GET_USERS_NOT_ALREADY_IN_BUDGET_USERS_BY_USER_ID, (current_user.id,current_budget))
    users = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('budget_invite_users.html', users=users)

def budget_settings():
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    #check for default budget
    cur.execute(queries.GET_DEFAULT_BUDGET_BY_USER_ID, (current_user.id,))
    
    existing = cur.fetchone()[0]

    if existing:
        return render_template('budget_settings.html')
    else:
        return render_template('budget_select_default.html')