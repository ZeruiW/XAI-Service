import os

from flask import Flask
import xai_backend_central_dev.flask_manager as fm


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    fm.load_env(app)

    from . import xai_cam
    app.register_blueprint(xai_cam.ebp)

    return app
