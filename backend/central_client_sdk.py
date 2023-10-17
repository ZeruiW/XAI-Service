import requests
import json
import time
import yaml
from tqdm import tqdm

# Load the configuration
with open('sdk_config.yaml', 'r') as file:
    config = yaml.safe_load(file)

class TaskPublisherClient:
    def __init__(self, base_url):
        self.base_url = base_url

    #-------------publisher functions----------------
    # Activte Publisher Function
    def activate_publisher(self, publisher_endpoint_url):
        url = f"{self.base_url}/task_publisher/publisher"
        data = {'publisher_endpoint_url': publisher_endpoint_url}
        response = requests.post(url, data=data)
        return response.json()
    
    #Get List of Registered Executors Function
    def get_registered_executors(self):
        url = f"{self.base_url}/task_publisher/executor"
        response = requests.get(url)
        return response.json()

    #Register/Update/Delete Executors Function
    def register_executor_endpoint(self, act, executor_endpoint_url, executor_type, executor_info):
        url = f"{self.base_url}/task_publisher/executor"
        data = {
            'act': act,
            'executor_endpoint_url': executor_endpoint_url,
            'executor_type': executor_type,
            'executor_info': json.dumps(executor_info)
        }
        response = requests.post(url, data=data)
        return response.json()
    
    #------------ Tasksheet Functions----------------
    # Create Task Sheet Function
    def create_task_sheet(self, payload):
        url = f"{self.base_url}/task_publisher/task_sheet"
        data = {'act': 'create'}
        data.update(payload)
        response = requests.post(url, data=data)
        return response.json()

    #Run Task from Task Sheet Function
    def run_task_sheet(self, task_sheet_id):
        url = f"{self.base_url}/task_publisher/task_sheet"
        data = {
            'act': 'run',
            'task_sheet_id': task_sheet_id
        }
        response = requests.post(url, data=data)
        return response.json()

    #Delete Task sheet Function
    def delete_task_sheet(self, task_sheet_id):
        url = f"{self.base_url}/task_publisher/task_sheet"
        data = {
            'act': 'delete',
            'task_sheet_id': task_sheet_id
        }
        response = requests.post(url, data=data)
        return response.text
    
    #GET Task Sheet Function
    def get_task_sheet(self):
        url = f"{self.base_url}/task_publisher/task_sheet"
        response = requests.get(url)
        return response.json()
    
    #GET Task Sheet Function by task_sheet_id
    def get_task_sheet_by_task_sheet_id(self, task_sheet_ids=None):
        url = f"{self.base_url}/task_publisher/task_sheet"
        params = {}
        if task_sheet_ids:
            params['task_sheet_ids'] = json.dumps(task_sheet_ids)
        response = requests.get(url, params=params)
        return response.json()
    
    #---------------Task Functions--------------------
    #Get Task info from task_ticket_id or task_sheet_id
    def get_task(self, task_ticket=None, task_sheet_id=None):
        url = f"{self.base_url}/task_publisher/task"
        params = {}
        if task_ticket:
            params['task_ticket'] = task_ticket
        if task_sheet_id:
            params['task_sheet_id'] = task_sheet_id
        response = requests.get(url, params=params)
        return response.json()

    #Get Task Result
    def task_result(self, task_ticket):
        url = f"{self.base_url}/task_publisher/task_result"
        params = {'task_ticket': task_ticket}
        response = requests.get(url, params=params)
        return response.json()
    
    #Update Task status
    def update_task_status(self, task_ticket, task_status, running_info):
        url = f"{self.base_url}/task_publisher/task"
        data = {
            'act': 'update_task_status',
            'task_ticket': task_ticket,
            'task_status': task_status,
            'running_info': json.dumps(running_info)
        }
        response = requests.post(url, data=data)
        return response.json()

    #stop task
    def stop_task(self, task_ticket):
        url = f"{self.base_url}/task_publisher/task"
        data = {
            'act': 'stop',
            'task_ticket': task_ticket
        }
        response = requests.post(url, data=data)
        return response.text

    #delete task
    def delete_task(self, task_ticket):
        url = f"{self.base_url}/task_publisher/task"
        data = {
            'act': 'delete',
            'task_ticket': task_ticket
        }
        response = requests.post(url, data=data)
        return response.text

    #-----------Pipeline Functions-----------------
    #create pipeline
    def create_pipeline(self, pipeline_name, xai_task_sheet_id, evaluation_task_sheet_id):
        url = f"{self.base_url}/task_publisher/pipeline"
        data = {
            'act': 'create',
            'pipeline_name': pipeline_name,
            'xai_task_sheet_id': xai_task_sheet_id,
            'evaluation_task_sheet_id': evaluation_task_sheet_id
        }
        response = requests.post(url, data=data)
        return response.json()

    #run pipeline
    def run_pipeline(self, pipeline_id):
        url = f"{self.base_url}/task_publisher/pipeline"
        data = {
            'act': 'run',
            'pipeline_id': pipeline_id
        }
        response = requests.post(url, data=data)
        return response.json()

    #delete pipeline
    def delete_pipeline(self, pipeline_id):
        url = f"{self.base_url}/task_publisher/pipeline"
        data = {
            'act': 'delete',
            'pipeline_id': pipeline_id
        }
        response = requests.post(url, data=data)
        return response.text



