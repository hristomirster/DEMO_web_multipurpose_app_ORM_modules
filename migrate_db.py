from sqlalchemy import create_engine, select
from users import Users
from todo import ToDo
from shopping import Shopping

engine_sqlite = create_engine('sqlite:///database.db')
# engine_postgresql = create_engine('postgresql://postgres:ZWOiN2KYZj3C4Dq3n1swOosDsZWcx@18.193.123.132/pd_database')
engine_postgresql = create_engine('postgresql://postgres:ZWOiN2KYZj3C4Dq3n1swOosDsZWcx@localhost/pg_database')


with engine_sqlite.begin() as conn_sqlite, engine_postgresql.begin() as conn_postgresql:
    rows = conn_sqlite.execute(select(ToDo)).fetchall()

    for row in rows:
        row_dict = row._asdict()
        conn_postgresql.execute(ToDo.__table__.insert().values(**row_dict))
