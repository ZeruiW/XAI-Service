
docker-compose up --build


### Run ResNet50 Model

Dependence

```bash
pip install -r model_service/resnet50/requirements.txt
pip install -r xai_service/pytorch_cam/requirements.txt

```

Check routes

```bash
flask --app db_service routes
flask --app model_service/resnet50 routes
flask --app xai_service/pytorch_cam routes

```

Run debug mode

```bash
flask --app db_service --debug run
flask --app model_service/resnet50 --debug run --host=0.0.0.0 -p 5001
flask --app xai_service/pytorch_cam --debug run
```

Endpoint                     Methods  Rule
---------------------------  -------  -----------------------
arxiv_cs.list_paper          GET      /db/arxiv_cs/
arxiv_cs.upload_paper        POST     /db/arxiv_cs/
explanation.add_explanation  POST     /db/explanation/
explanation.get_explanation  GET      /db/explanation/
imgnet1000.list_img          GET      /db/imgnet1000/
imgnet1000.upload_paper      POST     /db/imgnet1000/
static                       GET      /static/<path:filename>

Endpoint       Methods    Rule
-------------  ---------  -----------------------
resnet50.pred  GET, POST  /resnet50/
static         GET        /static/<path:filename>

Endpoint             Methods    Rule
-------------------  ---------  -----------------------
pt_cam.list_task     GET, POST  /xai/pt_cam/task
pt_cam.upload_paper  POST       /xai/pt_cam/
static               GET        /static/<path:filename>


--host 0.0.0.0 --port 5000
-p5001

RUN pip install -r model_service/resnet50/requirements.txt
RUN pip install -r xai_service/pytorch_cam/requirements.txt

CMD ["flask", "--app", "model_service/resnet50", "--debug", "run", "-p", "5002"]
CMD ["flask", "--app", "xai_service/pytorch_cam", "--debug", "run", "-p", "5000"]

in db:
docker build --tag db .
docker run -d -p 5000:5000 db


in model:
docker build --tag model .
docker run -d -p 5001:5001 model

in xai:
docker build --tag xai .
docker run -d -p 5002:5002 xai

flask --app model_service/resnet50 --debug run -p 5001
flask --app db_service --debug run -p 5002
flask --app xai_service/pytorch_cam --debug run -p 5003
flask --app evaluation_service --debug run -p 5004