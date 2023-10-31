from flask import Flask
from authentication import configure_logout
from index import configure_index_route
from todo import configure_todo_route
from shopping import configure_shoping_route
from vacations import configure_vacations_route
from users import configure_users_route

app = Flask(__name__)

configure_logout(app)
configure_index_route(app)
configure_todo_route(app)
configure_shoping_route(app)
configure_vacations_route(app)
configure_users_route(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
