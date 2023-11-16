import requests
import json
import time
import yaml
import re
import pkg_resources
from tqdm import tqdm
from collections import defaultdict
import threading
import sys
from threading import Lock

try:
    # Load the configuration file from the package
    config_file = pkg_resources.resource_filename('xai_sdk.xai_sdk', 'sdk_config.yaml')

    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

except FileNotFoundError:
    print("Error: Configuration file not found.")
except yaml.YAMLError as exc:
    print(f"Error: Failed to parse the configuration file - {exc}")

print_lock = Lock()

class TaskPublisherClient:
    def __init__(self, base_url):
        self.base_url = base_url

    #---------------------------------Publisher Functions----------------------------------
    # Activte Publisher Function
    def activate_publisher(self, publisher_endpoint_url):
        url = f"{self.base_url}/task_publisher/publisher"
        data = {'publisher_endpoint_url': publisher_endpoint_url}
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()  # Raises HTTP Error for bad HTTP response
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Error Connecting: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout Error: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Error: {req_err}")
        except ValueError as json_err:  # This is to handle invalid JSON
            print(f"JSON error: {json_err}")
    
    #Get List of Registered Executors Function
    def get_registered_executors(self):
        url = f"{self.base_url}/task_publisher/executor"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Error Connecting: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout Error: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Error: {req_err}")
        except ValueError as json_err:  # This is to handle invalid JSON
            print(f"JSON error: {json_err}")
    
    def register_executor_endpoint(self, act, executor_endpoint_url, executor_type, executor_info):
        url = f"{self.base_url}/task_publisher/executor"
        data = {
            'act': act,
            'executor_endpoint_url': executor_endpoint_url,
            'executor_type': executor_type,
            'executor_info': json.dumps(executor_info)
        }
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()

            if 'application/json' in response.headers.get('Content-Type', ''):
                try:
                    return response.json()
                except json.JSONDecodeError:
                    # Handle JSON decoding errors
                    return {
                        "status": "error",
                        "message": f"Failed to decode JSON. Response content: {response.text}"
                    }
            else:
                # If the response is not JSON, return its content as an error message
                return {
                    "status": "error",
                    "message": f"Unexpected response from server: {response.text}"
                }
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occured: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Error Connecing: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout Error Occured: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Error: {req_err}")

    def register(self, executor_endpoint_url, executor_type, executor_info):
        response = self.register_executor_endpoint('reg', executor_endpoint_url, executor_type, executor_info)
        if response.get('status') == 'error':
            print(f"Failed to register the service. Reason: {response.get('message', 'Unknown error')}")
        elif 'executor_id' in response:
            print(f"The service with executor_id: {response.get('executor_id')} is registered successfully!")
        else:
            print(f"Unexpected response received: {response}")
        return response
    
    def get_registered_services(self):
        try:
            # Get the list of registered executors
            executors_response = self.get_registered_executors()

            # Ensures the response is a list
            if not isinstance(executors_response, list):
                    print("Error: Invalid response format for registered executors.")
                    return

            # Extract executor IDs and service names based on their types
            executor_info = defaultdict(list)

            for executor in executors_response:
                executor_type = executor.get("executor_type")
                executor_id = executor.get("executor_id")
                service_name = executor.get("executor_info").get("exp_name")
                if executor_type and executor_id and service_name:
                    executor_info[executor_type].append((executor_id, service_name))

            if not executor_info:
                print("No services are currently registered.")
            else:
                # Print available executor IDs and service names for each type
                print("\nAvailable Registered Services:\n" + "-"*30)
                for executor_type, info in executor_info.items():
                    print(f"\n{executor_type.upper()} Services:")
                    for id, name in info:
                        print(f"  - ID: {id}, Service Name: {name}")
                print("\n" + "-"*30)

        except Exception as e:
            print(f"An error occurred while retrieving registered services: {e}")
    
    #-------------------------------------- Tasksheet Functions----------------------------------------
    # Create Task Sheet Function
    def self_task_sheet(self, payload):
        url = f"{self.base_url}/task_publisher/task_sheet"
        data = {'act': 'create'}
        data.update(payload)
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from response: {response.text}")
            return None

    
   # Create an XAI and Eval Task Sheet and return its ID.
    def create_task_sheet(self, payload, task_type="Task"):
        if 'task_parameters' in payload:
            payload['task_parameters'] = json.dumps(payload['task_parameters'])
        response = self.self_task_sheet(payload=payload)
        if response is None:
            print("Failed to get a valid response from the server.")
            return None
        if 'task_sheet_id' in response:
            print(f"{task_type} Task Sheet created successfully with the Task_Sheet_ID: {response['task_sheet_id']}")
            return response['task_sheet_id']
        else:
            print(f"Unexpected response format: {response}")
            return None
    
    # Run Task from Task Sheet Function
    def run_task_sheet(self, task_sheet_id, task_type="Task"):
        url = f"{self.base_url}/task_publisher/task_sheet"
        data = {'act': 'run', 'task_sheet_id': task_sheet_id}
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()  # Check for HTTP errors
            response_data = response.json()  # Attempt to decode JSON

        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return None
        except json.decoder.JSONDecodeError:
            print(f"Failed to decode JSON from response: {response.text}")
            return None

        # Check if the task ticket is in the response
        if response_data and 'task_ticket' in response_data:
            task_ticket_id = response_data['task_ticket']
            print(f"{task_type} Task Sheet has started running successfully with the task_ticket_id: {task_ticket_id}")
            return task_ticket_id
        else:
            # Handle the case where 'task_ticket' is not in the response
            error_message = response_data.get('message', 'No specific error message provided')
            print(f"Failed to start the {task_type} Task Sheet or did not receive a valid task_ticket_id. Error: {error_message}")
            return None

    #Delete Task sheet Function
    def delete_task_sheet(self, task_sheet_id):
        url = f"{self.base_url}/task_publisher/task_sheet"
        data = {'act': 'delete', 'task_sheet_id': task_sheet_id}
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return None
    
    #GET Task Sheet Function
    def get_task_sheet(self):
        url = f"{self.base_url}/task_publisher/task_sheet"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from response: {response.text}")
            return None
    
    #GET Task Sheet Function by task_sheet_id
    def get_task_sheet_by_task_sheet_id(self, task_sheet_ids=None):
        url = f"{self.base_url}/task_publisher/task_sheet"
        params = {}
        if task_sheet_ids:
            params['task_sheet_ids'] = json.dumps(task_sheet_ids)
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from response: {response.text}")
            return None
    
    #-----------------------------------------------------Task Functions----------------------------------------
   
    #Get Task info from task_ticket_id or task_sheet_id
    def get_task(self, task_ticket=None, task_sheet_id=None):
        url = f"{self.base_url}/task_publisher/task"
        params = {}
        if task_ticket:
            params['task_ticket'] = task_ticket
        if task_sheet_id:
            params['task_sheet_id'] = task_sheet_id
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from response: {response.text}")
            return None


    #Get Task Result
    def task_result(self, task_ticket):
        url = f"{self.base_url}/task_publisher/task_result"
        params = {'task_ticket': task_ticket}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from response: {response.text}")
        return None

    
    def update_task_status(self, task_ticket, task_status, running_info):
        url = f"{self.base_url}/task_publisher/task"
        data = {
            'act': 'update_task_status',
            'task_ticket': task_ticket,
            'task_status': task_status,
            'running_info': json.dumps(running_info)
        }
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from response: {response.text}")
            return None


    #stop task
    def stop_task(self, task_ticket):
        url = f"{self.base_url}/task_publisher/task"
        data = {'act': 'stop', 'task_ticket': task_ticket}
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return "Error occurred while stopping the task."


    #delete task
    def delete_task(self, task_ticket):
        url = f"{self.base_url}/task_publisher/task"
        data = {'act': 'delete', 'task_ticket': task_ticket}
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return "Error occurred while deleting the task."


    #--------------------------------------------Pipeline Functions----------------------------------------

    def create_pipeline(self, pipeline_name, xai_task_sheet_id, evaluation_task_sheet_id):
        url = f"{self.base_url}/task_publisher/pipeline"
        data = {
            'act': 'create',
            'pipeline_name': pipeline_name,
            'xai_task_sheet_id': xai_task_sheet_id,
            'evaluation_task_sheet_id': evaluation_task_sheet_id
        }
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            response_data = response.json()

            pipeline_id = response_data.get('pipeline_id')
            if pipeline_id:
                return pipeline_id
            else:
                print("Failed to extract pipeline_id from the response.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from response: {response.text}")
            return None

    #run pipeline
    def run_pipeline(self, pipeline_id):
        url = f"{self.base_url}/task_publisher/pipeline"
        data = {'act': 'run', 'pipeline_id': pipeline_id}
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from response: {response.text}")
            return None


    def delete_pipeline(self, pipeline_id):
        url = f"{self.base_url}/task_publisher/pipeline"
        data = {'act': 'delete', 'pipeline_id': pipeline_id}
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return "Error occurred while deleting the pipeline."

    
    #get all pipelines
    def get_all_pipelines(self):
        url = f"{self.base_url}/task_publisher/pipeline"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred: {e}")
            return []
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from response: {response.text}")
            return []

        
    #-----------------------------------------------Utility Functions----------------------------------- 

    # Function to check if a service is already registered
    def get_registered_service_urls(self, service_type):
        registered_executors = self.get_registered_executors()
        urls = [
            executor.get("executor_endpoint_url")
            for executor in registered_executors
            if executor.get("executor_type") == service_type
        ]
        return urls

    def monitor_task_progress(self, task_sheet_id=None, task_ticket=None):

        if not task_sheet_id and not task_ticket:
            print("Either task_sheet_id or task_ticket must be provided.")
            return

        # Check the task status periodically
        while True:
            try:
                task_info = self.get_task(task_sheet_id=task_sheet_id, task_ticket=task_ticket)
                if not task_info:
                    print("Failed to retrieve task information. Exiting the monitor.")
                    break

            except Exception as e:
                print(f"An error occurred: {e}")
                break
            
            # Check if task_info is a list and extract the relevant dictionary
            if isinstance(task_info, list):
                # Assuming the first dictionary in the list contains the relevant information
                task_info = task_info[0] if task_info else {}

            task_status = task_info.get('task_status')

            with print_lock:
                sys.stdout.write("\033[K")  # Clear the current console line
                if task_status == 'finished':
                    print("\n\nTask finished.")
                    break
                elif task_status in ['failed', 'error']:  # Add any other terminal statuses here
                    print(f"\n\nTask failed with status: {task_status}.")
                    exit()  # or handle the error appropriately
                else:
                    print(f"\n\nTask is still running with status: {task_status}. Waiting...")

                    # Display a progress bar and check the status every second
                    for _ in tqdm(range(30), desc="Processing", ncols=100):
                        time.sleep(1)  # sleep for 1 second
                        # Check the status again
                        task_info = self.get_task(task_sheet_id=task_sheet_id, task_ticket=task_ticket)
                        if isinstance(task_info, list):
                            task_info = task_info[0] if task_info else {}
                        if task_info.get('task_status') == 'finished':
                            break

    def fetch_task_sheet_info(self):
        task_sheets = self.get_task_sheet()
        if not task_sheets:
            print("No task sheets found.")
            return
        for task_sheet in task_sheets:
            task_sheet_id = task_sheet.get('task_sheet_id')
            task_sheet_name = task_sheet.get('task_sheet_name')
            task_type = task_sheet.get('task_type')
            print(f"Task Sheet ID: {task_sheet_id}, Task Sheet Name: {task_sheet_name}, Task Type: {task_type}")


    # Function to get the latest task sheet name index
    def get_latest_task_sheet_index(self, task_type):
        task_sheets = self.get_task_sheet()
        if not task_sheets:
            return 0

        indices = [0]
        for sheet in task_sheets:
            try:
                if task_type in sheet.get('task_sheet_name', ''):
                    index = int(sheet.get('task_sheet_name').split(task_type)[1])
                    indices.append(index)
            except (ValueError, IndexError):
                pass
        return max(indices)


    # Function to get the latest pipeline index
    def get_latest_pipeline_index(self, pipelines):
        if not pipelines:
            return 0

        indices = []
        for pipeline in pipelines:
            name = pipeline.get('pipeline_name', '')
            match = re.search(r'pipeline(\d+)', name)
            if match:
                try:
                    index = int(match.group(1))
                    indices.append(index)
                except ValueError:
                    pass
        return max(indices, default=0)

    
    #-------------------------------------------Functions using Configuration YAML file----------------------------------

    def register_service_from_config(self, config_path=None):

        if not config_path:
            config_path = pkg_resources.resource_filename('xai_sdk.xai_sdk', 'sdk_config.yaml')

        # Load the configuration from the yaml file
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        # Extract the services from the configuration
        services = config.get('services', {})
        if not services:
            print("No services found in the configuration.")
            return

        # Loop through each service type and its list of services
        for service_type, service_list in services.items():
            if not isinstance(service_list, list):
                print(f"Invalid format for service list under '{service_type}'.")
                continue

            for service_data in service_list:
                url = service_data.get('url')
                executor_info = service_data.get('info')

                if not url or not executor_info:
                    print(f"Missing required data for service registration in '{service_type}'.")
                    continue

                # preparing the request data
                request_data = {
                    'act': 'reg',
                    'executor_endpoint_url': url,
                    'executor_type': service_type,
                    'executor_info': executor_info
                }

                # Register the service
                response = self.register_executor_endpoint(**request_data)

                # Check the response and print a message
                if response.get('status') == 'error':
                    print(f"Failed to register service with URL {url}. Reason: {response.get('message')}")
                else:
                    print(f"Successfully registered service with executor_id:{response.get('executor_id')} and the URL {url}")

    def create_task_sheet_from_config(self, config_path=None):
        # If no path is provided, use the default path from the package
        if not config_path:
            config_path = pkg_resources.resource_filename('xai_sdk.xai_sdk', 'sdk_config.yaml')

        # Load the configuration from the yaml file
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        # Extract the xai task sheets and evaluation task sheets from the configuration
        xai_task_sheets = config.get('xai_task_sheets', [])
        evaluation_task_sheets = config.get('evaluation_task_sheets', [])

        # Loop through each xai task sheet payload and create it
        for payload in xai_task_sheets:
            #print(f"Sending XAI Task Sheet request with payload: {payload}")  # Print the request details
            self.create_task_sheet(payload, task_type=payload.get('task_type', 'Task'))

        # Loop through each evaluation task sheet payload and create it
        for payload in evaluation_task_sheets:
            #print(f"Sending Evaluation Task Sheet request with payload: {payload}")  # Print the request details
            self.create_task_sheet(payload, task_type=payload.get('task_type', 'Evaluation'))

    def run_task_sheet_from_config(self, config_path=None):
        # If no path is provided, use the default path from the package
        if not config_path:
            config_path = pkg_resources.resource_filename('xai_sdk.xai_sdk', 'sdk_config.yaml')

        # Load the configuration from the yaml file
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        # Extract the xai task sheet IDs and evaluation task sheet IDs from the configuration
        xai_task_sheet_ids = [item.get('task_sheet_id') for item in config.get('xai_task_sheet_ids', [])]
        evaluation_task_sheet_ids = [item.get('task_sheet_id') for item in config.get('evaluation_task_sheet_ids', [])]

        # Loop through each xai task sheet ID and run it
        for task_sheet_id in xai_task_sheet_ids:
            if task_sheet_id:
                self.run_task_sheet(task_sheet_id, task_type="XAI")

        # Loop through each evaluation task sheet ID and run it
        for task_sheet_id in evaluation_task_sheet_ids:
            if task_sheet_id:
                self.run_task_sheet(task_sheet_id, task_type="Evaluation")

    
    def create_and_run_task_sheet_from_config(self, config_path=None):
        # If no path is provided, use the default path from the package
        if not config_path:
            config_path = pkg_resources.resource_filename('xai_sdk.xai_sdk', 'sdk_config.yaml')

        # Load the configuration from the yaml file
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        # Extract the xai task sheets and evaluation task sheets from the configuration
        xai_task_sheets = config.get('xai_task_sheets', [])
        evaluation_task_sheets = config.get('evaluation_task_sheets', [])

        for idx, payload in enumerate(xai_task_sheets):
            xai_task_sheet_id = self.create_task_sheet(payload, task_type=payload.get('task_type', 'Task'))
            if xai_task_sheet_id:
                task_ticket = self.run_task_sheet(xai_task_sheet_id, task_type="XAI")
                if task_ticket:
                    # Start the task monitoring in a separate thread
                    monitor_thread = threading.Thread(target=self.monitor_task_progress, args=(xai_task_sheet_id, None))
                    monitor_thread.start()
                    monitor_thread.join()  # Wait for the monitoring thread to complete
                else:
                    print(f"Failed to run XAI Task Sheet with ID: {xai_task_sheet_id}")

                # Update the explanation_task_ticket in the corresponding evaluation task sheet payload
                if idx < len(evaluation_task_sheets):  # Ensure we don't go out of bounds
                    evaluation_task_sheets[idx]['task_parameters']['explanation_task_ticket'] = task_ticket

                # Now, run the corresponding evaluation task sheet
                eval_payload = evaluation_task_sheets[idx]
                eval_task_sheet_id = self.create_task_sheet(eval_payload, task_type=eval_payload.get('task_type', 'Evaluation'))
                if eval_task_sheet_id:
                    self.run_task_sheet(eval_task_sheet_id, task_type="Evaluation")
                else:
                    print(f"Failed to create Evaluation Task Sheet for payload: {eval_payload}")
            else:
                print(f"Failed to create XAI Task Sheet for payload: {payload}")


    def create_and_run_pipeline_from_config(self, config_path=None):
        # If no path is provided, use the default path from the package
        if not config_path:
            config_path = pkg_resources.resource_filename('xai_sdk.xai_sdk', 'sdk_config.yaml')

        # Load the configuration from the yaml file
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        # Extract the pipelines from the configuration
        pipelines = config.get('pipelines', [])
        if not pipelines:
            print("No pipeline configurations found.")
            return

        # Loop through each pipeline configuration
        for pipeline_config in pipelines:
            pipeline_name = pipeline_config['name']
            xai_task_sheet_id = pipeline_config['xai_task_sheet_id']
            evaluation_task_sheet_id = pipeline_config['evaluation_task_sheet_id']

            if not all([pipeline_name, xai_task_sheet_id, evaluation_task_sheet_id]):
                print(f"Missing required information in pipeline configuration: {pipeline_config}")
                continue

            pipeline_id = self.create_pipeline(pipeline_name, xai_task_sheet_id, evaluation_task_sheet_id)
            if pipeline_id:
                self.run_pipeline(pipeline_id)
            else:
                print(f"Failed to create or run pipeline: {pipeline_name}")

        print("All pipelines have been created and started running.")