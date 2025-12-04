FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copie du code source
COPY . .

# Copie du script de démarrage
COPY start.sh /app/start.sh

# Création des répertoires nécessaires
RUN mkdir -p /app/staticfiles /app/media /app/logs /app/keys

# Permissions
RUN chmod +x /app/manage.py /app/start.sh

# Expose le port
EXPOSE 8000

# Commande par défaut
CMD ["/app/start.sh"]