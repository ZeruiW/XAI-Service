import os
import json

from flask import Flask
import xai_backend_central_dev.flask_manager as fm


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    fm.load_env(app)

    from . import model
    app.register_blueprint(model.ebp)

    return app
