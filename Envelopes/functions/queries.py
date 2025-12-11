########### Get ###########
GET_ALL_BUDGETS = "SELECT * FROM budgets"
GET_BUDGET_BY_NAME = "SELECT pk_budgets_id FROM budgets WHERE name = %s"
GET_USERS_BY_NAME = "SELECT pk_users_id, name, password FROM users WHERE name = %s"
GET_DEFAULT_BUDGET_BY_USER_ID = "SELECT fk_budgets_id FROM user_default_budget WHERE fk_users_id = %s"
GET_ENVELOPE_BY_NAME_AND_BUDGET_ID = "SELECT pk_envelopes_id FROM envelopes WHERE name = %s AND fk_budgets_id = %s"
GET_USER_ALLOWED_BUDGETS_BY_USER_ID = "SELECT pk_budget_users_id FROM budget_users WHERE fk_users_id = %s"
GET_ENVELOPE_TRANSACTION_FIELDS_BY_BUDGET_AND_ENVELOPE_ID = "SELECT pk_envelope_transaction_fields_id, fk_budgets_id, fk_envelopes_id, form_order, field_name, field_type, is_required FROM envelope_transaction_fields WHERE fk_budgets_id = %s and fk_envelopes_id = %s"

########### Get With Join ###########
GET_BUDGET_NAME_BY_BUDGET_USERS = "SELECT b.pk_budgets_id, b.name FROM budgets b JOIN budget_users bu ON b.pk_budgets_id = bu.fk_budgets_id WHERE bu.fk_users_id = %s"
GET_USERS_NOT_ALREADY_IN_BUDGET_USERS_BY_USER_ID = "SELECT u.pk_users_id, u.name FROM users u WHERE u.pk_users_id != %s AND u.pk_users_id NOT IN (SELECT fk_users_id FROM budget_users WHERE fk_budgets_id = %s)"
GET_ENVELOPES_AND_TRANSACTION_FIELDS_BY_BUDGET_ID = "SELECT e.pk_envelopes_id, e.name, etf.form_order, etf.field_name, etf.field_type, etf.is_required FROM envelope_transaction_fields etf JOIN envelopes e ON etf.fk_envelopes_id = e.pk_envelopes_id WHERE etf.fk_budgets_id = %s"
GET_ENVELOPE_NAME_AND_TRANSACTION_FIELDS_BY_BUDGET_AND_ENVELOPE_ID = "SELECT e.name, pk_envelope_transaction_fields_id, etf.fk_budgets_id, fk_envelopes_id, form_order, field_name, field_type, is_required FROM envelope_transaction_fields etf JOIN envelopes e ON e.pk_envelopes_id = fk_envelopes_id WHERE etf.fk_budgets_id = %s and fk_envelopes_id = %s"

########### Put ###########
INSERT_INTO_ENVELOPES = "INSERT INTO envelopes (fk_budgets_id, name) VALUES (%s, %s)"
INSERT_INTO_BUDGETS   = "INSERT INTO budgets (name) VALUES (%s)"
INSERT_INTO_ENVELOPE_TRANSACTION_FIELDS = "INSERT INTO envelope_transaction_fields (fk_budgets_id, fk_envelopes_id, form_order, field_name, field_type, is_required) VALUES (%s,%s,%s,%s,%s,%s)"
INSERT_INTO_USER_DEFAULT_BUDGETS = "INSERT INTO user_default_budget (fk_users_id, fk_budgets_id) VALUES (%s, %s)"
INSERT_INTO_BUDGET_USERS = "INSERT INTO budget_users (fk_budgets_id, fk_users_id) VALUES (%s, %s)"

########### Put With Return ###########
INSERT_INTO_USERS_RETURN_PK = "INSERT INTO users (name, password) VALUES (%s, %s) RETURNING pk_users_id"
INSERT_INTO_BUDGETS_RETURN_PK = "INSERT INTO budgets (name) VALUES (%s) RETURNING pk_budgets_id"
INSERT_INTO_ENVELOPES_RETURN_PK = "INSERT INTO envelopes (fk_budgets_id, name) VALUES (%s, %s) RETURNING pk_envelopes_id"

########### PATCH ###########
UPDATE_USER_DEFAULT_BUDGET_BY_USER_ID = "UPDATE user_default_budget SET fk_budgets_id = %s WHERE fk_users_id = %s"
UPDATE_ENVELOPES_BY_ENVELOPES_ID = "UPDATE envelopes SET name = %s WHERE pk_envelopes_id = %s"

########### DROP ###########
DROP_FROM_ENVELOPE_TRANSACTION_FIELDS_BY_BUDGETS_AND_ENVELOPES_ID = "DELETE FROM envelope_transaction_fields WHERE fk_budgets_id = %s AND fk_envelopes_id = %s"
DROP_FROM_ENVELOPES_BY_BUDGETS_AND_ENVELOPES_ID = "DELETE FROM envelopes WHERE pk_envelopes_id = %s AND fk_budgets_id = %s"
DROP_FROM_TRANSACTIONS_BY_BUDGETS_AND_ENVELOPES_ID = "DELETE FROM envelope_transactions WHERE fk_budgets_id = %s AND fk_envelopes_id = %s"