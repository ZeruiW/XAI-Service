### Setup Local MySQL for Development

First time:

```bash
docker compose -f backend/db_service/docker-compos-mysql.yaml up -d
```

```bash
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

```
