FROM python:python:3.9.19-slim-bullseye

WORKDIR /ForumProject

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]