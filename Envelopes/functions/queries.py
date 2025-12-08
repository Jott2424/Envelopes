########### Get ###########
GET_DEFAULT_BUDGET_BY_USER_ID = "SELECT fk_budgets_id FROM user_default_budget WHERE fk_users_id = %s"
GET_ENVELOPE_BY_NAME_AND_BUDGET_ID = "SELECT pk_envelopes_id FROM envelopes WHERE name = %s AND fk_budgets_id = %s"

########### Put ###########
INSERT_INTO_ENVELOPES = "INSERT INTO envelopes (fk_budgets_id, name) VALUES (%s, %s)"
INSERT_INTO_ENVELOPE_TRANSACTION_FIELDS = "INSERT INTO envelope_transaction_fields (fk_budgets_id, fk_envelopes_id, form_order, field_name, field_type, is_required) VALUES (%s,%s,%s,%s,%s,%s)"