# syntax=docker/dockerfile:1
FROM python:3.8-alpine
WORKDIR /xai_framework

RUN python -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["flask", "--app", "db_service", "--debug", "run", "--host=0.0.0.0""-p", "5001"]

