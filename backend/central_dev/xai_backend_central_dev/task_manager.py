import random
import string
import os

from xai_backend_central_dev.mongodb_helper import Mon


def __get_random_string__(length):
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def __get_random_string_no_low__(length):
    letters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))


class TaskComponent():

    def __init__(self, component_name: str, component_path: str, context_path: str, mongo=True) -> None:
        self.context_path = context_path

        self.component_name = component_name
        self.component_path = component_path
        self.component_path_parent = os.path.abspath(
            os.path.dirname(self.component_path))

        # TODO: temporary solution for retreving the task result
        self.static_path = os.path.join(
            self.component_path_parent, 'static')

        self.storage_path = os.path.join(
            self.component_path_parent, f'{self.component_name}_storage')
        self.tmp_path = os.path.join(self.storage_path, 'tmp')
        self.db_path = os.path.join(self.storage_path, 'db')

        if not os.path.exists(self.tmp_path):
            os.makedirs(self.tmp_path, exist_ok=True)

        if not os.path.exists(self.static_path):
            os.makedirs(self.static_path, exist_ok=True)

        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path, exist_ok=True)

        self.executor_db_file_path = os.path.join(
            self.db_path, f'executor_{component_name}_db.json')

        os.environ['EXECUTOR_DB_FILE_PATH'] = self.executor_db_file_path
        os.environ['COMPONENT_STORAGE_DIR'] = self.storage_path
        os.environ['COMPONENT_DB_DIR'] = self.db_path
        os.environ['COMPONENT_TMP_DIR'] = self.tmp_path
        os.environ['COMPONENT_STATIC_DIR'] = self.static_path
        os.environ['CONTEXT_PATH'] = self.context_path

        if mongo:
            self.mondb = Mon()
