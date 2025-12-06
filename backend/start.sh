#!/bin/bash

# Attendre que la base de données soit prête
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-config.settings.production}
mkdir -p logs
echo "Waiting for database..."
sleep 5

# Exécuter les migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Créer le superuser si les variables d'environnement sont définies
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py shell <<EOF
from apps.users.models import User
import os

email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
first_name = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME', 'Admin')
last_name = os.environ.get('DJANGO_SUPERUSER_LAST_NAME', 'User')

try:
    if not User.objects.filter(email=email).exists():
        User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number='+2250000000000',
            role='admin'
        )
        print(f'Superuser {email} created successfully')
    else:
        print(f'Superuser {email} already exists')
except Exception as e:
    print(f'Error creating superuser: {e}')
EOF
fi

# Démarrer Gunicorn
echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
