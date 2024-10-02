FROM python:3.9-slim-bookworm

RUN apt-get update && \
    apt-get upgrade -y

COPY requirements.txt /requirements.txt
COPY requirements-test.txt /requirements-test.txt

# Install requirements from the project
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-test.txt

RUN rm /requirements*
