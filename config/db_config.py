import psycopg2
from config.settings import DATABASE_URL_PG

def get_db_connection():
    return psycopg2.connect(DATABASE_URL_PG)
