from sqlalchemy import create_engine, select
from users import Users
from todo import ToDo
from shopping import Shopping

engine_sqlite = create_engine('sqlite:///database.db')
engine_postgresql = create_engine('postgresql://postgres:ZWOiN2KYZj3C4Dq3n1swOosDsZWcx@18.193.123.132/pd_database')


with engine_sqlite.begin() as conn_sqlite, engine_postgresql.begin() as conn_postgresql:
    rows = conn_sqlite.execute(select(Shopping)).fetchall()

    for row in rows:
        row_dict = row._asdict()
        conn_postgresql.execute(Shopping.__table__.insert().values(**row_dict))