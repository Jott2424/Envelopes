from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT
from functions import db_utils, queries

from flask import render_template, redirect, url_for, request
from flask_login import current_user

def getting_started_home():
    return render_template('getting_started_home.html')

def getting_started_create_budget_route():
    return render_template('getting_started_create_budget.html')

def getting_started_create_budget_route():
    if request.method == 'POST':

        budget_name = request.form.get('budget_name')

        conn = db_utils.get_db_connection()
        cur = conn.cursor()

        #insert new budget to budgets and get ID
        cur.execute(queries.INSERT_INTO_BUDGETS_RETURN_PK, (budget_name,))
        pk = cur.fetchone()[0]
        
        #insert new budget to user default budgets
        cur.execute(queries.INSERT_INTO_USER_DEFAULT_BUDGETS, (current_user.id, pk))

        #insert new budget to budgets_users (table of who is allowed to access which budgets)
        cur.execute(queries.INSERT_INTO_BUDGET_USERS, (pk, current_user.id))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('home_route', budget_id=pk))
    
    else:
        return render_template('getting_started_create_budget.html')