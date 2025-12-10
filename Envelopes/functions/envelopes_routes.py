from functions import db_utils, queries

from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user

def envelopes_home(budget_id):
    return render_template('envelopes_home.html')

def envelopes_view():
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    # first get the budget id
    cur.execute(queries.GET_DEFAULT_BUDGET_BY_USER_ID, (current_user.id,))
    budget_id = cur.fetchone()[0]

    # now get envelopes with transaction fields (must include envelope_id)
    cur.execute(queries.GET_ENVELOPES_AND_TRANSACTION_FIELDS_BY_BUDGET_ID, (budget_id,))
    rows = cur.fetchall()

    envelopes = {}

    for envelope_id, envelope_name, form_order, field_name, field_type, is_required in rows:
        if envelope_name not in envelopes:
            envelopes[envelope_name] = {
                "id": envelope_id,
                "details": []
            }

        # append field
        envelopes[envelope_name]["details"].append(
            (form_order, field_name, field_type, is_required)
        )

    conn.close()
    return render_template('envelopes_view.html', envelopes=envelopes)


def envelopes_create():
    if request.method == 'POST':
        name = request.form.get('envelope_name')

        conn = db_utils.get_db_connection()
        cur = conn.cursor()
        
        #get default budget
        cur.execute(queries.GET_DEFAULT_BUDGET_BY_USER_ID,(current_user.id,))
        budget_id = cur.fetchone()

        #check if there is already an envelope in this budget with this name
        cur.execute(queries.GET_ENVELOPE_BY_NAME_AND_BUDGET_ID, (name,budget_id))
        exists = cur.fetchone()
        
        # if not then insert
        if exists == None:
            cur.execute(queries.INSERT_INTO_ENVELOPES_RETURN_PK, (budget_id,name))
            pk_id = cur.fetchone()[0]

            #insert this envelope's columns into the column tracking table
            trackers = request.form.getlist('trackers[]')
            types = request.form.getlist('types[]')
            required_indices = request.form.getlist('required[]')
            required_indices = [i for i in required_indices]

            form_order_counter = 1
            for idx, (t_name, t_type) in enumerate(zip(trackers, types)):
                print(idx)
                is_required = idx in required_indices
                cur.execute(queries.INSERT_INTO_ENVELOPE_TRANSACTION_FIELDS, (budget_id,pk_id,form_order_counter,t_name,t_type,is_required))
                #increase the form order value
                form_order_counter+=1
            
            conn.commit()
            cur.close()
            conn.close()
        else:
            flash(f"{name} envelope already exists")
            return redirect(url_for("envelopes_create_route"))
        return redirect(url_for("envelopes_home_route"))

    # Initial page load
    return render_template("envelopes_create.html", num_trackers=1)

def envelopes_edit():
    return render_template("envelopes_edit.html")