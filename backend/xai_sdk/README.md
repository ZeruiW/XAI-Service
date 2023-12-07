# XAI-Service SDK: User Guide

The SDK Gateway is meticulously designed to streamline the process of XAI Evaluation. Acting as a central access point, it enables swift interaction with various services orchestrated by the coordination center. Upon initialization, the SDK instantiates the publisher, which subsequently registers pivotal components: Database, AI Model, XAI Model, and Evaluation. Most Importantly, SDK helps users to register multiple services, create multiple task_sheets and run multiple pipelines with just one function call. Moreover, each component is modifiable, allowing users to adjust configurations to their specific requirements.

## Getting Started with XAI-Service SDK

### Step 1: Installation

1. #### Install the SDK:
   Use the following command to install the XAI-Service SDK from the Test PyPI repository:
   
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --no-deps xai_sdk
   ```

3. #### Install Dependencies:
   Next, install the required dependencies:
   
   ```bash
   pip install requests tqdm pyyaml
   ```
### Step 2: Setup

1. #### Prepare the Client Environment:
   Navigate to the directory ```/backend/sdk_client/``` where you need to create the "sdk_client.py" file and the configuration file named "sdk_config.yaml". "Example files are provided as templates to guide you."

2. #### Import SDKInterface:
   In client.py, import the SDKInterface from the SDK:
   
   ```bash
   from xai_sdk import SDKInterface
   ```
   Note: SDKInterface is part of the XAI_SDK which encapsulates the functionalities of all manager classes in the SDK, providing a unified and simplified API.

3. #### Initialize SDKInterface:
   Define the SDKInterface with the base_url of your publisher endpoint and assign it to a variable named sdk:
   
   ```bash
   sdk = SDKInterface(base_url= "http://publisher_endpoint_url")
   ```
### Step 3: Configuration

1. #### Set Configuration Path or String:
   You have two options for configuration:

   #### a) File Path Configuration:
   Set config_file_path to your YAML file path. Ensure sdk_config.yaml is in the same directory as client.py.

      ```config_source = "sdk_config_dev.yaml"```
   
   #### b) String-Based Configuration:
   Alternatively, define the configuration as a YAML-formatted string.

      ```bash
      config_source = """
      pipelines:
          - name: "pipeline2"
            xai_task_sheet_id: "8IU7NIAVYWJ0D0L"
            evaluation_task_sheet_id: "VKNWMX6I9O2OVHF"
      """
      ```

### Step 4: Activate Publisher

1. #### Activate the Publisher:
   Before using the SDK services, activate the publisher:
    
    ```bash
    sdk.activate_publisher("your_publisher_endpoint_url")
    ``` 
### Step 5: Utilizing SDK Services

1. #### Service Registration and Management:
   Utilize the following functions in client.py to manage XAI-pipelines:

   * Register Services:
   
      ```sdk.register_service_from_config(config_source)```

   * Get Registered Services Info:

      ```sdk.get_registered_services()```

   * Create and Run Task Sheets:

      ```sdk.create_and_run_task_sheet_from_config(config_source)```

   * Get Task sheets Info:

      ```sdk.fetch_task_sheet_info()```

   * Create and run pipelines:

      ```sdk.create_and_run_pipeline_from_config(config_source)```

   * Get Pipelines Info:

      ```sdk.get_all_pipelines()```

2. #### Additional Task Sheet and Task Management Functions:
   
   * Delete Task Sheet:

       ```sdk.delete_task_sheet("some_task_sheet_id")```

   * Get Task Sheet by ID:

       ```sdk.get_task_sheet_by_task_sheet_id(["some_task_sheet_id"])```

   * Get Task Result:

       ```sdk.task_result("some_task_ticket_id")```

   * Stop task:
     
       ```sdk.stop_task("some_task_ticket")```

   * Delete Task:
     
       ```sdk.delete_task("some_task_ticket")```

### Additional Information

For further details and comprehensive guidance, please visit the main repository of the XAI-Service project: [XAI-Service GitHub Repository](https://github.com/ZeruiW/XAI-Service)
