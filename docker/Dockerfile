FROM python:3.8

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install gunicorn uvicorn

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY ./api /app/api
