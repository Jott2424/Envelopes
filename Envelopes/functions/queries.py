########### Get ###########
GET_ALL_BUDGETS = "SELECT * FROM budgets"
GET_BUDGET_BY_NAME = "SELECT pk_budgets_id FROM budgets WHERE name = %s"
GET_USERS_BY_NAME = "SELECT pk_users_id, name, password FROM users WHERE name = %s"
GET_DEFAULT_BUDGET_BY_USER_ID = "SELECT fk_budgets_id FROM user_default_budget WHERE fk_users_id = %s"
GET_ENVELOPE_BY_NAME_AND_BUDGET_ID = "SELECT pk_envelopes_id FROM envelopes WHERE name = %s AND fk_budgets_id = %s"
GET_USER_ALLOWED_BUDGETS_BY_USER_ID = "SELECT pk_budget_users_id FROM budget_users WHERE fk_users_id = %s"
GET_ENVELOPE_TRANSACTION_FIELDS_BY_BUDGET_AND_ENVELOPE_ID = "SELECT pk_envelope_transaction_fields_id, fk_budgets_id, fk_envelopes_id, form_order, field_name, field_type, is_required FROM envelope_transaction_fields WHERE fk_budgets_id = %s AND fk_envelopes_id = %s"
GET_PAYMENT_SOURCES_BY_BUDGET_ID = "SELECT pk_payment_sources_id, name FROM payment_sources WHERE fk_budgets_id = %s"
GET_PAYMENT_SOURCES_BY_BUDGET_ID_AND_NAME = "SELECT pk_payment_sources_id, name FROM payment_sources WHERE fk_budgets_id = %s AND name = %s"
GET_PAYMENT_SOURCE_BY_PAYMENT_SOURCE_ID = "SELECT pk_payment_sources_id, name FROM payment_sources WHERE pk_payment_sources_id = %s"
GET_RECEIPT_TEMPLATES_ID_AND_DESCRIPTIONS = "SELECT pk_receipt_templates_id, description FROM receipts_templates"
GET_RECEIPT_BY_PK = "SELECT pk_receipts_id, fk_payment_sources_id, debit_or_credit, transaction_date, merchant, description FROM receipts WHERE pk_receipts_id = %s"
GET_ENVELOPE_NAMES_BY_ID = "SELECT pk_envelopes_id, name FROM envelopes WHERE pk_envelopes_id = ANY(%s)"

########### Get With Join ###########
GET_BUDGET_NAME_BY_BUDGET_USERS = "SELECT b.pk_budgets_id, b.name FROM budgets b JOIN budget_users bu ON b.pk_budgets_id = bu.fk_budgets_id WHERE bu.fk_users_id = %s"
GET_USERS_NOT_ALREADY_IN_BUDGET_USERS_BY_USER_ID = "SELECT u.pk_users_id, u.name FROM users u WHERE u.pk_users_id != %s AND u.pk_users_id NOT IN (SELECT fk_users_id FROM budget_users WHERE fk_budgets_id = %s)"
GET_ENVELOPES_AND_TRANSACTION_FIELDS_BY_BUDGET_ID = "SELECT e.pk_envelopes_id, e.name, etf.form_order, etf.field_name, etf.field_type, etf.is_required FROM envelope_transaction_fields etf JOIN envelopes e ON etf.fk_envelopes_id = e.pk_envelopes_id WHERE e.fk_budgets_id = %s"
GET_ENVELOPE_NAME_AND_TRANSACTION_FIELDS_BY_BUDGET_AND_ENVELOPE_ID = "SELECT e.name, pk_envelope_transaction_fields_id, e.fk_budgets_id, fk_envelopes_id, form_order, field_name, field_type, is_required FROM envelope_transaction_fields etf JOIN envelopes e ON e.pk_envelopes_id = fk_envelopes_id WHERE e.fk_budgets_id = %s AND fk_envelopes_id = %s"
GET_ENVELOPE_NAME_AND_TRANSACTION_FIELDS_EXCLUDING_AMOUNT_BY_BUDGET_AND_ENVELOPE_ID = "SELECT e.name, pk_envelope_transaction_fields_id, e.fk_budgets_id, fk_envelopes_id, form_order, field_name, field_type, is_required FROM envelope_transaction_fields etf JOIN envelopes e ON e.pk_envelopes_id = fk_envelopes_id WHERE e.fk_budgets_id = %s AND fk_envelopes_id = %s AND lower(field_name) NOT IN ('amount','description') "
GET_ENVELOPES_NAME_AND_TRANSACTION_FIELDS_BY_BUDGET = "SELECT e.name, fk_envelopes_id, form_order, field_name, field_type, is_required FROM envelope_transaction_fields etf JOIN envelopes e ON e.pk_envelopes_id = fk_envelopes_id WHERE e.fk_budgets_id = %s"
GET_RECEIPT_TEMPLATES_AND_PAYMENT_SOURCES_BY_BUDGETS_ID = "SELECT rt.pk_receipt_templates_id, rt.description, rt.debit_or_credit, ps.name as payment_source_name FROM receipt_templates rt LEFT JOIN payment_sources ps ON ps.pk_payment_sources_id = rt.fk_payment_sources_id WHERE rt.fk_budgets_id = %s"
GET_RECEIPTS_AND_PAYMENT_SOURCES_BY_BUDGETS_ID = "SELECT r.pk_receipts_id, r.description, r.debit_or_credit, r.transaction_date, r.amount, ps.name as payment_source_name FROM receipts r LEFT JOIN payment_sources ps ON ps.pk_payment_sources_id = r.fk_payment_sources_id WHERE r.fk_budgets_id = %s"
GET_RECEIPT_TEMPLATES_BY_RECEIPT_TEMPLATES_ID = "SELECT pk_receipt_templates_id, fk_payment_sources_id, debit_or_credit, merchant, description FROM receipt_templates WHERE pk_receipt_templates_id = %s"
GET_TRANSACTION_TEMPLATES_BY_RECEIPT_TEMPLATES_ID = "SELECT fk_envelopes_id AS envelope_id, details FROM transaction_templates WHERE fk_receipt_templates_id = %s ORDER BY pk_transaction_templates_id"
GET_TRANSACTIONS_BY_RECEIPT_ID = "SELECT fk_envelopes_id, details FROM transactions WHERE fk_receipts_id = %s ORDER BY pk_transactions_id"

