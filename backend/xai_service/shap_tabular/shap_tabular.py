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
    'shap_tabular', __name__, component_path=__file__, url_prefix='/xai/shap_tabular')


te = ebp.get_task_executor()
te.define_task_func_map('default', task_func.shap_task)

te.set_clean_task_function(task_func.cf)

# @ebp.route('/', methods=['GET', 'POST'])
# def pred():
#     if request.method == 'POST':
#         index = request.form.get('index')
#         index = int(index)
#         task_ticket = request.form.get('task_ticket')
#         model_url = request.form.get('model_service_url')
#         # rs = {}
#         # for i in range(len(file_name)):
#         #     rs[file_name[i]] = [round(d, 6) for d in prediction[i]]
#         #rs = task_func.shap_task('task_ticket', 'http://127.0.0.1:5008/xgb', index)
#         rs = task_func.shap_task(task_ticket, model_url, index)
#         return str(rs)

#     elif request.method == 'GET':
#         return 'get'
