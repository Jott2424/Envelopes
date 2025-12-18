from functions import db_utils, queries, helper_functions as hf
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
import json
from decimal import Decimal
from datetime import datetime

# ----------------------------
# Receipts Routes
# ----------------------------

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
        if save_as_template:
            if not description:
                flash("Please provide a description for the template.", "error")
                return redirect(request.url)

            # Insert receipt template
            cur.execute(
                queries.INSERT_INTO_RECEIPT_TEMPLATES_RETURN_PK,
                (budget_id, current_user.id, payment_source_id, debit_or_credit, merchant, description)
            )
            template_id = cur.fetchone()[0]

            # Insert transaction templates
            for txn in transactions.values():
                envelope_id = txn.pop("envelope_id")
                cur.execute(
                    queries.INSERT_INTO_TRANSACTION_TEMPLATES,
                    (template_id, envelope_id, json.dumps(txn))
                )

            conn.commit()
            flash("Receipt template saved successfully!", "success")
            cur.close()
            conn.close()
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
            cur.close()
            conn.close()
            return redirect(url_for("receipts_view_route", budget_id=budget_id))

    cur.close()
    conn.close()
    return render_template(
        "receipts_create.html",
        budget_id=budget_id,
        envelope_map=envelope_map,
        payment_sources=payment_sources
    )


