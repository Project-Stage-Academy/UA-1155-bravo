FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/
RUN apt-get update && apt-get install -y curl && apt-get clean

ADD https://github.com/jwilder/dockerize/releases/download/v0.7.0/dockerize-alpine-linux-amd64-v0.7.0.tar.gz /app/dockerize.tar.gz
RUN tar -C /app -xzf /app/dockerize.tar.gz && rm /app/dockerize.tar.gz

EXPOSE 8000

CMD ["/app/dockerize", "-wait", "tcp://postgres_lib:5432", "-timeout", "60s", "python3", "manage.py", "runserver", "0.0.0.0:8000"]