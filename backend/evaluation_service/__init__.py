import os

from flask import Flask
import xai_backend_central_dev.flask_manager as fm


def create_app(mode='dev'):
    fm.load_env(mode)

    from . import xai_eval
    context_path = os.environ['CONTEXT_PATH']
    static_url_path = context_path + '/static'

    app = Flask(__name__, instance_relative_config=True,
                static_url_path=static_url_path)
    fm.set_app(app)

    app.register_blueprint(xai_eval.ebp)
    # app.register_blueprint(tb_explanation.bp)

    return app
