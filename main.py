import datetime
from flask import Flask, render_template, redirect, request, Response
from sqlalchemy import select, String, insert, update, delete
from sqlalchemy.orm import Session, Mapped, mapped_column, DeclarativeBase
from authentication import configure_logout
from db_connection import engine
from index import configure_index_route
from todo import ToDo, configure_todo_route
from shopping import configure_shoping_route
from users import configure_users_route

current_datetime = datetime.datetime.now()


# class Base(DeclarativeBase):
#     pass


app = Flask(__name__)

configure_logout(app)

# Start index.html backend logic
configure_index_route(app)
# End index.html backend logic


# Start todo_tasks.html backend logic
configure_todo_route(app)
# End_ToDo_task_list


# Start shoping tasks
configure_shoping_route(app)
# Start Users section


# Start users task
configure_users_route(app)
# End users tasks


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
