FROM python:3.11-slim

MAINTAINER Aliakseeva

COPY . ./app

WORKDIR /app

RUN pip install -r requirements.txt --no-cache-dir
