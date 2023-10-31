import datetime
from flask import Flask, render_template, redirect, request, Response
from sqlalchemy import create_engine, select, String,insert, update, delete
from sqlalchemy.orm import Session, Mapped, mapped_column, DeclarativeBase
from functools import wraps
from typing import Optional

current_datetime = datetime.datetime.now()

engine = create_engine("sqlite+pysqlite:///database.db", echo=True)

class Base(DeclarativeBase):
    pass


app = Flask(__name__)


# Authentication section start
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

# print(check_auth("hristo", "pass"))  test with hc credentials ...


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


@app.route('/logout')
def logout():
    return Response(
        'Logged out successfully',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )
# Authentication section end


# Start index.html backend logic
@app.route('/')
@requires_auth
def index():
    current_user = request.authorization.username  # Get the logged-in user(name)
    return render_template("index.html", current_user=current_user)
# End index.html backend logic


# Start todo_tasks.html backend logic \
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


@app.route('/todo_tasks.html')
@requires_auth
def todo_tasks():
    with Session(engine) as session:
        current_user = request.authorization.username
        rows = session.execute(select(ToDo.id, ToDo.task, ToDo.person_responsible, ToDo.planned_due_date, ToDo.status, ToDo.date)).fetchall()
        todos = []
        for row in rows:
            id, task, person_responsible, planned_due_date, status, date = row
            planned_due_date = datetime.datetime.strptime(planned_due_date, '%Y-%m-%d %H:%M')  # Remove :%S and etc...
            todos.append({
                'id': id,
                'task': task,
                'person_responsible': person_responsible,
                'planned_due_date': planned_due_date,
                'status': status,
                'date': date
            })

    return render_template('todo_tasks.html', todos=todos, current_user=current_user, current_datetime=datetime.datetime.now())


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
                .values(status = status, date = date)
            )
            conn.commit()
    else:
        with engine.connect() as conn:
            conn.execute(
                update(ToDo)
                .where(ToDo.id == id)
                .values(status = status)
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
            return render_template('edit_todo_tasks.html', task=task, current_user=current_user)
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
            .values(task = task,
                    person_responsible = person_responsible,
                    planned_due_date = planned_due_date,
                    status = status,
                    date = date)
        )
        conn.commit()
    return redirect('/todo_tasks.html')



# End_ToDo_task_list









# Start shoping tasks
class Shopping(Base):
    __tablename__ = "table_shoping"
    id:             Mapped[int] = mapped_column(primary_key=True)
    goods:          Mapped[str]
    price:          Mapped[int]
    status:         Mapped[str]
    note:           Mapped[str]
    date:           Mapped[str]
    date_update:    Mapped[str]
    type:           Mapped[str]
    user_account:   Mapped[str]

    def __repr__(self) -> str:
        return f"Shopping(\
        id={self.id!r}, \
        goods={self.goods!r}, \
        price={self.price!r}, \
        status={self.status!r}, \
        note={self.note!r}, \
        date={self.date!r}, \
        date_update={self.date_update!r}, \
        type={self.type!r}, \
        user_account={self.user_account!r}, \
         )"


@app.route('/shoping_tasks.html')
@requires_auth
def shoping_tasks():
    with Session(engine) as session:
        current_user = request.authorization.username
        rows = session.execute(select(Shopping.id,
                                      Shopping.goods,
                                      Shopping.price,
                                      Shopping.status,
                                      Shopping.note,
                                      Shopping.date,
                                      Shopping.date_update,
                                      Shopping.type,
                                      Shopping.user_account)).fetchall()
        todos = []
        for row in rows:
            id, goods, price, status, note , date, date_update, type, user_account = row
            todos.append({
                'id': id,
                'goods': goods,
                'price': price,
                'status': status,
                'note': note,
                'date': date,
                'date_update': date_update,
                'type': type,
                'user_account': user_account
            })

        total_sum = 0
        total_sum_final = 0
        for task in todos:
            if task['status'] == 'to be done':
                total_sum += task['price']
            elif task['status'] == 'завършен':
                total_sum_final += task['price']


        food = 0
        for task in todos:
            if task['type'] == 'food':
                food += task['price']

        household = 0
        for task in todos:
            if task['type'] == 'home':
                household += task['price']

        fun = 0
        for task in todos:
            if task['type'] == 'entertainment':
                fun += task['price']

        taxes = 0
        for task in todos:
            if task['type'] == 'bills':
                taxes += task['price']

        transport = 0
        for task in todos:
            if task['type'] == 'transport':
                transport += task['price']

        mortgage = 0
        for task in todos:
            if task['type'] == 'mortgage':
                mortgage += task['price']

        todos_sorted = sorted(todos, key=lambda x: x['date_update'], reverse=True)  # Sort by date
        current_user = request.authorization.username
        return render_template('shoping_tasks.html',
                               total_sum_html=total_sum,
                               total_sum_final_html=total_sum_final,
                               food_html=food,
                               household_html=household,
                               fun_html=fun,
                               taxes_html=taxes,
                               transport_html=transport,
                               mortgage_html=mortgage,
                               todos=todos_sorted,
                               current_user=current_user)


