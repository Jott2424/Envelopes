from functions import db_utils, queries

from flask import render_template, request, redirect, url_for
from flask_login import current_user
from datetime import date, datetime, timedelta
import json
import calendar
from calendar import monthrange

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

    today = date.today()
    year = int(request.args.get('year', today.year))
    month = int(request.args.get('month', today.month))

    # --- Month boundaries ---
    first_of_month = date(year, month, 1)
    last_of_month = date(year, month, monthrange(year, month)[1])

    # Align to Sunday–Saturday
    first_week_start = first_of_month - timedelta(
        days=(first_of_month.weekday() + 1) % 7
    )
    last_week_end = last_of_month + timedelta(
        days=(6 - ((last_of_month.weekday() + 1) % 7))
    )

    # --- Get selected envelopes ---
    cur.execute("""
        SELECT details
        FROM user_settings
        WHERE fk_users_id = %s AND setting = 'default_ledger_envelopes'
    """, (current_user.id,))
    row = cur.fetchone()

    selected_envelopes = []
    if row and row[0] and "envelope_ids" in row[0]:
        selected_envelopes = [int(e) for e in row[0]["envelope_ids"]]

    if not selected_envelopes:
        cur.execute(queries.GET_ENVELOPES_BY_BUDGET_ID, (budget_id,))
        selected_envelopes = [r[0] for r in cur.fetchall()]

    # --- Historical balances BEFORE visible weeks ---
    cur.execute(
        queries.GET_LEDGER_BALANCES_BEFORE_DATE,
        (budget_id, first_week_start)
    )
    rows = cur.fetchall()

    running_totals = {eid: 0 for eid in selected_envelopes}
    for envelope_id, balance in rows:
        if envelope_id in running_totals:
            running_totals[envelope_id] = balance or 0

    # --- Weekly sums ---
    cur.execute(
        queries.GET_LEDGER_WEEKLY_SUMS,
        (budget_id, first_week_start, last_week_end)
    )
    transactions = cur.fetchall()

    def majority_month(week_label):
        start_str, _ = week_label.split(' - ')
        start = date.fromisoformat(start_str)
        days = [start + timedelta(days=i) for i in range(7)]
        return max(
            set(d.month for d in days),
            key=lambda m: sum(1 for d in days if d.month == m)
        )

    ledger = {}

    for week_label, envelope_id, debit, credit in transactions:
        if majority_month(week_label) != month:
            continue
        if envelope_id not in selected_envelopes:
            continue

        if week_label not in ledger:
            ledger[week_label] = {}

        running_totals[envelope_id] += (credit or 0) - (debit or 0)

        ledger[week_label][envelope_id] = {
            "debit": debit or 0,
            "credit": credit or 0,
            "running_total": running_totals[envelope_id]
        }

    # --- Envelope names ---
    cur.execute(
        queries.GET_ENVELOPE_NAMES_BY_ID,
        (selected_envelopes,)
    )
    envelopes = {eid: name for eid, name in cur.fetchall()}

    cur.close()
    conn.close()

    return render_template(
        "ledger_overview.html",
        budget_id=budget_id,
        ledger=ledger,
        envelopes=envelopes,
        year=year,
        month=month,
        current_year=today.year
    )




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

        cur.execute("""DELETE FROM user_settings WHERE setting = 'default_ledger_envelopes' and fk_users_id = %s""",(current_user.id,))

        # Upsert
        cur.execute("""
            INSERT INTO user_settings(fk_users_id, setting, details)
            VALUES(%s, 'default_ledger_envelopes', %s)
        """, (current_user.id, json.dumps(details)))
        conn.commit()
        return redirect(url_for("ledger_overview_route", budget_id=budget_id))

    cur.close()
    conn.close()
    return render_template("ledger_settings.html", budget_id=budget_id, envelopes=envelopes, selected=selected)