########### Put ###########
INSERT_INTO_ENVELOPES = "INSERT INTO envelopes (fk_budgets_id, name) VALUES (%s, %s)"
INSERT_INTO_BUDGETS   = "INSERT INTO budgets (name) VALUES (%s)"
INSERT_INTO_ENVELOPE_TRANSACTION_FIELDS = "INSERT INTO envelope_transaction_fields (fk_envelopes_id, form_order, field_name, field_type, is_required) VALUES (%s,%s,%s,%s,%s)"
INSERT_INTO_USER_DEFAULT_BUDGETS = "INSERT INTO user_default_budget (fk_users_id, fk_budgets_id) VALUES (%s, %s)"
INSERT_INTO_BUDGET_USERS = "INSERT INTO budget_users (fk_budgets_id, fk_users_id) VALUES (%s, %s)"
INSERT_INTO_PAYMENT_SOURCES = "INSERT INTO payment_sources (fk_budgets_id, name) VALUES (%s, %s)"
INSERT_INTO_TRANSACTIONS = "INSERT INTO transactions (fk_receipts_id, fk_envelopes_id, details) VALUES (%s, %s, %s)"
INSERT_INTO_TRANSACTION_TEMPLATES = "INSERT INTO transaction_templates (fk_receipt_templates_id, fk_envelopes_id, details) VALUES (%s, %s, %s)"

########### Put With Return ###########
INSERT_INTO_USERS_RETURN_PK = "INSERT INTO users (name, password) VALUES (%s, %s) RETURNING pk_users_id"
INSERT_INTO_BUDGETS_RETURN_PK = "INSERT INTO budgets (name) VALUES (%s) RETURNING pk_budgets_id"
INSERT_INTO_ENVELOPES_RETURN_PK = "INSERT INTO envelopes (fk_budgets_id, name) VALUES (%s, %s) RETURNING pk_envelopes_id"
INSERT_INTO_PAYMENT_SOURCES_RETURN_PK = "INSERT INTO payment_sources (fk_budgets_id, name) VALUES (%s, %s) RETURNING pk_payment_sources_id"
INSERT_INTO_RECEIPTS_RETURN_PK = "INSERT INTO receipts (fk_budgets_id, fk_users_id, fk_payment_sources_id, debit_or_credit, transaction_date, merchant, amount, description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING pk_receipts_id"
INSERT_INTO_RECEIPT_TEMPLATES_RETURN_PK = "INSERT INTO receipt_templates (fk_budgets_id, fk_users_id, fk_payment_sources_id, debit_or_credit, merchant, description) VALUES (%s,%s,%s,%s,%s,%s) RETURNING pk_receipt_templates_id"

