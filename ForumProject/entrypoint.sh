#!/bin/sh

/app/dockerize -wait tcp://postgres_lib:5432 -timeout 60s

echo "Applying database migrations..."
python3 manage.py migrate

echo "Creating superuser..."
python3 manage.py shell << END
from django.contrib.auth import get_user_model
import os

User = get_user_model()
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password)
    print("Superuser created")
else:
    print("Superuser already exists")
END

echo "Starting Django server..."
python3 manage.py runserver 0.0.0.0:8000