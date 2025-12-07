import os
import setup
from 
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, APP_SECKEY

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        setup.first_time_init_db()
        print("Database initialized.")
    else:
        print("Starting app")
        app.run(host='0.0.0.0', port=5000)