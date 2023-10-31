import datetime
from db_connection import engine
from sqlalchemy.orm import Session, Mapped, mapped_column, DeclarativeBase
from sqlalchemy import select, String, insert, update, delete
from flask import request, render_template, redirect
from authentication import requires_auth, Users


class Base(DeclarativeBase):
    pass


class ToDo(Base):
    __tablename__ = "table_todo"
    id: Mapped[int] = mapped_column(primary_key=True)
    task: Mapped[str] = mapped_column(String)
    person_responsible: Mapped[str] = mapped_column(String)
    planned_due_date: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    date: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"ToDo(\
        id={self.id!r}, \
        task={self.task!r}, \
        person_responsible={self.person_responsible!r}, \
        planned_due_date={self.planned_due_date!r}, \
        status={self.status!r}, \
        date={self.date!r}, \
         )"


def configure_todo_route(app):
    @app.route('/todo_tasks.html')
    @requires_auth
    def todo_tasks():
        with Session(engine) as session:
            current_user = request.authorization.username
            rows = session.execute(
                select(ToDo.id, ToDo.task, ToDo.person_responsible, ToDo.planned_due_date, ToDo.status,
                       ToDo.date)).fetchall()
            todos = []
            for row in rows:
                id, task, person_responsible, planned_due_date, status, date = row
                planned_due_date = datetime.datetime.strptime(planned_due_date,
                                                              '%Y-%m-%d %H:%M')  # Remove :%S and etc...
                todos.append({
                    'id': id,
                    'task': task,
                    'person_responsible': person_responsible,
                    'planned_due_date': planned_due_date,
                    'status': status,
                    'date': date
                })
            users = session.execute(select(Users.username))
            users_list = []
            for row in users:
                user = row
                if user[0] not in ['root', 'admin']:
                    users_list.append({
                        'user': user
                    })

        return render_template('todo_tasks.html', todos=todos, current_user=current_user,
                               current_datetime=datetime.datetime.now(), users_list=users_list)

    @app.route('/add_todo_tasks', methods=['POST'])
    @requires_auth
    def add_todo_tasks():
        task = request.form['task']
        responsible = request.form['responsible']
        planned_due_date = request.form['planned_due_date']
        status = 'to be done'
        with engine.connect() as conn:
            result = conn.execute(
                insert(ToDo),
                [
                    {"task": task,
                     "person_responsible": responsible,
                     "planned_due_date": planned_due_date,
                     "status": status,
                     },
                ],
            )
            conn.commit()
        return redirect('/todo_tasks.html')

    def update_task_status(status, id, date=None):
        if date is not None:
            with engine.connect() as conn:
                conn.execute(
                    update(ToDo)
                    .where(ToDo.id == id)
                    .values(status=status, date=date)
                )
                conn.commit()
        else:
            with engine.connect() as conn:
                conn.execute(
                    update(ToDo)
                    .where(ToDo.id == id)
                    .values(status=status)
                )
                conn.commit()

        return redirect('/todo_tasks.html')

    @app.route('/in_plan', methods=['POST'])
    def in_plan():
        id = request.form['id']
        return update_task_status('in progress', id)

    @app.route('/in_progres', methods=['POST'])
    def in_progres():
        id = request.form['id']
        return update_task_status('delayed', id)

    @app.route('/in_delayed', methods=['POST'])
    def in_delayed():
        id = request.form['id']
        return update_task_status('done', id)

    @app.route('/in_done', methods=['POST'])
    def in_done():
        id = request.form['id']
        date = datetime.datetime.now()
        return update_task_status('done_final', id, date)

    @app.route('/return_to_list_todo', methods=['POST'])
    def return_to_list_todo():
        id = request.form['id']
        date = datetime.datetime.now()
        return update_task_status('to be done', id, date)

    @app.route('/delete_todo', methods=['POST'])
    def delete_todo():
        id = request.form['id']
        with engine.connect() as conn:
            conn.execute(
                delete(ToDo)
                .where(ToDo.id == id)
            )
            conn.commit()
        return redirect('/todo_tasks.html')

    @app.route('/edit_todo_tasks/<int:task_id>', methods=['GET', 'POST'])
    @requires_auth
    def edit_todo_tasks(task_id):
        with Session(engine) as session:
            task = session.execute(select(ToDo.id,
                                          ToDo.task,
                                          ToDo.person_responsible,
                                          ToDo.planned_due_date,
                                          ToDo.status,
                                          ToDo.date
                                          ).where(ToDo.id == task_id)).fetchone()

            if task:
                task = {'id': task.id,
                        'task': task.task,
                        'person_responsible': task.person_responsible,
                        'planned_due_date': task.planned_due_date,
                        'status': task.status,
                        'date': task.date}

                current_user = request.authorization.username
                users = session.execute(select(Users.username))
                users_list = []
                for row in users:
                    user = row
                    if user[0] not in ['root', 'admin']:
                        users_list.append({
                            'user': user
                        })

                return render_template('edit_todo_tasks.html', task=task, current_user=current_user,
                                       users_list=users_list)
            else:
                # Handle case when task is not found.
                return "Task not found"

    @app.route('/edit_todo_tasks_button', methods=['POST'])
    @requires_auth
    def add_todo_tasks_button():
        id = request.form['id']
        task = request.form['task']
        person_responsible = request.form['person_responsible']
        planned_due_date = request.form['planned_due_date']
        status = request.form['status']
        date = request.form['date']

        with engine.connect() as conn:
            conn.execute(
                update(ToDo)
                .where(ToDo.id == id)
                .values(task=task,
                        person_responsible=person_responsible,
                        planned_due_date=planned_due_date,
                        status=status,
                        date=date)
            )
            conn.commit()
        return redirect('/todo_tasks.html')
