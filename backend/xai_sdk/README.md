The SDK Gateway is meticulously designed to streamline the process of XAI Evaluation. Acting as a central access point, it enables swift interaction with various services orchestrated by the coordination center. Upon initialization, the SDK instantiates the publisher, which subsequently registers pivotal components: Database, AI Model, XAI Model, and Evaluation. Most Importantly, SDK helps users to register multiple services, create multiple task_sheets and run multiple pipelines with just one function call. Moreover, each component is modifiable, allowing users to adjust configurations to their specific requirements.

************************************ Steps to use the SDK for the XAI-Service *********************************

1. First Install the SDK using the command "pip install --index-url https://test.pypi.org/simple/ --no-deps xai_sdk"

2. Now install the dependencies using the command "pip install requests tqdm pyyaml"

3. Now, create a python file named as "client.py" and a configuration file named as "sdk_config.yaml" in your root backend      
   directory "/XAI-Service/backend"

4. Now set the absolute path for the sdk_config.yaml as an environment varaible "XAI_SDK_CONFIG_PATH" using the command 
   For Unix/Linux/macOS:
   bash'''export XAI_SDK_CONFIG_PATH=/absolute-path/to/your/sdk_config.yaml'''

   For Windows Command Prompt:
   bash'''set XAI_SDK_CONFIG_PATH=C:\absolute-path\to\your\sdk_config.yaml'''

   For Windows PowerShell:
   bash'''$env:XAI_SDK_CONFIG_PATH="C:\absolute-path\to\your\config.yaml" '''


5. Now, In the client.py, import the "TaskpublisherClient" from the SDK using the command "from xai_sdk import 
   TaskPublisherClient"

6. Define the TaskPublisherClient with the 'base_url' which is the url of the central-service and define it to 'sdk'
   sdk = TaskPublisherClient(base_url="publisher_endpoint_url")

7. Now, Before calling all the services to create an XAI-Pipeline. Make sure you activate the publisher by calling the function
    # Activate Publisher
    sdk.activate_publisher("your_publisher_endpoint_url") 
   
8. Now, you can call all the functions using "sdk.your_function()"

9. Make sure to add relevant data in "sdk_config.yaml" before calling each of these           
   functions. (Sample YAML file is already provided in the repository)

   You can register multiple services, create and run multiple task_sheets and pipelines using sdk_config.yaml.               Refer the file for more understanding.

10. Here are the list of essential functions that are used to create XAI-pipelines. You can use these services in the "client.py"

    # Register Services
    #sdk.register_service_from_config()

    # Get Registered services Info
    #sdk.get_registered_services()

    # Create and Run Task Sheets
    #sdk.create_and_run_task_sheet_from_config()

    # Get Task sheets Info
    #sdk.fetch_task_sheet_info()

    # Create and run pipelines paralelly
    #sdk.create_and_run_pipeline_from_config()

    # Get Pipelines Info
    #sdk.get_all_pipelines()

11. Other Essential functions
    #------------------------------Task Sheet Functions--------------------

    # Delete Task sheet
    #sdk.delete_task_sheet("some_task_sheet_id")

    # GET Task Sheet by task_sheet_id
    #sdk.get_task_sheet_by_task_sheet_id(["some_task_sheet_id"])

    #----------------------------- Task functions----------------------

    # Get Task Result
    #sdk.task_result("nyEuJA8KvUnmhtn.6KGCOFN88Q")

    # Stop task
    #sdk.stop_task("some_task_ticket")

    # Delete task
    #sdk.delete_task("some_task_ticket")

12. You can always type "sdk." in the client.py to see all the functions that can be called using this SDK.

Please refer to the main repository of this project for more information about the XAI-Service.
https://github.com/ZeruiW/XAI-Service