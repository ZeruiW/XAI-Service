import os
from flask import Flask
from dotenv import load_dotenv, dotenv_values

basedir = os.path.abspath(os.path.dirname(__file__))
tmpdir = os.path.join(basedir, 'tmp')
if not os.path.isdir(tmpdir):
    os.mkdir(tmpdir)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    print('App Mode: ' + 'DEV' if app.debug else 'PROD')

    if app.debug:
        config = dotenv_values(os.path.join(basedir, ".env.dev"))
        for k in config.keys():
            if os.getenv(k) == None:
                os.environ[k] = config[k]
    else:
        load_dotenv(os.path.join(basedir, ".env.prod"))

    # from . import tb_arxiv_cs, tb_image_net_1000, tb_explanation
    # app.register_blueprint(tb_image_net_1000.bp)
    # app.register_blueprint(tb_arxiv_cs.bp)
    # app.register_blueprint(tb_explanation.bp)

    return app