client = TaskPublisherClient(base_url=config['base_url'])


# Function to check if a service is already registered
def is_service_registered(service_type):
    registered_executors = client.get_registered_executors()
    for executor in registered_executors:
        if executor.get("executor_type") == service_type:
            return True
    return False

# Function to get the latest task sheet name index
def get_latest_task_sheet_index(task_type):
    task_sheets = client.get_task_sheet()
    indices = [0]
    for sheet in task_sheets:
        if task_type in sheet.get('task_sheet_name'):
            index = int(sheet.get('task_sheet_name').split(task_type)[1])
            indices.append(index)
    return max(indices)


print("\n\nActivating the Publisher.....\nResponse:\n")
#Activate Publisher
response = client.activate_publisher(publisher_endpoint_url=config['base_url'])
print(response)
print("\nPublisher activated successfully !")

# Register services only if they are not already registered
services = ['db', 'model', 'xai', 'evaluation']
for service in services:
    if not is_service_registered(service):
        service_config = config['services'][f'{service}_service']
        print(f"\n\nRegistering the {service.upper()} service.....\nResponse:\n")
        executor_response = client.register_executor_endpoint(
            act='reg',
            executor_endpoint_url=service_config['url'],
            executor_type=service_config['type'],
            executor_info=service_config['info']
        )
        print(executor_response)
        print(f"\n{service.upper()} service registered successfully !")
    else:
        print(f"\n{service.upper()} service is already registered, skipping registration.")

# print("\n\nRegistering the Database service.....\nResponse:\n")
# #Register DB Executor Endpoint
# db_service = config['services']['db_service']
# executor_response = client.register_executor_endpoint(
#     act='reg',
#     executor_endpoint_url=db_service['url'],
#     executor_type=db_service['type'],                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
#     executor_info=db_service['info']
# )
# print(executor_response)
# print("\nDB service registered successfully !")

# print("\n\nRegistering the AI_Model Service...\nResponse:\n")
# #Register AI Model Executor Endpoint
# model_service = config['services']['ai_model_service']
# executor_response = client.register_executor_endpoint(
#     act='reg',
#     executor_endpoint_url=model_service['url'],
#     executor_type=model_service['type'],
#     executor_info=model_service['info']
# )
# print(executor_response)
# print("\nAI_Model service registered successfully !")


# print("\n\nRegistering the XAI Service.....\n Response:\n")
# #Register XAI Executor Endpoint
# xai_service = config['services']['xai_service']
# executor_response = client.register_executor_endpoint(  
#     act='reg',
#     executor_endpoint_url=xai_service['url'],
#     executor_type=xai_service['type'],
#     executor_info=xai_service['info']
# )
# print(executor_response)
# print("\nXAI service registered successfully !")

# print("\n\n Registering the Evaluation Service.....\nResponse:\n")
# #Register evaluation Executor Endpoint
# eval_service = config['services']['evaluation_service']
# executor_response = client.register_executor_endpoint(
#     act='reg',
#     executor_endpoint_url=eval_service['url'],
#     executor_type=eval_service['type'],
#     executor_info=eval_service['info']
# )
# print(executor_response)
# print("\nEvaluation service registered successfully !")

print("\n\nAll services registered successfully")

