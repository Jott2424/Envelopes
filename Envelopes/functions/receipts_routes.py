from functions import db_utils, queries

from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user

def receipts_home(budget_id):
    return render_template('receipts_home.html', budget_id=budget_id)

def receipts_create(budget_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    cur.execute(queries.GET_ENVELOPES_NAME_AND_TRANSACTION_FIELDS_BY_BUDGET, (budget_id,))
    rows = cur.fetchall()

    envelope_map = {}

    for (
        envelope_name,
        envelope_id,
        form_order,
        field_name,
        field_type,
        is_required
    ) in rows:

        if envelope_id not in envelope_map:
            envelope_map[envelope_id] = {
                "name": envelope_name,
                "fields": []
            }

        envelope_map[envelope_id]["fields"].append({
            "name": field_name,
            "type": field_type,
            "required": bool(is_required),
            "form_order": form_order
        })

    # Sort fields by form_order
    for env in envelope_map.values():
        env["fields"].sort(key=lambda f: f["form_order"])

    if request.method == "POST":
        # handle form submission here
        pass

    return render_template("receipts_create.html",budget_id=budget_id,envelope_map=envelope_map)

def receipts_view(budget_id):
    return render_template('receipts_home.html', budget_id=budget_id)