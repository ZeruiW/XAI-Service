FROM python:3.8-slim-buster

WORKDIR /model

COPY ../requirements.txt requirements.txt

RUN python -m pip install --upgrade pip \
    
    && pip install -r requirements.txt

COPY . .

EXPOSE 5001

CMD [ "flask", "--app", "resnet50", "run", "--host=0.0.0.0", "-p", "5001"]