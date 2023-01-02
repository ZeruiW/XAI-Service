import os
import json
from flask import (
    Blueprint, request, jsonify, send_file
)

from xai_backend_central_dev.task_publisher import TaskPublisher
from xai_backend_central_dev.constant import Pipeline
from xai_backend_central_dev.constant import TaskInfo
from xai_backend_central_dev.constant import TaskSheet
from xai_backend_central_dev.constant import ExecutorRegInfo

bp = Blueprint('central', __name__,
               url_prefix='/task_publisher')

task_publisher_name = 'central'
tp = TaskPublisher(task_publisher_name,
                   component_path=__file__, import_name=__name__)

# time related
import datetime
#timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
from bson.objectid import ObjectId
# Connect to the MongoDB instance
connection_string = os.getenv("MONGO_CONNECTION_STRING")
client = MongoClient(connection_string)

# Select the database and collection
databasestr = os.getenv("MONGO_DATABASE")
collectionstr = os.getenv("MONGO_COLLECTION")
database = client[databasestr]
collection = database[collectionstr]


#active central publisher itself
@bp.route('/publisher', methods=['GET', 'POST'])
def publisher():
    if request.method == 'GET':
        pass
        # return jsonify(tp.get_executor())
    else:
        form_data = request.form
        publisher_endpoint_url = form_data['publisher_endpoint_url']
        executor_registration_info = tp.activate_publisher(
            publisher_endpoint_url=publisher_endpoint_url)
        return jsonify(executor_registration_info)

#register executor
@bp.route('/executor', methods=['GET', 'POST'])
def executor():
    if request.method == 'GET':
        return jsonify(tp.get_executor_registration_info())
    else:
        # executor register
        form_data = request.form
        act = form_data['act']
        if act == 'reg':
            executor_endpoint_url = form_data[ExecutorRegInfo.executor_endpoint_url]
            exector_info = json.loads(form_data[ExecutorRegInfo.executor_info])
            # publisher_endpoint_url = form_data['publisher_endpoint_url']
            exector_id = tp.register_executor_endpoint(
                executor_endpoint_url, exector_info)
            instance_owner = form_data['instance_owner']

            #Instance_metadata
            instance_doc = {'Instance_metadata':
            {
                'instance_id': exector_id,
                'resgister_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'instance_owner': instance_owner,
                'service_endpoint_url': executor_endpoint_url,
                'executor_info': exector_info
            }}
            instance_json_string = json.dumps(instance_doc)
            collection.insert_one(json.loads(instance_json_string))

            return jsonify({
                    'executor_id': exector_id
                })
        if act == 'update':
            executor_id = form_data[ExecutorRegInfo.executor_id]
            executor_endpoint_url = form_data[ExecutorRegInfo.executor_endpoint_url]
            exector_info = json.loads(form_data[ExecutorRegInfo.executor_info])
            # publisher_endpoint_url = form_data['publisher_endpoint_url']
            exector_id = tp.update_executor_endpoint(
                executor_id, executor_endpoint_url, exector_info)
            return jsonify({
                'executor_id': exector_id
            })

        if act == 'delete':
            executor_id = form_data[ExecutorRegInfo.executor_id]
            tp.delete_executor_endpoint(executor_id)
            return ""

#request task info
@bp.route('/task', methods=['GET', 'POST'])
def task():
    if request.method == 'GET':
        # request a task info, need task ticket
        task_ticket = request.args.get('task_ticket')
        with_status = False if request.args.get('with_status') == None else (
            False if request.args.get('with_status') != '1' else True)
        # print(with_status)
        return jsonify(tp.get_ticket_info(task_ticket, with_status))
    else:
        return ""

#request task ticket
@bp.route('/ticket', methods=['GET', 'POST'])
def ticket():
    if request.method == 'GET':
        return ""
    else:
        # request a ticket
        form_data = request.form
        executor_id = form_data['executor_id']
        task_name = form_data['task_name']
        # task_sheet_id = form_data['task_sheet_id']
        tk = tp.gen_task_ticket(executor_id, task_name)
        return jsonify({
            'task_ticket': tk
        })

