from sqlalchemy.orm import Session, Mapped, mapped_column, DeclarativeBase
from sqlalchemy import select, String
from typing import Optional
from functools import wraps
from flask import request, Response
from db_connection import engine



class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "table_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String)
    password: Mapped[Optional[str]]
    role: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, password={self.password!r}, role={self.role!r})"


def check_auth(username, password):
    with Session(engine) as session:
        rows = session.execute(select(Users.username, Users.password)).fetchall()
        for row in rows:
            # print(row)
            if row == (username, password):
                return rows is not None


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def configure_logout(app):
    @app.route('/logout')
    def logout():
        return Response(
            'Logged out successfully',
            401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        )

