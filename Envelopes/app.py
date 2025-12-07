import os
import sys
from functions import setup, app_routing
from flask import Flask
# from flask_login import LoginManager
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, APP_SECKEY

app = Flask(__name__)
app.secret_key = APP_SECKEY

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

app_routing.register_routes(app)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        setup.first_time_init_db()
        print("Database initialized.")
        app.run(host='0.0.0.0', port=5000)
    else:
        print("Starting app")
        app.run(host='0.0.0.0', port=5000)