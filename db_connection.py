from decouple import config
from sqlalchemy import create_engine

db_password = config('DB_PASSWORD')

engine = create_engine(f'postgresql://postgres:{db_password}@localhost/pg_database')


"""
engine = create_engine("sqlite+pysqlite:///database.db")
engine = create_engine('postgresql://postgres:password@localhost/pg_database')
"""