#pipeline setting
@bp.route('/pipeline', methods=['GET', 'POST'])
def pipeline():
    if request.method == 'GET':
        pipeline_id = request.args.get(Pipeline.pipeline_id)
        rs = tp.pipeline.get_pipeline(pipeline_id)
        return jsonify(rs)
    else:
        form_data = request.form
        act = form_data['act']
        if act == 'create':
            pipeline_name = form_data[Pipeline.pipeline_name]
            pipeline_info = tp.pipeline.create_pipeline(pipeline_name)

            #Pipeline_metadata
            pipeline_owner = form_data['owner']
            pipeline_doc = {'Pipeline_metadata':
                    {
                        'pipeline_name': pipeline_name,
                        'pipeline_create_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'pipeline_owner': pipeline_owner,
                        'pipeline_id': pipeline_info[Pipeline.pipeline_id]
                    }}
            pipeline_json_string = json.dumps(pipeline_doc)
            collection.insert_one(json.loads(pipeline_json_string))       
                 
            return jsonify(pipeline_info)
        if act == 'add_task':
            pipeline_id = form_data[Pipeline.pipeline_id]
            task_name = form_data[TaskInfo.task_name]
            task_sheet_id = form_data[TaskSheet.task_sheet_id]
            code = tp.pipeline.add_task_to_pipeline(
                pipeline_id, task_name, task_sheet_id)


            #Pipeline_metadata
            collection.update_one({"Pipeline_metadata.pipeline_id": pipeline_id}, {"$addToSet": {
                "Pipeline_metadata.task_sheet_id": task_sheet_id, 
                "Pipeline_metadata.task_name": task_name}})
            
            return jsonify(code)
        if act == 'run':
            pipeline_id = form_data[Pipeline.pipeline_id]
            pipeline_info = tp.pipeline.run_pipeline(pipeline_id)

            #Pipeline_metadata
            collection.update_one({"Pipeline_metadata.pipeline_id": pipeline_id}, {"$addToSet": {
                "Pipeline_metadata.pipeline_start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }})
            
            return jsonify(pipeline_info)

        if act == 'duplicate':
            pipeline_id = form_data[Pipeline.pipeline_id]
            pipeline_info = tp.pipeline.duplicate_pipeline(pipeline_id)
            return jsonify(pipeline_info)

        if act == 'stop':
            pipeline_id = form_data[Pipeline.pipeline_id]
            pipeline_info = tp.pipeline.stop_pipeline(pipeline_id)

            #Pipeline_metadata
            collection.update_one({"Pipeline_metadata.pipeline_id": pipeline_id}, {"$addToSet": {
                "Pipeline_metadata.pipeline_stop_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }})

            return jsonify(pipeline_info)

        if act == 'update_task_status':
            task_ticket = form_data[TaskInfo.task_ticket]
            task_status = form_data[TaskInfo.task_status]
            tp.pipeline.update_pipeline_task_status(task_ticket, task_status)

        return ""

#task sheet setting
@bp.route('/task_sheet', methods=['GET', 'POST'])
def task_sheet():
    if request.method == 'GET':
        task_sheet_ids = request.args.get('task_sheet_ids')
        if task_sheet_ids != None:
            task_sheet_ids = json.loads(task_sheet_ids)
        rs = tp.pipeline.get_task_sheet(task_sheet_ids)
        return jsonify(rs)
    else:
        form_data = request.form
        act = form_data['act']
        if act == 'create':
            payload = dict(form_data)
            task_sheet_id = tp.pipeline.create_task_sheet(payload)

            #Task_sheet_metadata
            task_doc = {'Task_metadata':
            {
                'task_sheet_id': task_sheet_id,
                'task_sheet_name': payload['task_sheet_name'],
                'task_type': payload['task_type'],
                'task_owner': payload['owner'],
                'task_start_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'db_instance': {'db_instance_id': payload['db_service_executor_id']
                            #'db_parameter': "data_group_label",
                            },
                'model_instance': {'model_instance_id': payload['model_service_executor_id']
                                #model_parameter: "model_parameter",
                                },
                'xai_instance': {'xai_instance_id': payload['xai_service_executor_id']
                            #xai_parameter: "xai_parameter",
                            },
                'evaluation_instance': {'evaluation_instance_id': payload['evaluation_service_executor_id']
                                    #evaluate_parameter: "evaluate_parameter",
                                    },
                'task_parameters': payload['task_parameters']
            }}  
            task_json_string = json.dumps(task_doc)
            collection.insert_one(json.loads(task_json_string))

            return jsonify({
                'task_sheet_id': task_sheet_id
            })


        if act == 'run':
            task_sheet_id = form_data[TaskSheet.task_sheet_id]
            task_name = form_data[TaskInfo.task_name]

            return jsonify({
                'task_ticket': tp.pipeline.run_task_sheet_directly(task_sheet_id, task_name)
            })

@bp.route('/provenance_data', methods=['GET', 'POST'])
def provenance_data():
    if request.method == 'GET':
        return "this function is for query provenance data, please use POST method with metadata_type, metadata_id, and owner_name"
    else:
        form_data = request.form
        metadata_type = form_data['metadata_type']
        metadata_id = form_data['metadata_id'].strip('\'')
        owner_name = form_data['owner_name'].strip('\'')
        
        if metadata_type == "'Instance_metadata'":
            data = collection.find_one({
                "Instance_metadata.instance_id": metadata_id,
                "Instance_metadata.instance_owner": owner_name
            })
            return jsonify(data['Instance_metadata'])
        elif metadata_type == "'Task_metadata'":
            data = collection.find_one({
                "Task_metadata.task_sheet_id": metadata_id,
                "Task_metadata.task_owner": owner_name
            })
            return jsonify(data['Task_metadata'])
        elif metadata_type == "'Pipeline_metadata'":
            data = collection.find_one({
                "Pipeline_metadata.pipeline_id": metadata_id,
                "Pipeline_metadata.pipeline_owner": owner_name
            })
            related_task_data = {}
            for i in range(len(data['Pipeline_metadata']['task_sheet_id'])):
                one_task_data = collection.find_one({
                    "Task_metadata.task_sheet_id": data['Pipeline_metadata']['task_sheet_id'][i]
                })
                related_task_data[f'Task{i}'] = one_task_data['Task_metadata']
            
            return jsonify(data['Pipeline_metadata'], related_task_data)

        else:
            return "metadata_type is not correct, please check again"
        
        


# client.close()