# Get the list of registered executors
executors_response = client.get_registered_executors()
#print(json.dumps(executors_response, indent=4))  # Pretty print the response

# Extract executor IDs based on their types
executor_ids = {
    "db": None,
    "model": None,
    "xai": None,
    "evaluation": None
}

for executor in executors_response:
    executor_type = executor.get("executor_type")
    if executor_type in executor_ids:
        executor_ids[executor_type] = executor.get("executor_id")

# Increment the task sheet names
xai_index = get_latest_task_sheet_index('xai') + 1
eval_index = get_latest_task_sheet_index('eval_xai') + 1

# Modify the XAI and Evaluation task sheet names in the config
config['xai_task_sheet']['task_sheet_name'] = f"xai{xai_index}"
config['evaluation_task_sheet']['task_sheet_name'] = f"eval_xai{eval_index}"

# Check if all required executor IDs are available
if all(id is not None for key, id in executor_ids.items() if key != "evaluation"):
    # Create XAI Task Sheet with Specific Parameters and extracted executor IDs
    xai_config = config['xai_task_sheet']
    payload = {
        "act": "create",
        "task_type": "xai",
        "model_service_executor_id": executor_ids["model"],
        "db_service_executor_id": executor_ids["db"],
        "xai_service_executor_id": executor_ids["xai"],
        "task_parameters":json.dumps(xai_config['task_parameters']),
        "task_sheet_name": xai_config['task_sheet_name']
    }

    # Create XAI Task Sheet
    create_task_sheet_response = client.create_task_sheet(payload=payload)

    # Print the Response
    print("\n\nNow, Creating XAI Task Sheet...\nResponse:")
    print(json.dumps(create_task_sheet_response, indent=4))  # Pretty print the response
    print("\nXAI Task_sheet created successfully !")
    # Extract task_sheet_id from the response and run the XAI task sheet
    xai_task_sheet_id = create_task_sheet_response.get('task_sheet_id')
    if xai_task_sheet_id:
        #print(f"\n\n Extracted Task Sheet ID: {xai_task_sheet_id}")

        # Run XAI Task Sheet with the extracted task_sheet_id
        run_xai_task_sheet_response = client.run_task_sheet(task_sheet_id=xai_task_sheet_id)
        print("\n\nRunning XAI Task Sheet....\nResponse:")
        print(json.dumps(run_xai_task_sheet_response, indent=4))  # Pretty print the response
        print("XAI Task sheet running successfully...!")
        
     # Extract task_ticket from the response of running the XAI task sheet
        xai_task_ticket = run_xai_task_sheet_response.get('task_ticket')
        if xai_task_ticket:
            #print(f"\n\n Extracted XAI Task Ticket: {xai_task_ticket}")

            # Poll the status of the XAI task until it is finished
            while True:
                task_info = client.get_task(task_ticket=xai_task_ticket)
                task_status = task_info.get('task_status')

                if task_status == 'finished':
                    print("\n\nXAI Task finished.")
                    break
                elif task_status in ['failed', 'error']:  # Add any other terminal statuses here
                    print(f"\n\nXAI Task failed with status: {task_status}.")
                    exit()  # or handle the error appropriately
                else:
                    print(f"\n\nXAI Task is still running with status: {task_status}. Waiting...")

                    # Display a progress bar instead of sleeping for a fixed amount of time
                    for _ in tqdm(range(30), desc="Processing", ncols=100):
                        time.sleep(1)  # sleep for a total of 30 seconds, updating the progress bar every second

            # Create Evaluation Task Sheet with the extracted task_ticket and executor IDs
            eval_config = config['evaluation_task_sheet']
            eval_payload = {
                "act": "create",
                "task_type": "evaluation",
                "model_service_executor_id": executor_ids["model"],
                "db_service_executor_id": executor_ids["db"],
                "xai_service_executor_id": executor_ids["xai"],
                "evaluation_service_executor_id": executor_ids["evaluation"],
                "task_parameters": json.dumps({
                    "explanation_task_ticket": xai_task_ticket
                }),
                "task_sheet_name":eval_config['task_sheet_name']
            }
            
            # Create Evaluation Task Sheet
            create_eval_task_sheet_response = client.create_task_sheet(payload=eval_payload)
            print("\n\nNow, creating Evaluation Task Sheet...\nResponse:")
            print(json.dumps(create_eval_task_sheet_response, indent=4))  # Pretty print the response

            # Extract eval_task_sheet_id from the response and run the evaluation task sheet
            eval_task_sheet_id = create_eval_task_sheet_response.get('task_sheet_id')
            if eval_task_sheet_id:
                #print(f"\n\n Extracted Evaluation Task Sheet ID: {eval_task_sheet_id}")

                # Run Evaluation Task Sheet with the extracted task_sheet_id
                run_eval_task_sheet_response = client.run_task_sheet(task_sheet_id=eval_task_sheet_id)
                print("\n\nRunning Evaluation Task Sheet.....\nResponse:")
                print(json.dumps(run_eval_task_sheet_response, indent=4))  # Pretty print the response
                print("\nEvaluation Task sheet is running Successfully !")
            else:
                print("Evaluation Task Sheet ID not found in the response.")
        else:
            print("XAI Task Ticket not found in the response.")
    else:
        print("XAI Task Sheet ID not found in the response.")
