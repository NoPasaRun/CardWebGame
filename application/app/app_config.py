from logging.config import dictConfig
from flask import Flask, request
from application.app.app_links import *

SECRET_KEY = os.urandom(32)


def create_app():

    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "%(levelname)s IN ^^%(module)s^^ :: "
                              "<< * call %(funcName)s in line №%(lineno)d || %(message)s ||>>",
                }
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                },
                "file": {
                    "level": "WARNING",
                    "class": "logging.FileHandler",
                    "filename": os.path.join(logging_folder, "stdout.log"),
                    "formatter": "default",
                },

            },
            "root": {"level": "DEBUG", "handlers": ["console", "file"]},
        }
    )

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config["CSRF_PROTECT"] = False
    app.jinja_env.filters['zip'] = zip
    return app


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
