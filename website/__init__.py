from flask import Flask

from .events import socketio
from .routes import main

def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config["SECRET_KEY"] = "secret"

    # for html blueprints (rendering)
    app.register_blueprint(main)

    socketio.init_app(app)
    return app

