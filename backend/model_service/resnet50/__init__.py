import os
import json

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    from . import model
    app.register_blueprint(model.bp)

    return app
