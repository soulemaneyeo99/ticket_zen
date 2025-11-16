# 🎫 Ticket Zen - Backend API

Plateforme complète de billetterie digitale pour transport interurbain en Côte d'Ivoire.

## 🚀 Fonctionnalités

### Pour les Voyageurs
- ✅ Recherche de trajets (départ/arrivée/date)
- ✅ Réservation de tickets avec choix de siège
- ✅ Paiement en ligne (Orange Money, MTN, Moov, Wave, Visa, Mastercard)
- ✅ QR code sécurisé (JWT RS256)
- ✅ Historique des voyages
- ✅ Gestion des réclamations

### Pour les Compagnies
- ✅ Gestion complète des voyages (CRUD)
- ✅ Gestion de la flotte de véhicules
- ✅ Dashboard avec statistiques en temps réel
- ✅ Gestion des embarqueurs
- ✅ Export de rapports (CSV, Excel, PDF)

### Pour les Embarqueurs
- ✅ Application mobile pour scanner les QR codes
- ✅ Validation des tickets même hors ligne
- ✅ Synchronisation automatique
- ✅ Vue des voyages du jour

### Pour les Administrateurs
- ✅ Validation/Rejet des compagnies
- ✅ Gestion globale des utilisateurs
- ✅ Supervision de toutes les transactions
- ✅ Statistiques globales de la plateforme
- ✅ Gestion des réclamations
- ✅ Configuration des paramètres

## 🛠️ Technologies

- **Backend**: Django 5.0 + Django REST Framework
- **Base de données**: PostgreSQL
- **Cache**: Redis
- **Tâches asynchrones**: Celery
- **Authentification**: JWT (Simple JWT)
- **QR Codes**: PyJWT + Cryptographie RS256
- **Paiements**: CinetPay (mocké pour développement)
- **Documentation**: drf-spectacular (Swagger/OpenAPI)
- **Containerisation**: Docker + Docker Compose

## 📋 Prérequis

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (optionnel)

## 🔧 Installation

### 1. Cloner le repository
```bash
git clone https://github.com/votre-repo/ticket-zen-backend.git
cd ticket-zen-backend
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

### 5. Générer les clés RSA pour QR codes
```bash
python manage.py shell
>>> from utils.qr_generator import ensure_rsa_keys_exist
>>> ensure_rsa_keys_exist()
>>> exit()
```

### 6. Créer la base de données
```bash
# Créer la base PostgreSQL
createdb ticketzen_db

# Appliquer les migrations
python manage.py migrate
```

### 7. Créer un superuser
```bash
python manage.py createsuperuser
```

### 8. Lancer le serveur
```bash
python manage.py runserver
```

L'API sera disponible sur `http://localhost:8000`

## 🐳 Installation avec Docker
```bash
# Lancer tous les services
docker-compose up -d

# Appliquer les migrations
docker-compose exec backend python manage.py migrate

# Créer un superuser
docker-compose exec backend python manage.py createsuperuser

# Voir les logs
docker-compose logs -f
```

## 📚 Documentation API

Une fois le serveur lancé, accédez à :

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema OpenAPI**: http://localhost:8000/api/schema/

## 🧪 Tests

### Tester le flow de paiement
```bash
# Paiement réussi
python manage.py test_payment_flow --scenario=success

# Paiement échoué
python manage.py test_payment_flow --scenario=failed

# Remboursement
python manage.py test_payment_flow --scenario=refund
```

### Lancer les tests unitaires
```bash
pytest
```

### Avec couverture
```bash
pytest --cov=apps --cov-report=html
```

