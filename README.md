## docker-compose up --build

Check routes

```bash
flask --app db_service routes
flask --app model_service/resnet50 routes
flask --app xai_service/pytorch_cam routes

```

Run debug mode

```bash
flask --app model_service/resnet50 --debug run -p 5001
flask --app db_service --debug run -p 5002
flask --app xai_service/pytorch_cam --debug run -p 5003
flask --app evaluation_service --debug run -p 5004
```

# XAI Service Frontend

This is the frontend for the eXplainable AI service.

The project uses [Next.js](https://nextjs.org) framework, styled with [Tailwindcss](https://tailwindcss.com), and [Prisma ORM](https://prisma.io).

It is hosted on [Vercel](https://vercel.com).

## Development Prequisites:

-   Node >= `18.x`
-   npm >= `8.18.0`
-   Docker Engine

## Quickstart

-   Configure your `.env` environment variables from `.env.template`
-   Clone the project: `git clone https://github.com/ZeruiW/XAI-Service`
-   Change directory into cloned folder: `cd XAI-Service`
-   Install node depencies: `npm i`
-   Start development server: `npm run dev`

# XAI Service Backend

### Example XAI task setting
{"method_name":"hirescam","data_set_name":"azure_cog","data_set_group_name":"1500","model_name":"resnet50"}
### Example evaluation task setting
{"explanation_task_ticket":"CRx1G9HCKKsh4Qs.9OF7NXAJSL"}
## Local Dev

### MongoDB

Please have the `mongo.dev.conf` or `mongo.pred.conf` under the backend folder.

``` properties
conn_str=<<your mongodb url str>>
```



### Azure Blob Service

Please have the `az_blob_connection_str.json`  under the backend folder:

1. `backend/central/central_storage/tmp/az_blob_connection_str.json`;
2. `backend/db_service/azure_blob/azure_blob_storage/tmp/az_blob_connection_str.json`

The file is private, if you need them, please contact JUN. Or you can deploy your own Azure Blob Service.

### Run In Different Env Mode

Please use:

``` bash
flask --app 'backend/central:create_app("dev")' run -p 5006
```

or 

``` bash
flask --app 'backend/central:create_app("pred")' run -p 5006
```

to start the flask application.



## Run Docker in Dev Env

### 1. Start-Up Local MySQL

If you are the first time, please also create a volume for MySQL.

``` bash
docker volume create xaifw-mysql
```

Then:

``` bash
docker compose -f backend/db_service/docker-compos-mysql.yaml up -d
```

### 2. Volume for All the Services

``` bash
docker volume create xai_fw_volumes
```

### 3. Bring Up Services

```bash
docker compose -f backend/docker-compose.yml -f backend/docker-compose-dev.yml up --build
```

Or for single service:

```bash
docker compose -f backend/docker-compose.yml -f backend/docker-compose-dev.yml up [service_name] --build
```


Densenet121 service:

   ``` bash
   flask --app backend/model_service/densenet121 run -p 5010
   ```

multiple cam method support

   To start grad-cam:

   ``` bash
   flask --app 'backend/xai_service/pytorch_cam:create_app(cam_method="grad-cam")' run -p 5003
   ```

   or just

   ``` bash
   flask --app backend/xai_service/pytorch_cam run -p 5003
   ```

   Then the service endpoint is same as before:

   http://127.0.0.1:5003/xai/pt_cam

   To start other cams, like `grad-camew`:

   ``` bash
   flask --app 'backend/xai_service/pytorch_cam:create_app(cam_method="grad-camew")' run -p 5011
   ```

   The service endpoint will be:

   http://127.0.0.1:5011/xai/pt_cam/grad-camew

   Cam method List:

   ``` python
   if cam_method == None or cam_method == 'grad-cam':
       cam = GradCAM(**cam_kws)
   
   if cam_method == 'hirescam':
       cam = HiResCAM(**cam_kws)
   
   if cam_method == 'scorecam':
       cam = ScoreCAM(**cam_kws)
   
   if cam_method == 'grad-campp':
       cam = GradCAMPlusPlus(**cam_kws)
   
   if cam_method == 'ablationcam':
       cam = AblationCAM(**cam_kws)
   
   if cam_method == 'xgrad-cam':
       cam = XGradCAM(**cam_kws)
   
   if cam_method == 'eigencam':
       cam = EigenCAM(**cam_kws)
   
   if cam_method == 'eigengrad-cam':
       cam = EigenGradCAM(**cam_kws)
   
   if cam_method == 'layercam':
       cam = LayerCAM(**cam_kws)
   
   if cam_method == 'fullgrad':
       cam = FullGrad(**cam_kws)
   
   if cam_method == 'grad-camew':
       cam = GradCAMElementWise(**cam_kws)
   ```

   


flask --app backend/db_service/image_net_1000  run -p 5002
flask --app backend/db_service/azure_blob run -p 5009
flask --app backend/central run -p 5006
flask --app backend/model_service/resnet50 run -p 5001
flask --app backend/model_service/azure_cog run -p 5007
flask --app backend/model_service/densenet121 run -p 5010
flask --app 'backend/xai_service/pytorch_cam:create_app(cam_method="grad-cam")' run -p 5003
flask --app backend/evaluation_service run -p 5004
flask --app backend/model_service/xgb run -p 5011
flask --app backend/xai_service/shap_tabular run -p 5012
flask --app backend/model_service/google_image_class run -p 5013
flask --app 'backend/xai_service/pytorch_cam:create_app(cam_method="hirescam")' run -p 5014
flask --app 'backend/xai_service/pytorch_cam:create_app(cam_method="scorecam")' run -p 5015
flask --app 'backend/xai_service/pytorch_cam:create_app(cam_method="grad-campp")' run -p 5016
flask --app 'backend/xai_service/pytorch_cam:create_app(cam_method="ablationcam")' run -p 5017
flask --app 'backend/xai_service/pytorch_cam:create_app(cam_method="xgrad-cam")' run -p 5018
flask --app 'backend/xai_service/pytorch_cam:create_app(cam_method="eigencam")' run -p 5019
flask --app 'backend/xai_service/pytorch_cam:create_app(cam_method="eigengrad-cam")' run -p 5020
flask --app 'backend/xai_service/pytorch_cam:create_app(cam_method="layercam")' run -p 5021
flask --app 'backend/xai_service/pytorch_cam:create_app(cam_method="grad-camew")' run -p 5022
flask --app 'backend/xai_service/pytorch_cam:create_app(cam_method="fullgrad")' run -p 5023
flask --app backend/model_service/amazon_rek run -p 5024
flask --app backend/model_service/alibaba_ml run -p 5025
flask --app backend/model_service/hf_resnet50 run -p 5026