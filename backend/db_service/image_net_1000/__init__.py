import os
import mysql.connector
from flask import Flask
import xai_backend_central_dev.flask_manager as fm


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    fm.load_env(app)

    # set global db pool
    from . import db_helper
    cnxpool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=int(os.getenv('MYSQL_POOL_SIZE') or 20),
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DB')
    )
    db_helper.set_pool(cnxpool)
    db_helper.init_db()

    from . import tb_image_net_1000
    app.register_blueprint(tb_image_net_1000.bp)

    return app
