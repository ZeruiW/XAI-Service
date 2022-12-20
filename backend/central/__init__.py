import os
from flask import Flask
import xai_backend_central_dev.flask_manager as fm


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    fm.load_env(app)

    from . import central
    app.register_blueprint(central.bp)
    app.register_blueprint(central.tp.pipeline.ebp)
    # app.register_blueprint(tb_arxiv_cs.bp)
    # app.register_blueprint(tb_explanation.bp)

    return app
