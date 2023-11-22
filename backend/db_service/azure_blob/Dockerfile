FROM python:3.8-slim-buster

WORKDIR /db_service/azure_blob
COPY ./backend/db_service/azure_blob .
COPY ./backend/central_dev /central_dev
    
RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

RUN pip install /central_dev

EXPOSE 5009
CMD ["flask", "--app", "/db_service/azure_blob", "run", "--host=0.0.0.0", "-p", "5009"]