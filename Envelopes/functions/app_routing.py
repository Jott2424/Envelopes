# functions/app_routing.py
import psycopg2
from config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT
from functions import auth_routes, db_utils, budget_routes, home_routes, getting_started_routes, envelopes_routes, receipts_routes, payment_sources_routes
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

########################## AUTH ##########################
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

########################## HOME ##########################
    @app.route('/')
    @login_required
    def home_route():
        return home_routes.home()
    
########################## GETTING STARTED ##########################
    @app.route('/getting_started')
    @login_required
    def getting_started_home_route():
        return getting_started_routes.getting_started_home()
    
    @app.route('/getting_started_create_budget', methods=['GET','POST'])
    @login_required
    def getting_started_create_budget_route():
        return getting_started_routes.getting_started_create_budget_route()

########################## BUDGET ##########################
    @app.route('/budget/<int:budget_id>/create', methods=['GET', 'POST'])
    @login_required
    def budget_create_route(budget_id):
        return budget_routes.budget_create(budget_id)
        
    @app.route('/budget/<int:budget_id>')
    @login_required
    def budget_home_route(budget_id):
        return budget_routes.budget_home(budget_id)
    
    @app.route('/budget/<int:budget_id>/select_default', methods=['GET', 'POST'])
    @login_required
    def budget_select_default_route(budget_id):
        return budget_routes.budget_select_default(budget_id)
    
    @app.route('/budget/<int:budget_id>/invite_users', methods=['GET', 'POST'])
    @login_required
    def budget_invite_users_route(budget_id):
        return budget_routes.budget_invite_users(budget_id)

    @app.route('/budget/<int:budget_id>/settings', methods=['GET', 'POST'])
    @login_required
    def budget_settings_route(budget_id):
        return budget_routes.budget_settings(budget_id)
    
    @app.route('/budget/<int:budget_id>/ledger_overview', methods=['GET', 'POST'])
    @login_required
    def ledger_overview_route(budget_id):
        return budget_routes.ledger_overview(budget_id)
    
    @app.route('/budget/<int:budget_id>/ledger_settings', methods=['GET', 'POST'])
    @login_required
    def ledger_settings_route(budget_id):
        return budget_routes.ledger_settings(budget_id)

########################## ENVELOPES ##########################
    @app.route('/budget/<int:budget_id>/envelopes', methods=['GET', 'POST'])
    @login_required
    def envelopes_home_route(budget_id):
        return envelopes_routes.envelopes_home(budget_id)

    @app.route('/budget/<int:budget_id>/envelopes/view', methods=['GET', 'POST'])
    @login_required
    def envelopes_view_route(budget_id):
        return envelopes_routes.envelopes_view(budget_id)
    
    @app.route('/budget/<int:budget_id>/envelopes/create', methods=['GET', 'POST'])
    @login_required
    def envelopes_create_route(budget_id):
        return envelopes_routes.envelopes_create(budget_id)

    @app.route('/budget/<int:budget_id>/envelopes/<int:envelope_id>/edit', methods=['GET', 'POST'])
    @login_required
    def envelopes_edit_route(budget_id,envelope_id):
        return envelopes_routes.envelopes_edit(budget_id,envelope_id)

    @app.route('/budget/<int:budget_id>/envelopes/<int:envelope_id>/delete', methods=['POST'])
    @login_required
    def envelopes_delete_route(budget_id, envelope_id):
        return envelopes_routes.envelopes_delete(budget_id,envelope_id)

########################## RECEIPTS ##########################
    @app.route('/budget/<int:budget_id>/receipts', methods=['GET', 'POST'])
    @login_required
    def receipts_home_route(budget_id):
        return receipts_routes.receipts_home(budget_id)

    @app.route('/budget/<int:budget_id>/receipts/view', methods=['GET', 'POST'])
    @login_required
    def receipts_view_route(budget_id):
        return receipts_routes.receipts_view(budget_id)

    @app.route('/budget/<int:budget_id>/receipts/create', methods=['GET', 'POST'])
    @login_required
    def receipts_create_route(budget_id):
        return receipts_routes.receipts_create(budget_id)

    @app.route('/budget/<int:budget_id>/receipts/<int:receipt_id>/edit', methods=['GET', 'POST'])
    @login_required
    def receipts_edit_route(budget_id,receipt_id):
        return receipts_routes.receipts_edit(budget_id,receipt_id)

    @app.route('/budget/<int:budget_id>/receipts/<int:receipt_id>/delete', methods=['POST'])
    @login_required
    def receipts_delete_route(budget_id, receipt_id):
        return receipts_routes.receipts_delete(budget_id,receipt_id)
    
    @app.route('/budget/<int:budget_id>/receipt_templates/view', methods=['GET'])
    @login_required
    def receipt_templates_view_route(budget_id):
        return receipts_routes.receipt_templates_view(budget_id)

    @app.route('/budget/<int:budget_id>/receipt_templates/<int:template_id>/edit', methods=['GET', 'POST'])
    @login_required
    def receipt_templates_edit_route(budget_id, template_id):
        return receipts_routes.receipt_templates_edit(budget_id, template_id)
    
    @app.route('/budget/<int:budget_id>/receipt_templates/<int:template_id>/delete', methods=['GET', 'POST'])
    @login_required
    def receipt_templates_delete_route(budget_id, template_id):
        return receipts_routes.receipt_templates_delete(budget_id, template_id)


########################## PAYMENT SOURCES ##########################
    @app.route('/budget/<int:budget_id>/payment_sources', methods=['GET', 'POST'])
    @login_required
    def payment_sources_home_route(budget_id):
        return payment_sources_routes.payment_sources_home(budget_id)

    @app.route('/budget/<int:budget_id>/payment_sources/view', methods=['GET', 'POST'])
    @login_required
    def payment_sources_view_route(budget_id):
        return payment_sources_routes.payment_sources_view(budget_id)

    @app.route('/budget/<int:budget_id>/payment_sources/create', methods=['GET', 'POST'])
    @login_required
    def payment_sources_create_route(budget_id):
        return payment_sources_routes.payment_sources_create(budget_id)

    @app.route('/budget/<int:budget_id>/payment_sources/<int:payment_source_id>/edit', methods=['GET', 'POST'])
    @login_required
    def payment_sources_edit_route(budget_id,payment_source_id):
        return payment_sources_routes.payment_sources_edit(budget_id,payment_source_id)

    @app.route('/budget/<int:budget_id>/payment_sources/<int:payment_source_id>/delete', methods=['POST'])
    @login_required
    def payment_sources_delete_route(budget_id, payment_source_id):
        return payment_sources_routes.payment_sources_delete(budget_id,payment_source_id)
