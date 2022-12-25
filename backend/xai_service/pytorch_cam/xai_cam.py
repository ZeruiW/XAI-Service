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

ebp = ExecutorBluePrint(
    'pt_cam', __name__, component_path=__file__, url_prefix='/xai/pt_cam')
te = ebp.get_task_executor()
te.define_task_func_map('default', task_func.cam_task)
