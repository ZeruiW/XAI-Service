import os

from flask import Flask
import xai_backend_central_dev.flask_manager as fm

fm.create_tmp_dir(__file__)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    fm.load_env(app)

    from . import xai_eval
    app.register_blueprint(xai_eval.bp)
    # app.register_blueprint(tb_explanation.bp)

    return app
