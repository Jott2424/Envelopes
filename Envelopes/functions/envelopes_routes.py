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
    if request.method == "POST":
        name = request.form.get("envelope_name", "").strip()

        if not name:
            flash("Envelope name is required.", "error")
            return redirect(request.url)

        conn = db_utils.get_db_connection()
        cur = conn.cursor()

        # Check duplicate
        cur.execute(
            queries.GET_ENVELOPE_BY_NAME_AND_BUDGET_ID,
            (name, budget_id)
        )

        if cur.fetchone():
            flash(f"Envelope '{name}' already exists in this budget.", "error")
            cur.close()
            conn.close()
            return redirect(request.url)

        # Insert envelope
        cur.execute(
            queries.INSERT_INTO_ENVELOPES_RETURN_PK,
            (budget_id, name)
        )
        pk_envelope_id = cur.fetchone()[0]

        # Collect trackers
        trackers = request.form.getlist("trackers[]")
        types = request.form.getlist("types[]")
        required_indices = [int(i) for i in request.form.getlist("required[]")]

        form_order = 1

        for idx, (t_name, t_type) in enumerate(zip(trackers, types)):
            t_name = t_name.strip()

            # Skip empty optional rows
            if not t_name:
                continue

            is_required = idx in required_indices

            cur.execute(
                queries.INSERT_INTO_ENVELOPE_TRANSACTION_FIELDS,
                (
                    pk_envelope_id,
                    form_order,
                    t_name,
                    t_type,
                    is_required
                )
            )

            form_order += 1

        conn.commit()
        cur.close()
        conn.close()

        flash("Envelope created successfully!", "success")
        return redirect(
            url_for("envelopes_home_route", budget_id=budget_id)
        )

    # GET
    return render_template(
        "envelopes_create.html",
        budget_id=budget_id
    )


def envelopes_edit(budget_id, envelope_id):
    if request.method == "GET":
        conn = db_utils.get_db_connection()
        cur = conn.cursor()

        cur.execute(
            queries.GET_ENVELOPE_NAME_BY_PK,(envelope_id,))
        envelope_name = cur.fetchone()[0]
        print(envelope_name)

        cur.execute(
            queries.GET_ENVELOPE_NAME_AND_TRANSACTION_FIELDS_EXCLUDING_AMOUNT_BY_BUDGET_AND_ENVELOPE_ID,(budget_id, envelope_id))
        rows = cur.fetchall()


        fields = []
        for r in rows:
            fields.append({
                "envelope_name": envelope_name,
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
            envelope_name=envelope_name,
            fields=fields
        )        

    if request.method == "POST":

        # -------------------------
        # Check if delete button was clicked
        # -------------------------
        if request.form.get("delete_envelope"):
            conn = db_utils.get_db_connection()
            cur = conn.cursor()

            # Delete transactions
            cur.execute(
                queries.DROP_FROM_TRANSACTIONS_BY_ENVELOPES_ID,
                (envelope_id,)
            )

            # Delete all fields
            cur.execute(
                queries.DROP_FROM_ENVELOPE_TRANSACTION_FIELDS_BY_ENVELOPES_ID,
                (envelope_id,)
            )

            # Delete envelope itself
            cur.execute(
                queries.DROP_FROM_ENVELOPES_BY_ENVELOPES_ID,
                (envelope_id,)
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
            queries.DROP_FROM_ENVELOPE_TRANSACTION_FIELDS_BY_ENVELOPES_ID,
            (envelope_id,)
        )

        # Insert each new field
        for i in range(len(trackers)):
            field_name = trackers[i]
            field_type = types[i]
            is_required = str(i) in required_list

            cur.execute(
                queries.INSERT_INTO_ENVELOPE_TRANSACTION_FIELDS,
                (envelope_id, i, field_name, field_type, is_required)
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