def receipts_view(budget_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    cur.execute(queries.GET_RECEIPTS_AND_PAYMENT_SOURCES_BY_BUDGETS_ID, (budget_id,))
    columns = [desc[0] for desc in cur.description]
    receipts = [dict(zip(columns, row)) for row in cur.fetchall()]  # Convert tuples to dicts

    cur.close()
    conn.close()
    return render_template("receipts_view.html", budget_id=budget_id, receipts=receipts)


def receipt_templates_view(budget_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    cur.execute(queries.GET_RECEIPT_TEMPLATES_AND_PAYMENT_SOURCES_BY_BUDGETS_ID, (budget_id,))
    columns = [desc[0] for desc in cur.description]
    templates = [dict(zip(columns, row)) for row in cur.fetchall()]  # Convert tuples to dicts

    cur.close()
    conn.close()
    return render_template("receipt_templates_view.html", budget_id=budget_id, templates=templates)


def receipt_templates_edit(budget_id, template_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    # Load template
    cur.execute(queries.GET_RECEIPT_TEMPLATES_BY_RECEIPT_TEMPLATES_ID, (template_id,))
    row = cur.fetchone()
    if not row:
        flash("Template not found.", "error")
        cur.close()
        conn.close()
        return redirect(url_for("receipt_templates_view_route", budget_id=budget_id))

    template = {
        "pk_receipt_templates_id": row[0],
        "fk_payment_sources_id": row[1],
        "debit_or_credit": row[2],
        "merchant": row[3],
        "description": row[4]
    }

    # Load payment sources
    cur.execute(queries.GET_PAYMENT_SOURCES_BY_BUDGET_ID, (budget_id,))
    payment_sources = cur.fetchall()

    # Load transactions
    cur.execute(queries.GET_TRANSACTION_TEMPLATES_BY_RECEIPT_TEMPLATES_ID, (template_id,))
    transaction_template_rows = cur.fetchall()
    print(transaction_template_rows)
    template_transactions = [{"envelope_id": r[0], "details": r[1]} for r in transaction_template_rows]

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

    if request.method == "POST":
        action = request.form.get("action")

        if action in ("save_template", "create_receipt"):
            merchant = request.form.get("merchant")
            debit_or_credit = request.form.get("debit_or_credit")
            payment_source_id = request.form.get("payment_source_id")
            description = request.form.get("receipt_description")

            # Update template
            cur.execute(queries.UPDATE_RECEIPT_TEMPLATES_BY_PK, (merchant, debit_or_credit, payment_source_id, description, template_id))

            # Delete old transactions
            cur.execute(queries.DROP_FROM_TRANSACTION_TEMPLATES_BY_FK, (template_id,))

            # Insert new transactions
            transactions = {}
            for key, value in request.form.items():
                if key.startswith("transactions["):
                    parts = key.split("[")
                    row_id = parts[1][:-1]
                    field_name = parts[2][:-1]
                    transactions.setdefault(row_id, {})
                    transactions[row_id][field_name] = value.strip()

            for txn in transactions.values():
                envelope_id = txn.pop("envelope_id")
                cur.execute(queries.INSERT_INTO_TRANSACTION_TEMPLATES, (template_id, envelope_id, json.dumps(txn)))

            conn.commit()

            if action == "create_receipt":
                total_amount = Decimal("0.00")
                for txn in transactions.values():
                    amt = txn.get("amount")
                    if amt:
                        total_amount += Decimal(amt)

                cur.execute(
                    queries.INSERT_INTO_RECEIPTS_RETURN_PK,
                    (budget_id, current_user.id, payment_source_id, debit_or_credit, datetime.today().date(),
                     merchant, total_amount, description)
                )
                receipt_id = cur.fetchone()[0]

                for envelope_id, txn in transactions.items():
                    envelope_id = int(envelope_id)  # keys come in as strings

                    txn_description = txn.pop("description", None)
                    if txn_description:
                        txn["description"] = txn_description

                    cur.execute(
                        queries.INSERT_INTO_TRANSACTIONS,
                        (receipt_id, envelope_id, json.dumps(txn))
                    )


                conn.commit()
                flash("Receipt created successfully from template.", "success")
            else:
                flash("Template updated successfully.", "success")

            cur.close()
            conn.close()
            return redirect(url_for("receipt_templates_view_route", budget_id=budget_id))

    cur.close()
    conn.close()
    return render_template("receipt_templates_edit.html",budget_id=budget_id,template=template,template_transactions=template_transactions,payment_sources=payment_sources,envelope_map=envelope_map)

def receipt_templates_delete(budget_id, template_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    # Ensure template exists (optional but nice)
    cur.execute(
        queries.GET_RECEIPT_TEMPLATES_BY_RECEIPT_TEMPLATES_ID,
        (template_id,)
    )
    if not cur.fetchone():
        flash("Template not found.", "error")
        cur.close()
        conn.close()
        return redirect(url_for("receipt_templates_view_route", budget_id=budget_id))

    # Delete child rows first
    cur.execute(
        queries.DROP_FROM_TRANSACTION_TEMPLATES_BY_FK,
        (template_id,)
    )
    cur.execute(
        queries.DROP_FROM_RECEIPT_TEMPLATES_BY_PK,
        (template_id,)
    )

    conn.commit()
    cur.close()
    conn.close()

    flash("Template deleted successfully.", "success")
    return redirect(url_for("receipt_templates_view_route", budget_id=budget_id))

def receipts_edit(budget_id, receipt_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    # -----------------------------
    # Load receipt
    # -----------------------------
    cur.execute(queries.GET_RECEIPT_BY_PK, (receipt_id,))
    row = cur.fetchone()
    if not row:
        flash("Receipt not found.", "error")
        return redirect(url_for("receipts_view_route", budget_id=budget_id))

    receipt = {
        "pk_receipts_id": row[0],
        "fk_payment_sources_id": row[1],
        "debit_or_credit": row[2],
        "transaction_date": row[3],
        "merchant": row[4],
        "description": row[5]
    }

    # -----------------------------
    # Payment sources
    # -----------------------------
    cur.execute(queries.GET_PAYMENT_SOURCES_BY_BUDGET_ID, (budget_id,))
    payment_sources = cur.fetchall()

    # -----------------------------
    # Transactions
    # -----------------------------
    cur.execute(queries.GET_TRANSACTIONS_BY_RECEIPT_ID, (receipt_id,))
    transaction_rows = cur.fetchall()
    receipt_transactions = [
        {"envelope_id": r[0], "details": r[1]} for r in transaction_rows
    ]

    # -----------------------------
    # Envelope map
    # -----------------------------
    cur.execute(queries.GET_ENVELOPES_NAME_AND_TRANSACTION_FIELDS_BY_BUDGET, (budget_id,))
    rows = cur.fetchall()

    envelope_map = {}
    for envelope_name, envelope_id, form_order, field_name, field_type, is_required in rows:
        envelope_map.setdefault(envelope_id, {"name": envelope_name, "fields": []})
        envelope_map[envelope_id]["fields"].append({
            "name": field_name,
            "type": field_type,
            "required": bool(is_required),
            "form_order": form_order
        })

    for env in envelope_map.values():
        env["fields"].sort(key=lambda f: f["form_order"])

    # -----------------------------
    # POST
    # -----------------------------
    if request.method == "POST":
        action = request.form.get("action")

        # Save receipt
        merchant = request.form.get("merchant")
        debit_or_credit = request.form.get("debit_or_credit")
        payment_source_id = request.form.get("payment_source_id")
        transaction_date = request.form.get("transaction_date")
        description = request.form.get("receipt_description")

        # Parse transactions
        transactions = {}
        for key, value in request.form.items():
            if key.startswith("transactions["):
                parts = key.split("[")
                row_id = parts[1][:-1]
                field = parts[2][:-1]
                transactions.setdefault(row_id, {})[field] = value.strip()

        # Recalculate amount
        total_amount = Decimal("0.00")
        for txn in transactions.values():
            if txn.get("amount"):
                total_amount += Decimal(txn["amount"])

        # Update receipt
        cur.execute(
            queries.UPDATE_RECEIPT_BY_PK,
            (
                payment_source_id,
                debit_or_credit,
                transaction_date,
                merchant,
                total_amount,
                description,
                receipt_id
            )
        )

        # Replace transactions
        cur.execute(queries.DROP_FROM_TRANSACTIONS_BY_FK, (receipt_id,))
        for txn in transactions.values():
            envelope_id = txn.pop("envelope_id")
            cur.execute(
                queries.INSERT_INTO_TRANSACTIONS,
                (receipt_id, envelope_id, json.dumps(txn))
            )

        conn.commit()
        flash("Receipt updated.", "success")
        return redirect(url_for("receipts_view_route", budget_id=budget_id, receipt_id=receipt_id))

    return render_template(
        "receipts_edit.html",
        budget_id=budget_id,
        receipt=receipt,
        receipt_transactions=receipt_transactions,
        payment_sources=payment_sources,
        envelope_map=envelope_map
    )

def receipts_delete(budget_id, receipt_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    # Delete children first
    cur.execute(
        queries.DROP_FROM_TRANSACTIONS_BY_FK,
        (receipt_id,)
    )

    # Delete receipt
    cur.execute(
        queries.DROP_FROM_RECEIPTS_BY_PK,
        (receipt_id,)
    )

    conn.commit()
    cur.close()
    conn.close()

    flash("Receipt deleted successfully.", "success")
    return redirect(url_for("receipts_view_route", budget_id=budget_id))
