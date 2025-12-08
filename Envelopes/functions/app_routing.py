# def get_all_transaction_types():
#     conn = db_utils.get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT DISTINCT transaction_type FROM transactions ORDER BY transaction_type;")
#     types = [row[0] for row in cur.fetchall()]
#     cur.close()
#     return types

# def get_all_years():
#     conn = db_utils.get_db_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT DISTINCT EXTRACT(YEAR FROM transaction_date) AS year FROM transactions ORDER BY year;")
#     years = [int(row[0]) for row in cur.fetchall()]
#     cur.close()
#     return years


# functions/app_routing.py
import psycopg2
from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT
from functions import auth_routes, db_utils, budget_routes, home_routes, getting_started_routes, envelopes_routes
from classes.user import User

from flask import render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

def register_routes(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login_route'


    @login_manager.user_loader
    def load_user(user_id):
        conn = db_utils.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT pk_users_id, name FROM users WHERE pk_users_id = %s", (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return User(row[0], row[1])
        return None

    @app.route('/login', methods=['GET', 'POST'])
    def login_route():
        return auth_routes.login()
        
    @app.route('/register', methods=['GET', 'POST'])
    def register_route():
        return auth_routes.register()

    @app.route('/logout')
    @login_required
    def logout_route():
        return auth_routes.logout()
    
    @app.route('/')
    @login_required
    def home_route():
        return home_routes.home()
    
    @app.route('/getting_started')
    @login_required
    def getting_started_home_route():
        return getting_started_routes.getting_started_home()
    
    @app.route('/getting_started_create_budget', methods=['GET','POST'])
    @login_required
    def getting_started_create_budget_route():
        return getting_started_routes.getting_started_create_budget_route()

    @app.route('/budget')
    @login_required
    def budget_home_route():
        return budget_routes.budget_home()
    
    @app.route('/budget_create', methods=['GET', 'POST'])
    @login_required
    def budget_create_route():
        return budget_routes.budget_create()
    
    @app.route('/budget_select_default', methods=['GET', 'POST'])
    @login_required
    def budget_select_default_route():
        return budget_routes.budget_select_default()
    
    @app.route('/budget_invite_users', methods=['GET', 'POST'])
    @login_required
    def budget_invite_users_route():
        return budget_routes.budget_invite_users()

    @app.route('/budget_settings', methods=['GET', 'POST'])
    @login_required
    def budget_settings_route():
        return budget_routes.budget_settings()

    @app.route('/envelopes', methods=['GET', 'POST'])
    @login_required
    def envelopes_home_route():
        return envelopes_routes.envelopes_home()

    @app.route('/envelopes_view', methods=['GET', 'POST'])
    @login_required
    def envelopes_view_route():
        return envelopes_routes.envelopes_view()
    
    @app.route('/envelopes_create', methods=['GET', 'POST'])
    @login_required
    def envelopes_create_route():
        return envelopes_routes.envelopes_create()


#     @app.route('/logtransaction', methods=['GET', 'POST'])
#     @login_required
#     def logtransaction():
#         conn = db_utils.get_db_connection()
#         cur = conn.cursor()

#         if request.method == 'POST':
#             transaction_date = request.form['transaction_date']
#             transaction_type = request.form['transaction_type']
#             description = request.form.get('description', '')
#             total = request.form['total']

#             # Optional: Validate date and calories
#             try:
#                 transaction_date_obj = datetime.strptime(transaction_date, '%Y-%m-%d').date()
#                 # Validate and parse total as Decimal
#                 total_dec = Decimal(total).quantize(Decimal("0.01"))  # Enforce 2 decimal places

#             except (ValueError, InvalidOperation):
#                 flash("Invalid date or total input. Please enter a valid date and numeric amount.")
#                 cur.execute('SELECT id, name FROM transaction_types ORDER BY name')
#                 types = cur.fetchall()
#                 cur.close()
#                 conn.close()
#                 return render_template('logtransaction.html', types=types)

#             cur.execute('''
#                 INSERT INTO transactions (user_id, transaction_date, transaction_type, description, total)
#                 VALUES (%s, %s, %s, %s, %s)
#             ''', (current_user.id, transaction_date_obj, transaction_type, description, total_dec))
#             conn.commit()
#             flash('Transaction logged!')
#             cur.close()
#             conn.close()
#             return redirect(url_for('logtransaction'))

#         cur.execute('SELECT id, name FROM transaction_types ORDER BY name')
#         types = cur.fetchall()
#         cur.close()
#         conn.close()
#         return render_template('logtransaction.html', types=types)

#     @app.route('/addtransactiontype', methods=['GET', 'POST'])
#     @login_required
#     def addtransactiontype():
#         if request.method == 'POST':
#             type_name = request.form['type_name'].strip()

#             if not type_name:
#                 flash("Type name cannot be empty.")
#                 return render_template('modifybudget.html')

#             conn = db_utils.get_db_connection()
#             cur = conn.cursor()

#             # Check if type already exists
#             cur.execute('SELECT 1 FROM transaction_types WHERE name = %s', (type_name,))
#             if cur.fetchone():
#                 flash("That type already exists.")
#                 cur.close()
#                 conn.close()
#                 return render_template('modifybudget.html')

#             cur.execute('''
#                 INSERT INTO transaction_types (name)
#                 VALUES (%s)
#             ''', (type_name,))
#             conn.commit()
#             cur.close()
#             conn.close()

#             flash('Transaction type added!')

#             # Redirect to avoid resubmission and update URL
#             return redirect(url_for('modifybudget'))

#         return render_template('modifybudget.html')

#     @app.route('/deletebudget', methods=['POST'])
#     @login_required
#     def deletebudget():
#         type_id = int(request.form['category_id'])  # Grabbing it from the form

#         conn = db_utils.get_db_connection()
#         cur = conn.cursor()

#         # Check if category is in use
#         cur.execute('SELECT 1 FROM transactions WHERE transaction_type = (SELECT name FROM transaction_types WHERE id = %s)', (type_id,))
#         if cur.fetchone():
#             flash('Cannot delete category in use by transactions.')
#         else:
#             cur.execute('DELETE FROM category_budgets WHERE transaction_type_id = %s', (type_id,))
#             cur.execute('DELETE FROM transaction_types WHERE id = %s', (type_id,))
#             conn.commit()
#             flash('Category deleted.')

#         cur.close()
#         conn.close()
#         return redirect(url_for('modifybudget'))
#     from datetime import datetime
#     from decimal import Decimal, InvalidOperation

#     @app.route('/modifybudget', methods=['GET', 'POST'])
#     @login_required
#     def modifybudget():
#         conn = db_utils.get_db_connection()
#         cur = conn.cursor()

#         # Fetch categories for dropdown
#         cur.execute('SELECT id, name FROM transaction_types ORDER BY name')
#         types = cur.fetchall()

#         if request.method == 'POST':
#             category_id = request.form['category_id']
#             amount_str = request.form['amount']
#             week_start_str = request.form['week_start']

#             # Validate inputs
#             try:
#                 amount = Decimal(amount_str).quantize(Decimal("0.01"))
#                 category_id = int(category_id)
#                 week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
#             except (InvalidOperation, ValueError):
#                 flash("Invalid input data.")
#                 cur.close()
#                 conn.close()
#                 return render_template('modifybudget.html', types=types, budgets=[], recent_week=None, all_budgets=[])

#             # Check if budget for this category and week_start exists
#             cur.execute('''
#                 SELECT id FROM category_budgets 
#                 WHERE transaction_type_id = %s AND week_start = %s
#             ''', (category_id, week_start))
#             row = cur.fetchone()

#             if row:
#                 # Update existing budget amount
#                 cur.execute('''
#                     UPDATE category_budgets 
#                     SET amount = %s 
#                     WHERE id = %s
#                 ''', (amount, row[0]))
#             else:
#                 # Insert new budget record
#                 cur.execute('''
#                     INSERT INTO category_budgets (transaction_type_id, amount, week_start) 
#                     VALUES (%s, %s, %s)
#                 ''', (category_id, amount, week_start))

#             conn.commit()
#             flash("Weekly budget updated!")

#         # Find the most recent week_start with budgets (latest Sunday)
#         cur.execute('SELECT MAX(week_start) FROM category_budgets')
#         recent_week = cur.fetchone()[0]

#         budgets = []
#         if recent_week:
#             # Fetch budgets for the most recent week
#             cur.execute('''
#                 SELECT cb.id, cb.amount, tt.name
#                 FROM category_budgets cb
#                 JOIN transaction_types tt ON cb.transaction_type_id = tt.id
#                 WHERE cb.week_start = %s
#                 ORDER BY tt.name
#             ''', (recent_week,))
#             budgets = cur.fetchall()

#         # Fetch all budgets for bottom table with category names and week_start
#         cur.execute('''
#             SELECT cb.id, cb.amount, cb.week_start, tt.name
#             FROM category_budgets cb
#             JOIN transaction_types tt ON cb.transaction_type_id = tt.id
#             ORDER BY cb.week_start DESC, tt.name
#         ''')
#         all_budgets = [
#             {'id': row[0], 'amount': row[1], 'week_start': row[2], 'name': row[3]}
#             for row in cur.fetchall()
#         ]

#         cur.close()
#         conn.close()

#         return render_template('modifybudget.html',
#                             types=types,
#                             budgets=budgets,
#                             recent_week=recent_week,
#                             all_budgets=all_budgets)
#     from decimal import Decimal, InvalidOperation
#     from datetime import datetime

#     @app.route('/editbudget/<int:budget_id>', methods=['GET', 'POST'])
#     @login_required
#     def editbudget(budget_id):
#         conn = db_utils.get_db_connection()
#         cur = conn.cursor()

#         # Fetch the budget row by ID
#         cur.execute('''
#             SELECT cb.id, cb.amount, cb.week_start, tt.name
#             FROM category_budgets cb
#             JOIN transaction_types tt ON cb.transaction_type_id = tt.id
#             WHERE cb.id = %s
#         ''', (budget_id,))
#         row = cur.fetchone()

#         if row is None:
#             flash("Budget not found.")
#             cur.close()
#             conn.close()
#             return redirect(url_for('modifybudget'))

#         budget = {
#             'id': row[0],
#             'amount': row[1],
#             'week_start': row[2],
#             'name': row[3]
#         }

#         if request.method == 'POST':
#             amount_str = request.form.get('amount')
#             week_start_str = request.form.get('week_start')

#             # Validate and parse amount
#             try:
#                 amount = Decimal(amount_str).quantize(Decimal('0.01'))
#             except (InvalidOperation, TypeError):
#                 flash("Invalid amount format.")
#                 return render_template('editbudget.html', budget=budget)

#             # Validate and parse week_start date
#             try:
#                 week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
#             except (ValueError, TypeError):
#                 flash("Invalid week start date format. Please use YYYY-MM-DD.")
#                 return render_template('editbudget.html', budget=budget)

#             # Update the budget in DB
#             cur.execute('''
#                 UPDATE category_budgets
#                 SET amount = %s, week_start = %s
#                 WHERE id = %s
#             ''', (amount, week_start, budget_id))
#             conn.commit()

#             flash("Budget updated successfully.")
#             cur.close()
#             conn.close()
#             return redirect(url_for('modifybudget'))

#         # GET request — render the form with existing budget data
#         cur.close()
#         conn.close()
#         return render_template('editbudget.html', budget=budget)

#     from calendar import monthrange
#     from datetime import datetime, date, timedelta
#     from decimal import Decimal
#     from flask import render_template, request
#     from flask_login import login_required
#     from collections import defaultdict

#     @app.route('/viewbudget', methods=['GET', 'POST'])
#     @login_required
#     def viewbudget():
#         from collections import defaultdict
#         from decimal import Decimal
#         from datetime import datetime, timedelta
#         from calendar import monthrange

#         selected_month = datetime.now().month
#         selected_year = datetime.now().year
#         selected_categories = []
#         selected_weeks = []

#         conn = db_utils.get_db_connection()
#         cur = conn.cursor()

#         # Get all categories from DB (exclude Total)
#         cur.execute("SELECT name FROM transaction_types ORDER BY name")
#         categories_list = [row[0] for row in cur.fetchall() if row[0] != 'Total']

#         action = request.form.get('action', 'view')

#         if request.method == 'POST':
#             selected_month = int(request.form.get('month', selected_month))
#             selected_year = int(request.form.get('year', selected_year))
#             selected_categories = request.form.getlist('categories')
#             selected_weeks = request.form.getlist('weeks')

#             # Always include Total in calculations
#             if 'Total' not in selected_categories:
#                 selected_categories.append('Total')

#         # ---- Compute all weeks in month (≥4 days logic) ----
#         weeks_in_month = []
#         first_day = datetime(selected_year, selected_month, 1)
#         last_day = datetime(selected_year, selected_month, monthrange(selected_year, selected_month)[1])
#         current = first_day - timedelta(days=first_day.weekday() + 1 if first_day.weekday() != 6 else 0)
#         while current <= last_day:
#             days_in_month = sum(1 for i in range(7) if (current + timedelta(days=i)).month == selected_month)
#             if days_in_month >= 4:
#                 week_end = current + timedelta(days=6)
#                 weeks_in_month.append({'start': current, 'end': week_end})
#             current += timedelta(days=7)

#         # Determine current week based on today's date
#         today = datetime.today()
#         this_week_start = today - timedelta(days=today.weekday() + 1 if today.weekday() != 6 else 0)
#         this_week_str = this_week_start.strftime("%Y-%m-%d")

#         # Only default to today’s week if first load and NOT a month-change
#         if not selected_weeks and action != 'month-change':
#             selected_weeks = [this_week_str]

#         # If GET or no categories selected yet, show selection form
#         if not selected_categories or request.method == 'GET' or action == 'month-change':
#             cur.close()
#             conn.close()
#             return render_template(
#                 'select_categories.html',
#                 categories=categories_list,
#                 selected_month=selected_month,
#                 selected_year=selected_year,
#                 selected_categories=selected_categories,
#                 weeks_in_month=weeks_in_month,
#                 selected_weeks=selected_weeks
#             )

#         # ---- Prepare SQL for selected categories (exclude Total) ----
#         categories_for_sql = [c for c in selected_categories if c != 'Total']
#         placeholders = ', '.join(['%s'] * len(categories_for_sql))

#         # ---- Budgets ----
#         query_categories = f"""
#             SELECT wb.week_start, tt.name AS category, wb.amount
#             FROM category_budgets wb
#             JOIN transaction_types tt ON wb.transaction_type_id = tt.id
#             WHERE tt.name IN ({placeholders})
#             ORDER BY wb.week_start, tt.name
#         """
#         cur.execute(query_categories, categories_for_sql)
#         category_results = cur.fetchall()

#         query_total = f"""
#             SELECT wb.week_start, 'Total' AS category, SUM(wb.amount) AS amount
#             FROM category_budgets wb
#             JOIN transaction_types tt ON wb.transaction_type_id = tt.id
#             WHERE tt.name IN ({placeholders})
#             GROUP BY wb.week_start
#         """
#         cur.execute(query_total, categories_for_sql)
#         total_results = cur.fetchall()

#         budget_data = total_results + category_results
#         budget_by_week = {}
#         all_categories = set()
#         for week_start, name, amount in budget_data:
#             budget_by_week.setdefault(week_start, {})[name] = amount
#             all_categories.add(name)

#         # ---- Transactions ----
#         query_transactions = f"""
#             SELECT t.transaction_date, tt.name AS category, t.total
#             FROM transactions t
#             JOIN transaction_types tt ON t.transaction_type = tt.name
#             WHERE tt.name IN ({placeholders})
#         """
#         cur.execute(query_transactions, categories_for_sql)
#         transaction_data = cur.fetchall()

#         transactions_by_type_and_week = {}
#         for tdate, name, total in transaction_data:
#             week_start = tdate - timedelta(days=tdate.weekday() + 1 if tdate.weekday() != 6 else 0)
#             transactions_by_type_and_week.setdefault(week_start, {}).setdefault(name, Decimal('0.00'))
#             transactions_by_type_and_week[week_start][name] += total
#             all_categories.add(name)

#         # Total for transactions
#         for week_start in transactions_by_type_and_week.keys():
#             total_sum = sum(transactions_by_type_and_week[week_start].get(cat, Decimal('0.00'))
#                             for cat in categories_for_sql)
#             transactions_by_type_and_week[week_start]['Total'] = total_sum
#             all_categories.add('Total')

#         # ---- Build display weeks ----
#         all_week_starts = sorted(set(budget_by_week.keys()) | set(transactions_by_type_and_week.keys()))
#         cumulative_budget = defaultdict(Decimal)
#         cumulative_spent = defaultdict(Decimal)
#         weeks = []

#         for week_start in all_week_starts:
#             end = week_start + timedelta(days=6)
#             summary = {}
#             this_week_budgets = budget_by_week.get(week_start, {})
#             this_week_spent = transactions_by_type_and_week.get(week_start, {})

#             for cat in sorted(all_categories, key=lambda x: (0 if x == 'Total' else 2 if x == 'Unplanned' else 1, x)):
#                 if cat in selected_categories:
#                     weekly_budget = this_week_budgets.get(cat, Decimal('0.00'))
#                     spent = this_week_spent.get(cat, Decimal('0.00'))

#                     cumulative_budget[cat] += weekly_budget
#                     envelope = cumulative_budget[cat] - cumulative_spent[cat]
#                     remaining = envelope - spent
#                     cumulative_spent[cat] += spent

#                     summary[cat] = {
#                         'budget': weekly_budget,
#                         'spent': spent,
#                         'envelope': envelope,
#                         'remaining': remaining
#                     }

#             # Only show weeks the user selected
#             if week_start.strftime("%Y-%m-%d") in selected_weeks:
#                 weeks.append({
#                     'start': week_start,
#                     'end': end,
#                     'summary': summary
#                 })

#         cur.close()
#         conn.close()
#         return render_template(
#             'viewbudget.html',
#             weeks=weeks,
#             selected_month=selected_month,
#             selected_year=selected_year
#         )


#     @app.route('/viewbudget/week')
#     @login_required
#     def viewbudget_week():
#         start_str = request.args.get('start')
#         end_str = request.args.get('end')

#         try:
#             start = datetime.strptime(start_str, '%Y-%m-%d').date()
#             end = datetime.strptime(end_str, '%Y-%m-%d').date()
#         except (ValueError, TypeError):
#             flash("Invalid date range.")
#             return redirect(url_for('viewbudget'))

#         conn = db_utils.get_db_connection()
#         cur = conn.cursor()

#         cur.execute('''
#             SELECT transaction_type, transaction_date, description, total
#             FROM transactions
#             WHERE transaction_date >= %s
#             AND transaction_date <= %s
#             ORDER BY transaction_type, transaction_date
#         ''', (start, end))
        
#         raw_data = cur.fetchall()
#         cur.close()
#         conn.close()

#         # Group by transaction type
#         from collections import defaultdict
#         categorized = defaultdict(list)
#         for ttype, tdate, desc, total in raw_data:
#             categorized[ttype].append({
#                 'date': tdate,
#                 'description': desc,
#                 'total': total
#             })

#         return render_template('viewbudget_week.html', start=start, end=end, categorized=categorized)

#     @app.route('/viewtransactions')
#     @login_required
#     def viewtransactions():

#         # if not user_id:
#         #     return redirect(url_for('login'))

#         transaction_type_filter = request.args.get('transaction_type', '')
#         search_filter = request.args.get('search', '')
#         year_filter = request.args.get('year', '')
#         month_filter = request.args.get('month', '')
#         page = int(request.args.get('page', 1))
#         per_page = int(request.args.get('per_page', 10))

#         offset = (page - 1) * per_page

#         # Base query and params
#         query = "SELECT id, transaction_date, transaction_type, description, total FROM transactions where 1=1"
#         params = []

#         # Filters
#         if transaction_type_filter:
#             query += " AND transaction_type = %s"
#             params.append(transaction_type_filter)

#         if search_filter:
#             query += " AND description ILIKE %s"
#             params.append(f"%{search_filter}%")

#         if year_filter:
#             query += " AND EXTRACT(YEAR FROM transaction_date) = %s"
#             params.append(int(year_filter))

#         if month_filter:
#             query += " AND EXTRACT(MONTH FROM transaction_date) = %s"
#             params.append(int(month_filter))

#         # Count total items for pagination
#         count_query = f"SELECT COUNT(*) FROM ({query}) AS subquery"
#         cur = db_utils.get_db_connection().cursor()
#         cur.execute(count_query, params)
#         total_items = cur.fetchone()[0]

#         # Add ordering and limit/offset
#         query += " ORDER BY transaction_date DESC LIMIT %s OFFSET %s"
#         params.extend([per_page, offset])

#         cur.execute(query, params)
#         transactions = cur.fetchall()

#         current_year = datetime.now().year
#         years = get_all_years()

#         # Prepare month options (1-12 with names)
#         months = [(i, month_name[i]) for i in range(1, 13)]

#         total_pages = (total_items + per_page - 1) // per_page

#         return render_template('viewtransactions.html',
#                             transactions=transactions,
#                             all_types=get_all_transaction_types(),  # Your function for types
#                             transaction_type_filter=transaction_type_filter,
#                             search_filter=search_filter,
#                             year_filter=int(year_filter) if year_filter else '',
#                             month_filter=int(month_filter) if month_filter else '',
#                             years=years,
#                             months=months,
#                             page=page,
#                             per_page=per_page,
#                             total_pages=total_pages,
#                             total_items=total_items)

#     @app.route('/transactions/delete/<int:txn_id>', methods=['POST'])
#     @login_required
#     def delete_transaction(txn_id):
#         conn = db_utils.get_db_connection()
#         cur = conn.cursor()

#         # Optional: Ensure current user owns this transaction
#         cur.execute('SELECT id FROM transactions WHERE id = %s', (txn_id,))
#         txn = cur.fetchone()
#         if not txn:
#             flash('Transaction not found or already deleted.')
#         else:
#             cur.execute('DELETE FROM transactions WHERE id = %s', (txn_id,))
#             conn.commit()
#             flash('Transaction deleted.')

#         cur.close()
#         conn.close()
#         return redirect(url_for('viewtransactions'))

#     @app.route('/transactions/modify/<int:txn_id>', methods=['GET', 'POST'])
#     @login_required
#     def modify_transaction(txn_id):
#         conn = db_utils.get_db_connection()
#         cur = conn.cursor()
#         # Fetch the transaction to edit, ensure it belongs to current user
#         cur.execute('''
#             SELECT id, transaction_date, transaction_type, description, total
#             FROM transactions
#             WHERE id = %s
#         ''', (txn_id,))
#         txn = cur.fetchone()

#         if txn is None:
#             cur.close()
#             conn.close()
#             flash('Transaction not found or access denied.')
#             return redirect(url_for('viewtransactions'))

#         if request.method == 'POST':
#             # Read form data
#             transaction_date = request.form['transaction_date']
#             transaction_type = request.form['transaction_type']
#             description = request.form.get('description', '')
#             total = request.form['total']

#             # Validate inputs
#             try:
#                 transaction_date_obj = datetime.strptime(transaction_date, '%Y-%m-%d').date()
#                 total_dec = Decimal(total).quantize(Decimal('0.01'))
#             except Exception:
#                 flash('Invalid date or amount.')
#                 cur.close()
#                 conn.close()
#                 return redirect(url_for('modify_transaction', txn_id=txn_id))

#             # Update record
#             cur.execute('''
#                 UPDATE transactions
#                 SET transaction_date = %s,
#                     transaction_type = %s,
#                     description = %s,
#                     total = %s
#                 WHERE id = %s
#             ''', (transaction_date_obj, transaction_type, description, total_dec, txn_id))
#             conn.commit()
#             cur.close()
#             conn.close()

#             flash('Transaction updated successfully.')
#             return redirect(url_for('viewtransactions'))

#         # For GET: show form with current values
#         # Also fetch transaction types for dropdown
#         cur.execute('SELECT name FROM transaction_types ORDER BY name')
#         types = [row[0] for row in cur.fetchall()]
#         cur.close()
#         conn.close()

#         return render_template('modifytransaction.html', txn=txn, types=types)

# # from flask import render_template
# # from datetime import date, timedelta
# # from decimal import Decimal