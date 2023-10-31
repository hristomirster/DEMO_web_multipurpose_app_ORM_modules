import datetime
from db_connection import engine
from sqlalchemy.orm import Session, Mapped, mapped_column, DeclarativeBase
from sqlalchemy import select, String, insert, update, delete
from flask import request, render_template, redirect
from authentication import requires_auth, Users


class Base(DeclarativeBase):
    pass

def configure_shoping_route(app):
    class Shopping(Base):
        __tablename__ = "table_shoping"
        id: Mapped[int] = mapped_column(primary_key=True)
        goods: Mapped[str]
        price: Mapped[int]
        status: Mapped[str]
        note: Mapped[str]
        date: Mapped[str]
        date_update: Mapped[str]
        type: Mapped[str]
        user_account: Mapped[str]

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
                id, goods, price, status, note, date, date_update, type, user_account = row
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
        date = datetime.datetime.now()
        date_update = datetime.datetime.now()
        type = request.form['type']
        current_user = request.authorization.username  # Get the logged-in user(name)
        with engine.connect() as conn:
            conn.execute(
                insert(Shopping), [
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
                .values(status='завършен', date_update=datetime.datetime.now())
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
                .values(status='to be done', date_update=datetime.datetime.now())
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
                task = {'id': task.id, 'goods': task.goods, 'price': task.price, 'status': task.status,
                        'note': task.note,
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
                .values(goods=task, price=price, note=note, type=type, user_account=user)
            )
            conn.commit()
        return redirect('/shoping_tasks.html')
