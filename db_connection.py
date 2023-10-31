from sqlalchemy import create_engine

engine = create_engine('postgresql://postgres:ZWOiN2KYZj3C4Dq3n1swOosDsZWcx@localhost/pg_database')


"""
engine = create_engine("sqlite+pysqlite:///database.db")
engine = create_engine('postgresql://postgres:password@localhost/pg_database')
"""
