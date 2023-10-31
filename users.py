import datetime
from db_connection import engine
from sqlalchemy.orm import Session, Mapped, mapped_column, DeclarativeBase
from sqlalchemy import select, String, insert, update, delete
from flask import request, render_template, redirect
from authentication import requires_auth, Users

def configure_users_route(app):
    @app.route('/users_tasks.html')
    @requires_auth
    def users():
        with Session(engine) as session:
            current_user = request.authorization.username
            rows = session.execute(select(Users.id, Users.username, Users.password, Users.role))
            todos = []
            for row in rows:
                id, username, password, role = row
                todos.append({
                    'id': id,
                    'username': username,
                    'password': password,
                    'role': role
                })
            user_role = session.execute(select(Users.role).where(Users.username == current_user)).fetchone()
            user_is_admin = False
            if user_role[0] in ['Administrator', 'Super User']:
                user_is_admin = True

        return render_template('users_tasks.html', todos=todos, current_user=current_user, user_is_admin=user_is_admin)

    @app.route('/edit_users_tasks/<int:task_id>', methods=['GET', 'POST'])
    @requires_auth
    def edit_users_tasks(task_id):
        with Session(engine) as session:
            task = session.execute(select(Users.id,
                                          Users.username,
                                          Users.password,
                                          Users.role
                                          ).where(Users.id == task_id)).fetchone()
            if task:
                task = {'id': task.id,
                        'username': task.username,
                        'password': task.password,
                        'role': task.role}

                current_user = request.authorization.username
                with Session(engine) as session2:
                    user_role = session2.execute(select(Users.role).where(Users.username == current_user)).fetchone()
                    print(task['username'])
                    if user_role[0] in ['Administrator', 'Super User']:
                        print(type(user_role))
                        return render_template('edit_users_tasks.html', task=task, current_user=current_user)
                    else:
                        print(type(user_role))
                        return render_template('access_denied.html', current_user=current_user)
            else:
                # Handle case when task is not found.
                return "Task not found"

    @app.route('/edit_users_tasks_button', methods=['POST'])
    @requires_auth
    def edit_users_tasks_button():
        id = request.form['id']
        role = request.form['role']
        with engine.connect() as conn:
            conn.execute(
                update(Users)
                .where(Users.id == id)
                .values(role=role)
            )
            conn.commit()
        return redirect('/users_tasks.html')

    @app.route('/add_user_tasks', methods=['POST'])
    def add_user_tasks():
        username = request.form['username']
        password_1 = request.form['password_1']
        role = request.form['role']

        # Check if username already exist
        with engine.connect() as conn:
            existing_user = conn.execute(
                select(Users).where(Users.username == username)
            ).fetchone()

            if existing_user:
                return "<strong><h1>User already exists!<h1></strong>"'<a href="/users_tasks.html"><button>Back</button></a>'

            conn.execute(
                insert(Users), [
                    {"username": username,
                     "password": password_1,
                     "role": role}
                ]
            )
            conn.commit()

        return redirect('/users_tasks.html')

    @app.route('/edit_users_pass/<int:task_id>', methods=['GET', 'POST'])
    @requires_auth
    def edit_users_pass(task_id):
        with Session(engine) as session:
            task = session.execute(select(Users.id,
                                          Users.username,
                                          Users.password,
                                          Users.role
                                          ).where(Users.id == task_id)).fetchone()

            if task:
                task = {'id': task.id,
                        'username': task.username,
                        'password': task.password,
                        'role': task.role}

                current_user = request.authorization.username
                return render_template('edit_users_pass.html', task=task, current_user=current_user)
            else:
                # Handle case when task is not found.
                return "Task not found"

    @app.route('/edit_users_pass_button', methods=['POST'])
    @requires_auth
    def edit_users_pass_button():
        id = request.form['id']
        old_password = request.form['old_password']
        password_1 = request.form['password_1']

        with engine.connect() as conn:
            old_password_check = conn.execute(select(Users.password).where(Users.id == id)).fetchone()
            if old_password_check[0] == old_password:
                conn.execute(
                    update(Users)
                    .where(Users.id == id)
                    .values(password=password_1)
                )
                conn.commit()
        return redirect('/users_tasks.html')

    @app.route('/delete_users', methods=['POST'])
    def delete_users():
        id = request.form['id']
        with engine.connect() as conn:
            conn.execute(
                delete(Users)
                .where(Users.id == id)
            )
            conn.commit()
        return redirect('/users_tasks.html')
