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


ebp = ExecutorBluePrint(
    'pt_cam', __name__, component_path=__file__, url_prefix='/xai/pt_cam')
te = ebp.get_task_executor()

print('--------')
print('Platform:')
print(platform.platform())
print('--------')


@ebp.route('/', methods=['POST', 'GET'])
def cam_func():
    if request.method == 'GET':
        task_ticket = request.args['task_ticket']
        file_name = os.path.join(ebp.tmp_path, f'{task_ticket}.zip')
        if os.path.exists(file_name):
            # np.load in tmp folder
            # cam_array_file = os.path.join(basedir, 'tmp\' + task_name + '.zip')
            # cam_array = np.load(cam_array_file)
            # for i in range(len(cam_array)):
            return send_file(file_name, as_attachment=True)
        else:
            # TODO: should follow the restful specification
            return "no such task"

    if request.method == "POST":
        form_data = request.form
        # task_info = f"{str(time.time()).split('.')[1]}#{form_data['model_name'].lower()}#{form_data['method_name'].lower()}#{form_data['data_set_name'].lower()}#{form_data['data_set_group_name'].lower()}"
        task_info = dict(
            task_desc="generate cam explanation",
            model_name=form_data['model_name'].lower(),
            method_name=form_data['method_name'].lower(),
            data_set_name=form_data['data_set_name'].lower(),
            data_set_group_name=form_data['data_set_group_name'].lower(),
        )
        task_ticket = te.request_ticket_and_start_task(
            task_info, task_func.cam_task, form_data)
        if task_ticket == None:
            return "Can not request a task ticket"
        else:
            return jsonify({
                'task_ticket': task_ticket
            })