## 📂 Structure du projet
```
ticket_zen_backend/
├── apps/                      # Applications Django
│   ├── users/                # Gestion utilisateurs & auth
│   ├── companies/            # Gestion compagnies
│   ├── trips/                # Gestion voyages
│   ├── tickets/              # Gestion tickets/réservations
│   ├── payments/             # Gestion paiements
│   ├── boarding/             # Gestion embarquements
│   ├── fleet/                # Gestion flotte véhicules
│   ├── notifications/        # Système notifications
│   ├── logs/                 # Logs immuables
│   ├── claims/               # Gestion réclamations
│   └── core/                 # Paramètres plateforme
├── config/                   # Configuration Django
│   ├── settings/             # Settings par environnement
│   ├── urls.py               # URLs principales
│   └── celery.py             # Configuration Celery
├── utils/                    # Utilitaires globaux
│   ├── qr_generator.py       # Génération QR codes
│   ├── qr_validator.py       # Validation QR codes
│   ├── pagination.py         # Pagination custom
│   ├── exceptions.py         # Exceptions custom
│   ├── validators.py         # Validateurs
│   ├── helpers.py            # Fonctions helper
│   ├── exports.py            # Export CSV/Excel/PDF
│   └── permissions.py        # Permissions avancées
├── keys/                     # Clés RSA pour QR codes
├── media/                    # Fichiers uploadés
├── requirements.txt          # Dépendances Python
├── docker-compose.yml        # Configuration Docker
├── Dockerfile                # Image Docker
└── manage.py                 # Script Django
```

## 🔐 Sécurité

- ✅ JWT avec rotation des tokens
- ✅ QR codes signés avec RS256
- ✅ Rate limiting par endpoint
- ✅ CORS configuré strictement
- ✅ Validation stricte des inputs
- ✅ Logs immuables de toutes actions sensibles
- ✅ Protection CSRF, XSS, clickjacking
- ✅ HTTPS only en production

## 🚦 Endpoints principaux

### Authentification
- `POST /api/v1/auth/register/` - Inscription
- `POST /api/v1/auth/login/` - Connexion
- `POST /api/v1/auth/logout/` - Déconnexion

### Voyages
- `GET /api/v1/trips/` - Liste des voyages
- `POST /api/v1/trips/search/` - Rechercher des voyages
- `POST /api/v1/trips/` - Créer un voyage (compagnie)

### Tickets
- `POST /api/v1/tickets/` - Réserver un ticket
- `GET /api/v1/tickets/my-tickets/` - Mes tickets
- `POST /api/v1/tickets/{id}/cancel/` - Annuler un ticket

### Paiements
- `POST /api/v1/payments/initialize/` - Initialiser un paiement
- `POST /api/v1/payments/webhook/` - Webhook CinetPay

### Embarquement
- `POST /api/v1/boarding/` - Scanner un QR code
- `POST /api/v1/boarding/sync-offline/` - Synchroniser scans offline

## 📊 Statistiques & Exports
```bash
# Obtenir les statistiques
GET /api/v1/dashboard/stats/

# Exporter des données
POST /api/v1/export/
{
  "type": "tickets",  # tickets, payments, trips, companies
  "format": "csv",    # csv, excel, pdf
  "date_from": "2025-01-01",
  "date_to": "2025-12-31"
}
```

## 🔄 Tâches Celery

### Lancer Celery Worker
```bash
celery -A config worker -l info
```

### Lancer Celery Beat (tâches planifiées)
```bash
celery -A config beat -l info
```

### Tâches disponibles
- Envoi emails/SMS
- Rappels de voyage
- Nettoyage notifications anciennes
- Génération rapports automatiques

## 🌍 Déploiement

### Variables d'environnement en production
```env
DJANGO_ENV=production
DEBUG=False
ALLOWED_HOSTS=api.ticketzen.com
SECRET_KEY=your-very-secret-key-here

# Base de données
DB_HOST=your-postgres-host
DB_PASSWORD=your-secure-password

# Redis
REDIS_HOST=your-redis-host

# CinetPay (production)
CINETPAY_MODE=PRODUCTION
CINETPAY_API_KEY=real-api-key
CINETPAY_SITE_ID=real-site-id
CINETPAY_SECRET_KEY=real-secret-key
```

### Commandes de déploiement
```bash
# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Appliquer les migrations
python manage.py migrate

# Créer un superuser
python manage.py createsuperuser
```

## 📞 Support

- **Email**: support@ticketzen.com
- **Documentation**: https://docs.ticketzen.com
- **Issues**: https://github.com/votre-repo/ticket-zen-backend/issues

## 📄 Licence

Copyright © 2025 Ticket Zen. Tous droits réservés.

## 👥 Équipe

Développé avec ❤️ par l'équipe Ticket Zen

---

**Version**: 1.0.0
**Dernière mise à jour**: 17 Novembre 2025