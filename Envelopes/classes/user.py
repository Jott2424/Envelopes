from functions import db_utils
import psycopg2
from flask_login import UserMixin


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id_, username):
        self.id = id_
        self.username = username

    @staticmethod
    def get(user_id):
        conn = db_utils.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            return User(user[0], user[1])
        return None