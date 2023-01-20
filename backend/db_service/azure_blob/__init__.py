import os
import json
from flask import Flask
import xai_backend_central_dev.flask_manager as fm


def create_app(mode='dev'):
    fm.load_env(mode)
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    fm.set_app(app)

    from . import azure_blob
    app.register_blueprint(azure_blob.bp)

    return app
