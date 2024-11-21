FROM python:3.12-slim-bookworm

RUN apt-get update && \
    apt-get upgrade -y &&\
    apt-get install ansible -y

COPY requirements.txt /requirements.txt