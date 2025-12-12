import psycopg2
from functions import db_utils

# first time db init
def first_time_init_db():
    conn = db_utils.get_db_connection()
    cur = conn.cursor()
    #who can use the app
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            pk_users_id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    ''')
    #a distinct budget with plans for money coming in and going out
    cur.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            pk_budgets_id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );
    ''')
    #which users have access to which budgets
    cur.execute('''
        CREATE TABLE IF NOT EXISTS budget_users (
            pk_budget_users_id SERIAL PRIMARY KEY,
            fk_budgets_id INTEGER REFERENCES budgets(pk_budgets_id),
            fk_users_id INTEGER REFERENCES users(pk_users_id)
        );
    ''')
    #the default budget for each user on home
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_default_budget (
            pk_user_default_budget_id SERIAL PRIMARY KEY,
            fk_budgets_id INTEGER REFERENCES budgets(pk_budgets_id),
            fk_users_id INTEGER REFERENCES users(pk_users_id)
        );
    ''')
    #accounts that money can physically be spent from
    cur.execute('''
        CREATE TABLE IF NOT EXISTS payment_sources (
            pk_payment_sources_id SERIAL PRIMARY KEY,
            fk_budgets_id INTEGER REFERENCES budgets(pk_budgets_id),
            name TEXT NOT NULL
        );
    ''')
    #envelopes are categories that money is being budgeted towards
    cur.execute('''
        CREATE TABLE IF NOT EXISTS envelopes (
            pk_envelopes_id SERIAL PRIMARY KEY,
            fk_budgets_id INTEGER REFERENCES budgets(pk_budgets_id),
            name TEXT NOT NULL
        );
    ''')
    #which fields does each envelope want to track for each transaction
    cur.execute('''
        CREATE TABLE IF NOT EXISTS envelope_transaction_fields (
            pk_envelope_transaction_fields_id SERIAL PRIMARY KEY,
            fk_envelopes_id INTEGER REFERENCES envelopes(pk_envelopes_id),
            form_order INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            field_type TEXT NOT NULL,
            is_required BOOLEAN NOT NULL
        );
    ''')
    #a receipt can have multiple envelope deductions (transactions)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            pk_receipts_id SERIAL PRIMARY KEY,
            fk_budgets_id INTEGER REFERENCES budgets(pk_budgets_id),
            fk_users_id INTEGER REFERENCES users(pk_users_id),
            fk_payment_sources_id INTEGER REFERENCES payment_sources(pk_payment_sources_id),
            debit_or_credit TEXT NOT NULL
        );
    ''')
    #a receipt can have multiple envelope deductions (transactions)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            pk_transactions_id SERIAL PRIMARY KEY,
            fk_receipts_id INTEGER REFERENCES receipts(pk_receipts_id),
            fk_envelopes_id INTEGER REFERENCES envelopes(pk_envelopes_id),
            details JSONB NOT NULL
        );
    ''')
    # # table for storing presets for depositing money into envelopes
    # cur.execute('''
    #     CREATE TABLE IF NOT EXISTS user_envelope_deposit_presets (
    #         pk_user_envelope_deposit_presets_id SERIAL PRIMARY KEY,
    #         fk_budgets_id INTEGER REFERENCES budgets(pk_budgets_id),
    #         fk_users_id INTEGER REFERENCES users(pk_users_id),
    #         fk_envelopes_id INTEGER REFERENCES envelopes(pk_envelopes_id),
    #         fk_account_id INTEGER REFERENCES accounts(pk_accounts_id),
    #         amount NUMERIC(10,2) NOT NULL,
    #         description TEXT
    #     );
    # ''')
    # #table for storing settings for each user
    # cur.execute('''
    #     CREATE TABLE IF NOT EXISTS user_settings (
    #         fk_users_id INTEGER REFERENCES users(pk_users_id),
    #         settings TEXT NOT NULL,
    #         PRIMARY KEY (fk_users_id, settings)
    #     );
    # ''')


    conn.commit()
    cur.close()
    conn.close()