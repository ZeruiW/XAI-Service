import os
import pathlib

cnxpool = None


def init_db():
    global cnxpool
    cnx = cnxpool.get_connection()
    with open(os.path.join(pathlib.Path(__file__).parent.resolve(), "config", "db_init.sql"), 'r') as f:
        cursor = cnx.cursor()
        for result in cursor.execute(f.read(), multi=True):
            pass
            # if result.with_rows:
            #     print("Rows produced by statement '{}':".format(result.statement))
            #     print(result.fetchall())
            # else:
            #     print("Number of rows affected by statement '{}': {}".format(
            #         result.statement, result.rowcount))
        cnx.commit()
        cursor.close()


def set_pool(p):
    global cnxpool
    cnxpool = p


def trans(func, *func_parameter):
    global cnxpool
    cnx = cnxpool.get_connection()
    rs = func(cnx, *func_parameter)
    cnx.close()

    return rs
