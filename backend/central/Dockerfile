FROM python:3.8-slim-buster


WORKDIR /central
COPY ./backend/central .
COPY ./backend/central_dev /central_dev

RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*
    
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

RUN pip install /central_dev

EXPOSE 5006
CMD ["flask", "--app", "/central", "run", "--host=0.0.0.0", "-p", "5006"]