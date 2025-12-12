from functions import db_utils, queries

from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
import json

def receipts_home(budget_id):
    return render_template('receipts_home.html', budget_id=budget_id)

def receipts_create(budget_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    # -----------------------------------------
    # 1. Load envelope field definitions
    # -----------------------------------------
    cur.execute(queries.GET_ENVELOPES_NAME_AND_TRANSACTION_FIELDS_BY_BUDGET,(budget_id,))
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

    # sort fields by the form order
    for env in envelope_map.values():
        env["fields"].sort(key=lambda f: f["form_order"])

    # -----------------------------------------
    # 2. Get payment sources
    # -----------------------------------------
    cur.execute(queries.GET_PAYMENT_SOURCES_BY_BUDGET_ID, (budget_id,))
    payment_sources = cur.fetchall()

    # -----------------------------------------
    # 3. POST logic
    # -----------------------------------------
    if request.method == "POST":
        payment_source_id = request.form.get("payment_source_id")
        debit_or_credit = request.form.get("debit_or_credit")

        if not payment_source_id or not debit_or_credit:
            flash("You must select a payment source and transaction type.", "error")
            return redirect(request.url)

        # ------------------------------
        # Extract dynamic transaction rows
        # ------------------------------
        transactions = {}  # envelope_id → dict of values

        for key, value in request.form.items():
            if key.startswith("transactions["):
                # Example key:
                # transactions[14][amount]
                parts = key.split("[")
                envelope_id = parts[1][:-1]  # remove trailing ]
                field_name = parts[2][:-1]   # also remove trailing ]

                transactions.setdefault(envelope_id, {})
                transactions[envelope_id][field_name] = value.strip()

        # ------------------------------
        # Validate required fields
        # ------------------------------
        errors = []

        for envelope_id, env in envelope_map.items():
            if envelope_id not in transactions:
                # No transaction entered for this envelope → allowed.
                continue

            txn = transactions[envelope_id]

            for field in env["fields"]:
                if field["required"]:
                    fname = field["name"]
                    if fname not in txn or txn[fname] == "":
                        errors.append(
                            f"Missing required field '{fname}' for envelope '{env['name']}'"
                        )

        if errors:
            for e in errors:
                flash(e, "error")
            return redirect(request.url)

        # ------------------------------
        # Insert receipt with DebitOrCredit
        # ------------------------------
        cur.execute(queries.INSERT_INTO_RECEIPTS_RETURN_PK, (current_user.id, budget_id, payment_source_id, debit_or_credit))
        receipt_id = cur.fetchone()[0]

        # ------------------------------
        # Insert transactions (JSONB)
        # ------------------------------
        for envelope_id, data in transactions.items():
            details_json = json.dumps(data)

            cur.execute(
                queries.INSERT_INTO_TRANSACTIONS,
                (receipt_id, envelope_id, details_json)
            )

        conn.commit()

        flash("Receipt created successfully!", "success")
        return redirect(url_for("receipts_view_route", budget_id=budget_id))

    # -----------------------------------------
    # 4. Render page (GET)
    # -----------------------------------------
    return render_template(
        "receipts_create.html",
        budget_id=budget_id,
        envelope_map=envelope_map,
        payment_sources=payment_sources
    )


def receipts_view(budget_id):
    return render_template('receipts_home.html', budget_id=budget_id)