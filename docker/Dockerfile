FROM python:3.12-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    pip install --upgrade pip && \
    pip install pipenv && \
    rm -rf /var/lib/apt/lists/*

COPY ./src/Pipfile ./src/Pipfile.lock /tmp/
RUN cd /tmp && pipenv install --dev --system

WORKDIR /app/src
ENV PYTHONPATH=/app/src
