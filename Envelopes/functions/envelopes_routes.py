from functions import db_utils

from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user

def envelopes_home():
    return render_template('envelopes_home.html')

def envelopes_view():
    return render_template('envelopes_view.html')

def envelopes_create():
    if request.method == 'POST':
        name = request.form.get('envelope_name')

        conn = db_utils.get_db_connection()
        cur = conn.cursor()
        
        #check if there is already an envelope in this budget with this name
        cur.execute('''
            SELECT fk_budgets_id
            FROM user_default_budget
            WHERE fk_users_id = %s
            ''',(current_user.id,))
        budget_id = cur.fetchone()

        cur.execute('''
            SELECT pk_envelopes_id
            FROM envelopes
            WHERE name = %s
            AND fk_budgets_id = %s
            ''', (name,budget_id))
        exists = cur.fetchone()
        
        # if not then insert
        if exists == None:
            cur.execute('''
                INSERT INTO envelopes (fk_budgets_id, name)
                VALUES (%s, %s)
                ''',(budget_id, name))

            #get this inserted envelopes id
            cur.execute('''
                SELECT pk_envelopes_id
                FROM envelopes
                WHERE name = %s
                AND fk_budgets_id = %s
                ''', (name,budget_id))
            pk_id = cur.fetchone()[0]
            print(pk_id)

            #insert this envelope's columns into the column tracking table
            trackers = request.form.getlist('trackers[]')
            types = request.form.getlist('types[]')
            required_indices = request.form.getlist('required[]')
            required_indices = [i for i in required_indices]

            form_order_counter = 1
            for idx, (t_name, t_type) in enumerate(zip(trackers, types)):
                print(idx)
                is_required = idx in required_indices
                cur.execute('''
                INSERT INTO envelope_transaction_fields (fk_budgets_id, fk_envelopes_id, form_order, field_name, field_type, is_required)
                VALUES (%s,%s,%s,%s,%s,%s)
                ''', (budget_id,pk_id,form_order_counter,t_name,t_type,is_required))
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