else:
    print("Required executor IDs are not available.")

# Increment the pipeline name
pipeline_index = get_latest_task_sheet_index('pipeline') + 1
config['pipeline']['name'] = f"pipeline{pipeline_index}"

# GET Task Sheets
task_sheet_response = client.get_task_sheet()

#Extracting xai and Evaluation task_sheet_ids
xai_task_sheet_id = None
evaluation_task_sheet_id = None

for sheet in task_sheet_response:
    task_type = sheet.get('task_type')
    task_sheet_id = sheet.get('task_sheet_id')
    
    if task_type == 'xai' and task_sheet_id:
        xai_task_sheet_id = task_sheet_id
    elif task_type == 'evaluation' and task_sheet_id:
        evaluation_task_sheet_id = task_sheet_id

# Check if both xai and evaluation task_sheet_ids are extracted
if xai_task_sheet_id and evaluation_task_sheet_id:
    # Create Pipeline
    pipeline_config = config['pipeline']
    create_pipeline_response = client.create_pipeline(
        pipeline_name=pipeline_config['name'],
        xai_task_sheet_id=xai_task_sheet_id,
        evaluation_task_sheet_id=evaluation_task_sheet_id
    )
    #print(create_pipeline_response)

    # Extract pipeline_id from the response
    pipeline_id = create_pipeline_response.get('pipeline_id')
    if pipeline_id:
        #print(f"Extracted Pipeline ID: {pipeline_id}")

        # Run Pipeline with the extracted pipeline_id
        print("\n\nRunning Pipeline.....\n")
        run_pipeline_response = client.run_pipeline(pipeline_id=pipeline_id)
        print(f"Pipeline with the pipeline Id:{pipeline_id}. Created Successfully !!!")
    else:
        print("Pipeline ID not found in the response.")
else:
    print("Either XAI or Evaluation Task Sheet ID not found.")

















# # Delete Task Sheet
# delete_task_sheet_response = client.delete_task_sheet(task_sheet_id="sheet1")
# print(delete_task_sheet_response)



# # Get Task
# task_response = client.get_task(task_ticket="ticket1")
# print(task_response)

# # Get Task Result
# task_result_response = client.task_result(task_ticket="ticket1")
# print(task_result_response)

# # Update Task Status
# update_task_status_response = client.update_task_status(
#     task_ticket="ticket1",
#     task_status="completed",
#     running_info={"progress": "100%"}
# )
# print(update_task_status_response)

# # Stop Task
# stop_task_response = client.stop_task(task_ticket="ticket1")
# print(stop_task_response)

# # Delete Task
# delete_task_response = client.delete_task(task_ticket="ticket1")
# print(delete_task_response)





# # Delete Pipeline
# delete_pipeline_response = client.delete_pipeline(pipeline_id="pipeline1")
# print(delete_pipeline_response)


# # Update Executor Endpoint
# executor_response = client.register_executor_endpoint(
#     act='update',
#     executor_endpoint_url="http://127.0.0.1:5001/resnet50",
#     executor_id="D2QPM5471J",
#     executor_info={"exe_name": "newresnet50"}
# )
# print(executor_response)

# # delete Executor Endpoint
# executor_response = client.register_executor_endpoint(
#     act='delete',
#     executor_id="D2QPM5471J",
# )
# print(executor_response)
