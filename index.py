from flask import request, render_template
from authentication import requires_auth


def configure_index_route(app):
    @app.route('/')
    @requires_auth
    def index():
        current_user = request.authorization.username
        return render_template("index.html", current_user=current_user)
