from functions import db_utils, queries

from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user

def envelopes_home(budget_id):
    return render_template('envelopes_home.html', budget_id=budget_id)

def envelopes_view(budget_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

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
    
    return render_template('envelopes_view.html', envelopes=envelopes, budget_id=budget_id)


def envelopes_create(budget_id):
    if request.method == 'POST':
        name = request.form.get('envelope_name')

        conn = db_utils.get_db_connection()
        cur = conn.cursor()

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
            return redirect(url_for("envelopes_create_route", budget_id=budget_id))
        return redirect(url_for("envelopes_home_route", budget_id=budget_id))

    # Initial page load
    return render_template("envelopes_create.html", num_trackers=1, budget_id=budget_id)

def envelopes_edit(budget_id, envelope_id):
    if request.method == "GET":
        conn = db_utils.get_db_connection()
        cur = conn.cursor()

        cur.execute(
            queries.GET_ENVELOPE_NAME_AND_TRANSACTION_FIELDS_BY_BUDGET_AND_ENVELOPE_ID,
            (budget_id, envelope_id)
        )
        rows = cur.fetchall()

        fields = []
        for r in rows:
            fields.append({
                "envelope_name": r[0],
                "id": r[1],
                "budget_id": r[2],
                "envelope_id": r[3],
                "form_order": r[4],
                "field_name": r[5],
                "field_type": r[6],
                "is_required": r[7]
            })

        cur.close()
        conn.close()

        return render_template(
            "envelopes_edit.html",
            budget_id=budget_id,
            envelope_id=envelope_id,
            fields=fields
        )        

    if request.method == "POST":

        # -------------------------
        # Check if delete button was clicked
        # -------------------------
        if request.form.get("delete_envelope"):
            conn = db_utils.get_db_connection()
            cur = conn.cursor()

            # Delete all fields
            cur.execute(
                queries.DROP_FROM_ENVELOPE_TRANSACTION_FIELDS_BY_BUDGETS_AND_ENVELOPES_ID,
                (budget_id, envelope_id)
            )

            # Delete transactions (if you track them)
            cur.execute(
                queries.DROP_FROM_TRANSACTIONS_BY_BUDGETS_AND_ENVELOPES_ID,
                (envelope_id, budget_id)
            )

            # Delete envelope itself
            cur.execute(
                queries.DROP_FROM_ENVELOPES_BY_BUDGETS_AND_ENVELOPES_ID,
                (envelope_id, budget_id)
            )

            conn.commit()
            cur.close()
            conn.close()

            flash("Envelope deleted successfully!", "success")
            return redirect(url_for("envelopes_home_route", budget_id=budget_id))

        # -------------------------
        # Otherwise, normal save/update logic
        # -------------------------
        envelope_name = request.form.get("envelope_name")
        trackers = request.form.getlist("trackers[]")
        types = request.form.getlist("types[]")
        required_list = request.form.getlist("required[]")  # indexes only, ex: ["0", "2"]

        conn = db_utils.get_db_connection()
        cur = conn.cursor()

        # Update envelope name
        cur.execute(
            queries.UPDATE_ENVELOPES_BY_ENVELOPES_ID,
            (envelope_name, envelope_id)
        )

        # Delete all old fields
        cur.execute(
            queries.DROP_FROM_ENVELOPE_TRANSACTION_FIELDS_BY_BUDGETS_AND_ENVELOPES_ID,
            (budget_id, envelope_id)
        )

        # Insert each new field
        for i in range(len(trackers)):
            field_name = trackers[i]
            field_type = types[i]
            is_required = str(i) in required_list

            cur.execute(
                queries.INSERT_INTO_ENVELOPE_TRANSACTION_FIELDS,
                (budget_id, envelope_id, i, field_name, field_type, is_required)
            )

        conn.commit()
        cur.close()
        conn.close()

        flash("Envelope updated successfully!", "success")
        return redirect(url_for("envelopes_home_route", budget_id=budget_id))


def envelopes_delete(budget_id, envelope_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    # Delete all fields
    cur.execute(queries.DROP_FROM_ENVELOPE_TRANSACTION_FIELDS_BY_BUDGETS_AND_ENVELOPES_ID,(budget_id, envelope_id))
    print(queries.DROP_FROM_ENVELOPE_TRANSACTION_FIELDS_BY_BUDGETS_AND_ENVELOPES_ID)
    # Delete transactions
    
    cur.execute(queries.DROP_FROM_TRANSACTIONS_BY_BUDGETS_AND_ENVELOPES_ID,(envelope_id, budget_id))

    # Delete envelope itself
    cur.execute(queries.DROP_FROM_ENVELOPES_BY_BUDGETS_AND_ENVELOPES_ID,(envelope_id, budget_id))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("envelopes_home_route", budget_id=budget_id))