@app.route('/add_shoping_tasks', methods=['POST'])
def add_shoping_tasks():
    goods = request.form['goods']
    price = request.form['price']
    status = 'to be done'
    note = request.form['note']
    date = current_datetime.now()
    date_update = current_datetime.now()
    type = request.form['type']
    current_user = request.authorization.username  # Get the logged-in user(name)
    with engine.connect() as conn:
        conn.execute(
            insert(Shopping),[
                {"goods": goods,
                 "price": price,
                 "status": status,
                 "note": note,
                 "date": date,
                 "date_update": date_update,
                 "type": type,
                 "user_account": current_user
                }
            ]
        )
        conn.commit()
    return redirect('/shoping_tasks.html')


@app.route('/complete_shoping_task', methods=['POST'])
def complete_shoping_task():
    task_id = request.form['task_id']
    with engine.connect() as conn:
        conn.execute(
            update(Shopping)
            .where(Shopping.id == task_id)
            .values(status = 'завършен', date_update = current_datetime.now())
        )
        conn.commit()
    return redirect('/shoping_tasks.html')


@app.route('/return_to_list_shop', methods=['POST'])
def return_to_list_shop():
    task_id = request.form['task_id']
    with engine.connect() as conn:
        conn.execute(
            update(Shopping)
            .where(Shopping.id == task_id)
            .values(status = 'to be done', date_update = current_datetime.now())
        )
        conn.commit()
    return redirect('/shoping_tasks.html')


@app.route('/delete_shoping_task', methods=['POST'])
def delete_shoping_task():
    task_id = request.form['task_id']
    with engine.connect() as conn:
        conn.execute(
            delete(Shopping)
            .where(Shopping.id == task_id)
        )
        conn.commit()

    return redirect('/shoping_tasks.html')


@app.route('/edit_shoping_tasks/<int:task_id>', methods=['GET', 'POST'])
@requires_auth
def edit_shoping_tasks(task_id):
    with Session(engine) as session:
        task = session.execute(select(Shopping.id,
                                      Shopping.goods,
                                      Shopping.price,
                                      Shopping.status,
                                      Shopping.note,
                                      Shopping.date,
                                      Shopping.date_update,
                                      Shopping.type,
                                      Shopping.user_account
                                      ).where(Shopping.id == task_id)).fetchone()


        if task:
            task = {'id': task.id, 'goods': task.goods, 'price': task.price, 'status': task.status, 'note': task.note,
                    'date': task.date, 'date_update': task.date_update, 'type': task.type,
                    'user_account': task.user_account}

            current_user = request.authorization.username
            return render_template('edit_shoping_tasks.html', task=task, current_user=current_user)
        else:
            # Handle case when task is not found
            return "Task not found"


@app.route('/edit_shoping_tasks_button', methods=['POST'])
@requires_auth
def add_shoping_tasks_button():
    id = request.form['id']
    task = request.form['goods']
    price = request.form['price']
    note = request.form['note']
    type = request.form['type']
    user = request.form['user']

    with engine.connect() as conn:
        conn.execute(
            update(Shopping)
            .where(Shopping.id == id)
            .values(goods = task, price = price, note = note, type = type, user_account = user)
        )
        conn.commit()
    return redirect('/shoping_tasks.html')


@app.route('/users_tasks.html')
@requires_auth
def users():
    current_user = request.authorization.username  # Get the logged-in user(name)
    return render_template('users_tasks.html', current_user=current_user)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
