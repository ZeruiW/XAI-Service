import requests
import json
import time
import yaml
import re
import pkg_resources
from tqdm import tqdm
from collections import defaultdict

try:
    # Load the configuration file from the package
    config_file = pkg_resources.resource_filename('sdk', 'sdk_config.yaml')

    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

except FileNotFoundError:
    print("Error: Configuration file not found.")
except yaml.YAMLError as exc:
    print(f"Error: Failed to parse the configuration file - {exc}")
    

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
    def register(self, act, executor_endpoint_url, executor_type, executor_info):
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
    
    #get all pipelines
    def get_all_pipelines(self):
        url = f"{self.base_url}/task_publisher/pipeline"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()  
        else:
            print(f"Failed to fetch pipelines: {response.status_code}")
            return []
        





        
if __name__ == "__main__":
    
    client = TaskPublisherClient(base_url=config['base_url'])

    # Function to check if a service is already registered
    def get_registered_service_urls(service_type):
        registered_executors = client.get_registered_executors()
        urls = [
            executor.get("executor_endpoint_url")
            for executor in registered_executors
            if executor.get("executor_type") == service_type
        ]
        return urls


    # Function to get the latest task sheet name index
    def get_latest_task_sheet_index(task_type):
        task_sheets = client.get_task_sheet()
        indices = [0]
        for sheet in task_sheets:
            if task_type in sheet.get('task_sheet_name'):
                index = int(sheet.get('task_sheet_name').split(task_type)[1])
                indices.append(index)
        return max(indices)

    #function to get the latest pipeline index
    def get_latest_pipeline_index(pipelines):
        indices = []
        for pipeline in pipelines:
            name = pipeline.get('pipeline_name', '')
            match = re.search(r'pipeline(\d+)', name)  # Use regex to extract the index
            if match:
                try:
                    index = int(match.group(1))  # Extract the index from the regex match
                    indices.append(index)
                except ValueError:
                    pass
        return max(indices, default=0)



    print("\n\nActivating the Publisher.....\nResponse:\n")
    #Activate Publisher
    response = client.activate_publisher(publisher_endpoint_url=config['base_url'])
    print(response)
    print("\nPublisher activated successfully !")

    # Register services if they are not already registered or if their URL has changed
    services = ['db', 'model', 'xai', 'evaluation']
    for service in services:
        service_config = config['services'][f'{service}_service']
        registered_urls = get_registered_service_urls(service)
        
        print(f"Registered URLs for {service.upper()}: {registered_urls}")
        print(f"URL in sdk_config.yaml for {service.upper()}: {service_config['url']}")
        
        if not registered_urls or service_config['url'] not in registered_urls:
            print(f"\n\nRegistering the {service.upper()} service.....\nResponse:\n")
            executor_response = client.register(
                act='reg',
                executor_endpoint_url=service_config['url'],
                executor_type=service_config['type'],
                executor_info=service_config['info']
            )
            print(executor_response)
            print(f"\n{service.upper()} service registered successfully !")
        else:
            print(f"\n{service.upper()} service is already registered with the same URL, skipping registration.")


    print("\n\nAll services registered successfully")

    # Get the list of registered executors
    executors_response = client.get_registered_executors()
    #print(json.dumps(executors_response, indent=4))  # Pretty print the response

    # Extract executor IDs and service names based on their types
    executor_info = defaultdict(list)

    for executor in executors_response:
        executor_type = executor.get("executor_type")
        executor_id = executor.get("executor_id")
        service_name = executor.get("executor_info").get("exp_name")  # Adjust the key as per your actual data structure
        executor_info[executor_type].append((executor_id, service_name))

    # Print available executor IDs and service names for each type
    for executor_type, info in executor_info.items():
        print(f"Available services for {executor_type.upper()}:")
        for id, name in info:
            print(f"ID: {id}, Service Name: {name}")

    #Selecting executor Ids by the user
    selected_executor_ids = {
        "db": None,
        "model": None,
        "xai": None,
        "evaluation": None
    }

    for service_type in selected_executor_ids.keys():
        if executor_info[service_type]:
            print(f"\nPlease select a service for {service_type.upper()}:")
            for i, (executor_id, service_name) in enumerate(executor_info[service_type], start=1):
                print(f"{i}. {service_name} (ID: {executor_id})")
            
            selected_index = int(input("Enter the number of your choice: ")) - 1
            selected_executor_ids[service_type] = executor_info[service_type][selected_index][0]  # Select the ID part from the tuple


    # Increment the task sheet names
    xai_index = get_latest_task_sheet_index('xai') + 1
    eval_index = get_latest_task_sheet_index('eval_xai') + 1

    # Modify the XAI and Evaluation task sheet names in the config
    config['xai_task_sheet']['task_sheet_name'] = f"xai{xai_index}"
    config['evaluation_task_sheet']['task_sheet_name'] = f"eval_xai{eval_index}"

    # Check if all required executor IDs are available
    if all(id is not None for key, id in selected_executor_ids.items() if key != "evaluation"):
        # Create XAI Task Sheet with Specific Parameters and selected executor IDs
        xai_config = config['xai_task_sheet']
        payload = {
            "act": "create",
            "task_type": "xai",
            "model_service_executor_id": selected_executor_ids["model"],
            "db_service_executor_id": selected_executor_ids["db"],
            "xai_service_executor_id": selected_executor_ids["xai"],
            "task_parameters": json.dumps(xai_config['task_parameters']),
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
                    "model_service_executor_id": selected_executor_ids["model"],
                    "db_service_executor_id": selected_executor_ids["db"],
                    "xai_service_executor_id": selected_executor_ids["xai"],
                    "evaluation_service_executor_id": selected_executor_ids["evaluation"],
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

    # Fetch all existing pipelines
    pipelines = client.get_all_pipelines()
    # print(pipelines)  # Print the fetched pipelines

    # Get the latest pipeline index
    latest_index = get_latest_pipeline_index(pipelines)
    # print(latest_index)  # Print the latest index

    # Increment the index
    new_index = latest_index + 1

    # Update the pipeline name in the configuration
    config['pipeline']['name'] = f"pipeline{new_index}"
    # print(config['pipeline']['name'])  # Print the updated pipeline name


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
