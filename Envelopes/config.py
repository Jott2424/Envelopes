import os

# Replace with your PostgreSQL credentials
DB_NAME = os.environ.get('DB_NAME', 'envelopes')
DB_USER = os.environ.get('DB_USER', 'envelopes')
DB_PASS = os.environ.get('DB_PASS', 'envelopes')
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('DB_PORT', '17501')
APP_SECKEY = os.environ.get('APP_SECKEY', 'supersecretkey')
