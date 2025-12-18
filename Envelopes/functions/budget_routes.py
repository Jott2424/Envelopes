from functions import db_utils, queries

from flask import render_template, request, redirect, url_for
from flask_login import current_user
from datetime import date, datetime
import json
import calendar

def budget_home(budget_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    #confirm this user has access to this budget
    cur.execute(queries.GET_USER_ALLOWED_BUDGETS_BY_USER_ID, (current_user.id,))

    authorized = cur.fetchone()[0]
    if not authorized:
        return "Unauthorized", 403

    conn.close()

    # pass budget_id into template
    return render_template('budget_home.html', budget_id=budget_id)

def budget_create(budget_id):
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
    return render_template('budget_create.html', budget_id=budget_id)

def budget_select_default(budget_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        print('post!')
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

        return redirect(url_for('budget_home_route', budget_id = selected_budget_id))

    # GET request – show budget selection
    cur.execute(queries.GET_BUDGET_NAME_BY_BUDGET_USERS, (current_user.id,))
    budgets = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('budget_select_default.html', budgets=budgets, budget_id=budget_id)

def budget_invite_users(budget_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        selected_user_id = request.form.get('selected_user')
        if not selected_user_id:
            return "No user selected", 400

        # Check if the selected user already has a default budget
        cur.execute(queries.GET_DEFAULT_BUDGET_BY_USER_ID, (selected_user_id,))
        try:
            existing = cur.fetchone()[0]
        except:
            existing = None

        if existing != None:
            # Update existing record
            cur.execute(queries.UPDATE_USER_DEFAULT_BUDGET_BY_USER_ID, (budget_id, selected_user_id))
        else:
            # Insert new default record
            cur.execute(queries.INSERT_INTO_USER_DEFAULT_BUDGETS, (selected_user_id, budget_id))
        
        #insert user to allowed budgets table
        cur.execute(queries.INSERT_INTO_BUDGET_USERS, (budget_id, selected_user_id))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('budget_home_route', budget_id = budget_id))

    # GET request – show user selection
    # Get the id of the current budget
    cur.execute(queries.GET_DEFAULT_BUDGET_BY_USER_ID, (current_user.id,))
    current_budget = cur.fetchone()[0]

    cur.execute(queries.GET_USERS_NOT_ALREADY_IN_BUDGET_USERS_BY_USER_ID, (current_user.id,current_budget))
    users = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('budget_invite_users.html', users=users, budget_id=budget_id)

def budget_settings(budget_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    #check for default budget
    default_budget = budget_id

    if default_budget:
        return render_template('budget_settings.html', budget_id = budget_id)
    else:
        return render_template('budget_select_default.html')

def ledger_overview(budget_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    # Get user-selected year/month
    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))

    # Get user-selected envelopes (from user_settings)
    cur.execute("""
        SELECT details
        FROM user_settings
        WHERE fk_users_id = %s AND setting='ledger_default_envelopes'
    """, (current_user.id,))
    row = cur.fetchone()
    selected_envelopes = row[0] if row else None  # list of envelope ids
    selected_envelopes = selected_envelopes or []

    # Get all envelopes in budget if user has no default selection
    if not selected_envelopes:
        cur.execute("SELECT pk_envelopes_id, name FROM envelopes WHERE fk_budgets_id=%s", (budget_id,))
        selected_envelopes = [r[0] for r in cur.fetchall()]

    # Query transactions grouped by week
    cur.execute(queries.GET_LEDGER_WEEKLY_SUMS, (
    budget_id,  # for receipts filter
    year, month,  # first %s-%s-01
    year, month   # second %s-%s-01
    ))
    transactions = cur.fetchall()  # see query below

    # Prepare data structure: {week_label: {envelope_id: {'debit': , 'credit': , 'running_total': } } }
    ledger = {}
    running_totals = {eid: 0 for eid in selected_envelopes}

    for week_label, envelope_id, debit, credit in transactions:
        if envelope_id not in selected_envelopes:
            continue
        if week_label not in ledger:
            ledger[week_label] = {}
        ledger[week_label][envelope_id] = {
            'debit': debit,
            'credit': credit,
            'running_total': running_totals[envelope_id] + credit - debit
        }
        running_totals[envelope_id] += credit - debit

    # Sort envelopes by name
    print(selected_envelopes)
    cur.execute(queries.GET_ENVELOPE_NAMES_BY_ID, (selected_envelopes,))
    rows = cur.fetchall()
    cur_envelopes = {eid: name for eid, name in rows}

    cur.close()
    conn.close()

    return render_template("ledger_overview.html",
                        budget_id=budget_id,
                        year=year,
                        month=month,
                        current_year=today.year,  # <--- add this
                        envelopes=cur_envelopes,
                        ledger=ledger)



def ledger_settings(budget_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT pk_envelopes_id, name FROM envelopes WHERE fk_budgets_id=%s", (budget_id,))
    envelopes = cur.fetchall()

    # Load current selection
    cur.execute("""
        SELECT details->'envelope_ids' AS envelope_ids
        FROM user_settings
        WHERE fk_users_id=%s AND setting='default_ledger_envelopes'
    """, (current_user.id,))
    row = cur.fetchone()
    selected = [int(e) for e in row[0]] if row and row[0] else []

    if request.method=="POST":
        selected_ids = request.form.getlist("envelopes")
        details = {"envelope_ids": [int(e) for e in selected_ids]}
        # Upsert
        cur.execute("""
            INSERT INTO user_settings(fk_users_id, setting, details)
            VALUES(%s, 'default_ledger_envelopes', %s)
            ON CONFLICT (fk_users_id, setting)
            DO UPDATE SET details=EXCLUDED.details
        """, (current_user.id, json.dumps(details)))
        conn.commit()
        return redirect(url_for("ledger_overview_route", budget_id=budget_id))

    cur.close()
    conn.close()
    return render_template("ledger_settings.html", budget_id=budget_id, envelopes=envelopes, selected=selected)
