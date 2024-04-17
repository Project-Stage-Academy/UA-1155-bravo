FROM python:3.9.19-slim-bullseye

RUN apt-get update && apt-get install -y wget && \
    wget https://github.com/jwilder/dockerize/releases/download/v0.6.1/dockerize-linux-amd64-v0.6.1.tar.gz && \
    tar -C /usr/local/bin -xzvf dockerize-linux-amd64-v0.6.1.tar.gz && \
    rm dockerize-linux-amd64-v0.6.1.tar.gz

WORKDIR /ForumProject

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["dockerize", "-wait", "tcp://db:5432", "-timeout", "60s", "python3", "manage.py", "runserver", "0.0.0.0:8000"]