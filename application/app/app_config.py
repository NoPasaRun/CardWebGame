import os
from flask import Flask, request


SECRET_KEY = os.urandom(32)


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config["CSRF_PROTECT"] = False
    app.jinja_env.filters['zip'] = zip
    return app


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
