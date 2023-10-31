import datetime
from db_connection import engine
from sqlalchemy.orm import Session, Mapped, mapped_column, DeclarativeBase
from sqlalchemy import select, String, insert, update, delete
from flask import request, render_template, redirect
from authentication import requires_auth, Users


class Base(DeclarativeBase):
    pass


class Vacations(Base):
    __tablename__ = "table_vacations"
    id:                 Mapped[int] = mapped_column(primary_key=True)
    target_location:    Mapped[str]
    target_date:        Mapped[str]
    possible_date:      Mapped[str]
    person_responsible: Mapped[str]
    expenses:           Mapped[int]
    note:               Mapped[str]
    status:             Mapped[str]

    def __repr__(self) -> str:
        return f"Vacations(\
        id={self.id!r},\
        expenses={self.expenses!r},\
            )"


def configure_vacations_route(app):
    @app.route('/vacations_tasks.html')
    @requires_auth
    def vacations_tasks():
        with Session(engine) as session:
            current_user = request.authorization.username
            rows = session.execute(
                select(Vacations.id,
                       Vacations.target_location,
                       Vacations.target_date,
                       Vacations.possible_date,
                       Vacations.person_responsible,
                       Vacations.expenses,
                       Vacations.note,
                       Vacations.status
                       )
            )
            html_input = []
            for row in rows:
                id, target_location, target_date, possible_date, person_responsible, expenses, note, status = row

                html_input.append({
                    'id': id,
                    'target_location': target_location,
                    'target_date': target_date,
                    'possible_date': possible_date,
                    'person_responsible': person_responsible,
                    'expenses': expenses,
                    'note': note,
                    'status': status
                })

        return render_template('vacations_tasks.html', html_input=html_input, current_user=current_user, current_datetime=datetime.datetime.now())














































