# syntax=docker/dockerfile:1
FROM python:3.10-buster
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
#COPY requirements.txt /app/
#RUN pip install -r requirements.txt
COPY ./app /app/
COPY run.sh /run.sh
RUN chmod +x /run.sh
