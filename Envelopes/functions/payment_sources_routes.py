from functions import db_utils, queries

from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user

def payment_sources_home(budget_id):
    return render_template('payment_sources_home.html', budget_id=budget_id)

def payment_sources_create(budget_id):
    if request.method == 'POST':
        payment_source_name = request.form.get('payment_source_name')
        
        conn = db_utils.get_db_connection()
        cur = conn.cursor()

        # Check if there is a payment source with this name
        cur.execute(queries.GET_PAYMENT_SOURCES_BY_BUDGET_ID_AND_NAME, (budget_id, payment_source_name))
        existing = cur.fetchone()

        if not existing or existing == None:
            # insert
            cur.execute(queries.INSERT_INTO_PAYMENT_SOURCES_RETURN_PK, (budget_id, payment_source_name))
            conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for('payment_sources_home_route', budget_id=budget_id))
    return render_template('payment_sources_create.html', budget_id=budget_id)

def payment_sources_view(budget_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    # Get payment sources for the budget
    cur.execute(queries.GET_PAYMENT_SOURCES_BY_BUDGET_ID, (budget_id,))
    payment_sources = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('payment_sources_view.html', budget_id=budget_id, payment_sources=payment_sources)
def payment_sources_edit(budget_id, payment_source_id):
    conn = db_utils.get_db_connection()
    cur = conn.cursor()

    if request.method == "GET":
        # Retrieve the record being edited
        cur.execute(queries.GET_PAYMENT_SOURCE_BY_PAYMENT_SOURCE_ID, (payment_source_id,))
        payment_source = cur.fetchone()

        cur.close()
        conn.close()

        return render_template('payment_sources_edit.html', budget_id=budget_id,payment_source=payment_source)

    # POST: update or delete
    if "delete" in request.form:
        cur.execute(queries.DROP_FROM_PAYMENT_SOURCES_BY_PAYMENT_SOURCES_ID, (payment_source_id,))
        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for("payment_sources_view_route", budget_id=budget_id))

    # Otherwise UPDATE
    new_name = request.form.get("name")

    cur.execute(queries.UPDATE_PAYMENT_SOURCES_BY_PAYMENT_SOURCE_ID, (new_name, payment_source_id))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("payment_sources_view_route", budget_id=budget_id))


def payment_sources_delete(budget_id,payment_source_id):
    return render_template('payment_sources_home.html', budget_id=budget_id, payment_source_id=payment_source_id)