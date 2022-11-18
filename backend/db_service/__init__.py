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

    from . import tb_image_net_1000, tb_arxiv_cs, tb_explanation
    app.register_blueprint(tb_image_net_1000.bp)
    app.register_blueprint(tb_arxiv_cs.bp)
    app.register_blueprint(tb_explanation.bp)

    return app
