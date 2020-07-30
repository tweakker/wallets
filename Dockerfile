FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat


WORKDIR /code
COPY . /code/

RUN pip install -r requirements.txt
