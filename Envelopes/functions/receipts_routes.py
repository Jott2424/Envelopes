from functions import db_utils, queries, helper_functions as hf

from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
import json
from decimal import Decimal 

def receipts_home(budget_id):
    return render_template('receipts_home.html', budget_id=budget_id)

def receipts_create(budget_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    # Load envelope fields
    cur.execute(queries.GET_ENVELOPES_NAME_AND_TRANSACTION_FIELDS_BY_BUDGET, (budget_id,))
    rows = cur.fetchall()

    envelope_map = {}
    for envelope_name, envelope_id, form_order, field_name, field_type, is_required in rows:
        if envelope_id not in envelope_map:
            envelope_map[envelope_id] = {"name": envelope_name, "fields": []}
        envelope_map[envelope_id]["fields"].append({
            "name": field_name,
            "type": field_type,
            "required": bool(is_required),
            "form_order": form_order
        })
    for env in envelope_map.values():
        env["fields"].sort(key=lambda f: f["form_order"])

    # Get payment sources
    cur.execute(queries.GET_PAYMENT_SOURCES_BY_BUDGET_ID, (budget_id,))
    payment_sources = cur.fetchall()

    if request.method == "POST":
        payment_source_id = request.form.get("payment_source_id")
        debit_or_credit = request.form.get("debit_or_credit")
        transaction_date = request.form.get("transaction_date")
        merchant = request.form.get("merchant")
        description = request.form.get("receipt_description", "")

        if not all([payment_source_id, debit_or_credit, transaction_date, merchant]):
            flash("Date, merchant, payment source, and transaction type are required.", "error")
            return redirect(request.url)

        # Collect transactions
        transactions = {}
        for key, value in request.form.items():
            if key.startswith("transactions["):
                parts = key.split("[")
                row_id = parts[1][:-1]
                field_name = parts[2][:-1]
                transactions.setdefault(row_id, {})
                transactions[row_id][field_name] = value.strip()

        # Validate required envelope fields
        errors = []
        for row_id, txn in transactions.items():
            envelope_id = txn.get("envelope_id")
            if not envelope_id:
                errors.append("Each transaction must have an envelope selected.")
                continue
            env = envelope_map.get(int(envelope_id))
            if not env:
                continue
            for field in env["fields"]:
                if field["required"]:
                    fname = field["name"]
                    if fname not in txn or txn[fname] == "":
                        errors.append(f"Missing required field '{fname}' for envelope '{env['name']}'")
        if errors:
            for e in errors:
                flash(e, "error")
            return redirect(request.url)

        save_as_template = request.form.get("save_as_template")
        template_name = request.form.get("template_name")

        if save_as_template:
            if not template_name:
                flash("Please provide a template name.", "error")
                return redirect(request.url)

            # Insert receipt template
            cur.execute(
                queries.INSERT_INTO_RECEIPT_TEMPLATES_RETURN_PK,
                (budget_id, current_user.id, payment_source_id, debit_or_credit, merchant, template_name, description)
            )
            template_id = cur.fetchone()[0]

            # Insert transactions as templates
            for txn in transactions.values():
                envelope_id = txn.pop("envelope_id")
                txn_description = txn.pop("description", None)
                if txn_description:
                    txn["description"] = txn_description
                cur.execute(
                    queries.INSERT_INTO_TRANSACTION_TEMPLATES,
                    (template_id, envelope_id, json.dumps(txn))
                )

            conn.commit()
            flash("Receipt template saved successfully!", "success")
            return redirect(url_for("receipt_templates_view_route", budget_id=budget_id))

        else:
            # Calculate total amount
            total_amount = Decimal("0.00")
            for txn in transactions.values():
                amt = txn.get("amount")
                if amt:
                    try:
                        total_amount += Decimal(amt)
                    except Exception:
                        flash("Invalid amount value.", "error")
                        return redirect(request.url)

            # Insert normal receipt
            cur.execute(
                queries.INSERT_INTO_RECEIPTS_RETURN_PK,
                (budget_id, current_user.id, payment_source_id, debit_or_credit, transaction_date, merchant, total_amount, description)
            )
            receipt_id = cur.fetchone()[0]

            # Insert transactions
            for txn in transactions.values():
                envelope_id = txn.pop("envelope_id")
                txn_description = txn.pop("description", None)
                if txn_description:
                    txn["description"] = txn_description
                cur.execute(
                    queries.INSERT_INTO_TRANSACTIONS,
                    (receipt_id, envelope_id, json.dumps(txn))
                )

            conn.commit()
            flash("Receipt created successfully!", "success")
            return redirect(url_for("receipts_view_route", budget_id=budget_id))

    return render_template("receipts_create.html", budget_id=budget_id, envelope_map=envelope_map, payment_sources=payment_sources)


def receipts_view(budget_id):
    return render_template('receipts_home.html', budget_id=budget_id)