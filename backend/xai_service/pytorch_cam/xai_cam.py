from flask import (
    request, jsonify, send_file
)

import os
import platform
from xai_backend_central_dev.flask_manager import ExecutorBluePrint

from . import task_func

# task_executor_info = {
#     'executor_name': 'xai_service:pt_cam'
# }


print('--------')
print('Platform:')
print(platform.platform())
print('--------')

env_cam_method = os.environ.get('CAM_METHOD')
varient = '' if (env_cam_method ==
                 'grad-cam' or env_cam_method is None) else env_cam_method

# TODO: CAM PATH
url_prefix = f'/xai/pt_cam{varient}'

ebp = ExecutorBluePrint(
    'pt_cam', __name__, component_path=__file__, url_prefix=url_prefix)
te = ebp.get_task_executor()
te.define_task_func_map('default', task_func.cam_task)

te.set_clean_task_function(task_func.cf)
