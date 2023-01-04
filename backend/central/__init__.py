import os
from flask import Flask
import xai_backend_central_dev.flask_manager as fm


def create_app(test_config=None):
    # create and configure the app
    from . import central

    context_path = os.environ['CONTEXT_PATH']
    static_url_path = context_path + '/static'

    app = Flask(__name__, instance_relative_config=True,
                static_url_path=static_url_path)

    fm.load_env(app)

    app.register_blueprint(central.bp)
    # app.register_blueprint(central.tp.pipeline.ebp)

    return app
