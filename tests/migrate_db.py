from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, Mapped, mapped_column, DeclarativeBase

engine_sqlite = create_engine('sqlite:///database.db')
engine_postgresql = create_engine('postgresql://postgres:password@localhost/database')


class Base(DeclarativeBase):
    pass


class ToDo(Base):
    __tablename__ = "table_todo"
    id: Mapped[int] = mapped_column(primary_key=True)
    task: Mapped[str]
    person_responsible: Mapped[str]
    planned_due_date: Mapped[str]
    status: Mapped[str]
    date: Mapped[str]

with engine_sqlite.begin() as conn_sqlite, engine_postgresql.begin() as conn_postgresql:
    rows = conn_sqlite.execute(select(ToDo)).fetchall()

    for row in rows:
        row_dict = row._asdict()
        conn_postgresql.execute(ToDo.__table__.insert().values(**row_dict))