########### PATCH ###########
UPDATE_USER_DEFAULT_BUDGET_BY_USER_ID = "UPDATE user_default_budget SET fk_budgets_id = %s WHERE fk_users_id = %s"
UPDATE_ENVELOPES_BY_ENVELOPES_ID = "UPDATE envelopes SET name = %s WHERE pk_envelopes_id = %s"
UPDATE_PAYMENT_SOURCES_BY_PAYMENT_SOURCE_ID = "UPDATE payment_sources SET name = %s WHERE pk_payment_sources_id = %s"
UPDATE_RECEIPT_TEMPLATES_BY_PK = "UPDATE receipt_templates SET merchant=%s, debit_or_credit=%s, fk_payment_sources_id=%s, description=%s WHERE pk_receipt_templates_id=%s"
UPDATE_RECEIPT_BY_PK = "UPDATE receipts SET fk_payment_sources_id = %s, debit_or_credit = %s, transaction_date = %s, merchant = %s, amount = %s, description = %s WHERE pk_receipts_id = %s"

########### DROP ###########
DROP_FROM_ENVELOPE_TRANSACTION_FIELDS_BY_ENVELOPES_ID = "DELETE FROM envelope_transaction_fields WHERE fk_envelopes_id = %s"
DROP_FROM_ENVELOPES_BY_ENVELOPES_ID = "DELETE FROM envelopes WHERE pk_envelopes_id = %s"
DROP_FROM_TRANSACTIONS_BY_ENVELOPES_ID = "DELETE FROM transactions WHERE fk_envelopes_id = %s"
DROP_FROM_RECEIPTS_BY_ENVELOPES_ID = "DELETE FROM receipts WHERE fk_envelopes_id = %s"
DROP_FROM_PAYMENT_SOURCES_BY_PAYMENT_SOURCES_ID = "DELETE FROM payment_sources WHERE pk_payment_sources_id = %s"
DROP_FROM_TRANSACTIONS_BY_PAYMENT_SOURCES_ID = "DELETE FROM transactions WHERE fk_receipts_id IN (SELECT pk_receipts_id FROM receipts WHERE fk_payment_source_id = %s)"
DROP_FROM_RECEIPTS_BY_PAYMENT_SOURCES_ID = "DELETE FROM receipts WHERE fk_payment_source_id = %s"
DROP_FROM_RECEIPT_TEMPLATES_BY_PK = "DELETE FROM receipt_templates WHERE pk_receipt_templates_id=%s"
DROP_FROM_TRANSACTION_TEMPLATES_BY_FK = "DELETE FROM transaction_templates WHERE fk_receipt_templates_id=%s"
DROP_FROM_RECEIPTS_BY_PK = "DELETE FROM receipts WHERE pk_receipts_id = %s"
DROP_FROM_TRANSACTIONS_BY_FK = "DELETE FROM transactions WHERE fk_receipts_id = %s"

################ LEDGER
GET_LEDGER_WEEKLY_SUMS = """-- Get sums of debit/credit per envelope per week
-- Query: Get transactions grouped by week and envelope
WITH all_receipts AS (
    SELECT
        r.pk_receipts_id,
        r.transaction_date,
        r.debit_or_credit,
        t.fk_envelopes_id,
        (t.details->>'amount')::numeric AS amount
    FROM receipts r
    JOIN transactions t ON t.fk_receipts_id = r.pk_receipts_id
    WHERE r.fk_budgets_id = %s
),
week_ranges AS (
    SELECT
        generate_series(
            date_trunc('month', date '%s-%s-01')::date,
            (date_trunc('month', date '%s-%s-01') + interval '1 month - 1 day')::date,
            interval '1 day'
        )::date AS d
),
weeks_with_sunday AS (
    SELECT
        d,
        (d - extract(dow from d)::int) AS week_start -- Sunday
    FROM week_ranges
),
week_assignment AS (
    SELECT
        r.pk_receipts_id,
        r.fk_envelopes_id,
        r.debit_or_credit,
        r.amount,
        -- Compute week number and label based on majority month rule
        (date_trunc('week', r.transaction_date) + interval '1 day')::date AS week_start,
        (date_trunc('week', r.transaction_date) + interval '7 day')::date AS week_end
    FROM all_receipts r
)
SELECT
    to_char(wa.week_start, 'YYYY-MM-DD') || ' - ' || to_char(wa.week_end, 'YYYY-MM-DD') AS week_label,
    wa.fk_envelopes_id,
    SUM(CASE WHEN wa.debit_or_credit='debit' THEN wa.amount ELSE 0 END) AS debit,
    SUM(CASE WHEN wa.debit_or_credit='credit' THEN wa.amount ELSE 0 END) AS credit
FROM week_assignment wa
GROUP BY 1, 2
ORDER BY 1 ASC;
"""