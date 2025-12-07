import psycopg2
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )


