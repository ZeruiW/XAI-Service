1. Start mongo container

   ```bash
   docker compose -f backend/docker-compose.yml -f backend/docker-compose-dev.yml up mongo --build
   ```

2. Start Central:

   ``` bash
   pip install -q backend/central_dev/. && flask --app 'backend/central:create_app("dev")' run -p 5006
   ```

3. Start Azure blob service

   Please have a `backend/db_service/azure_blob/azure_blob_storage/tmp/az_blob_connection_str.json` file and provide the connection string:
   ``` json
   {
       "connection_str": "ask Jun for the private key"
   }
   ```

   Then run:

   ``` bash
   flask --app backend/db_service/azure_blob run -p 5009  
   ```

4. Start ResNet50:

   ``` bash
   flask --app backend/model_service/resnet50 run -p 5001      
   ```

5. Start Grad-CAM XAI:

   ``` bash
   flask --app 'backend/xai_service/pytorch_cam:create_app(cam_method="grad-cam")' run -p 5003
   ```

6. Start Eval Service:

   ``` bash
   flask --app backend/evaluation_service run -p 5004
   ```

7. Start Frontend:

   ``` bash
   docker compose -f frontend-x/docker-compose.yml up fex --build
   ```



Check this link for API and use case:

https://www.postman.com/youyinnn/workspace/concordia/collection/2019955-72d3c5f3-2070-4bba-97de-d5990085b20e?action=share&creator=2019955&active-environment=2019955-c8be28eb-2739-48db-89b7-a74fc752029c

1. activate the central;
2. register db, xai, model, evaluation service;
3. create xai tasksheet, available config for demo:
   ``` json
   {
       "method_name": "grad-cam",
       "data_set_name": "imagenet1000",
       "data_set_group_name": "g0",
       "model_name": "resnet50",
       "executor_config": {
           "use_pytorch_multiprocess": true
       }
   }
   ```
5. run the task;
6. check the result;
