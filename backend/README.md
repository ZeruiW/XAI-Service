# docker-compose up --build

Check routes

```bash
flask --app db_service routes
flask --app model_service/resnet50 routes
flask --app xai_service/pytorch_cam routes

```

Run debug mode

```bash
database_service:
flask --app db_service --debug run -p 5002

AI model Sercice:
flask --app model_service/resnet50 --debug run -p 5001

evaluation service:
flask --app evaluation_service --debug run -p 5004

XAI service:
(the only difference are ports and endpoints, the operations are same.)
flask --app xai_service/pytorch_cam --debug run -p 5003
flask --app xai_service/pytorch_gradcampp --debug run -p 5005
flask --app xai_service/pytorch_layercam --debug run -p 5006
```
