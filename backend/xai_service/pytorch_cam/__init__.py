import os

from flask import Flask

basedir = os.path.abspath(os.path.dirname(__file__))
tmpdir = os.path.join(basedir, 'tmp')
if not os.path.isdir(tmpdir):
    os.mkdir(tmpdir)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    from . import xai_cam
    app.register_blueprint(xai_cam.bp)

    return app
