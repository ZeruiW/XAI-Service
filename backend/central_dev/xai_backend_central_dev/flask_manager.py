from dotenv import load_dotenv, dotenv_values
import glob
import os


def create_tmp_dir(service_init_path):
    basedir = os.path.abspath(os.path.dirname(service_init_path))
    tmpdir = os.path.join(basedir, 'tmp')
    if not os.path.isdir(tmpdir):
        os.mkdir(tmpdir)


def load_env(app):
    print('App Mode: ' + 'dev' if app.debug else 'prod')

    env_file = f".env.{'dev' if app.debug else 'prod'}"
    for f in glob.glob(os.path.join(os.getcwd(), '**', env_file), recursive=True):
        env_file = f

    if app.debug:
        config = dotenv_values(env_file)
        for k in config.keys():
            if os.getenv(k) == None:
                os.environ[k] = config[k]
    else:
        load_dotenv(env_file)
