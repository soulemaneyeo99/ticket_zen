# 📊 ANALYSE COMPLÈTE DU PROJET TICKET ZEN

**Date**: 26 novembre 2025  
**Version du projet**: 1.0.0  
**Stack**: Django 5.0 + Next.js 16 + PostgreSQL + Redis + Celery

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture globale](#architecture-globale)
3. [Backend - Django](#backend---django)
4. [Frontend - Next.js](#frontend---nextjs)
5. [Base de données](#base-de-données)
6. [Sécurité](#sécurité)
7. [Déploiement](#déploiement)
8. [Points clés et recommandations](#points-clés-et-recommandations)

---

## 🎯 VUE D'ENSEMBLE

### Qu'est-ce que Ticket Zen ?

**Ticket Zen** est une plateforme complète de billetterie digitale pour le transport interurbain en Côte d'Ivoire. Elle permet aux voyageurs de réserver des tickets de bus, de payer en ligne, et aux compagnies de gérer leurs voyages et leur flotte.

### Objectifs
- ✅ Offrir une plateforme de réservation simple et sécurisée
- ✅ Numériser l'accès par QR code sécurisé (JWT RS256)
- ✅ Supporter plusieurs méthodes de paiement locales (Orange Money, MTN, Moov, Wave, Visa, Mastercard)
- ✅ Fournir des outils de gestion pour les compagnies
- ✅ Gérer le suivi des embarquements en temps réel

### Public cible
- 👨‍🚌 **Voyageurs**: Particuliers cherchant à réserver des tickets
- 🏢 **Compagnies**: Entreprises de transport gérant leurs voyages
- 👷 **Embarqueurs**: Agents validant les tickets lors de l'embarquement
- 👨‍💼 **Administrateurs**: Support et supervision de la plateforme

---

## 🏗️ ARCHITECTURE GLOBALE

### Vue d'ensemble de l'infrastructure

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                      │
│  (React 19, TypeScript, TailwindCSS, Zustand)               │
│  Responsive - Desktop & Mobile                              │
└─────────────────────────────────────────┬───────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
            ┌───────▼───────┐    ┌───────▼───────┐    ┌───────▼───────┐
            │  Django API   │    │  Celery Beat  │    │ Celery Worker │
            │  (REST)       │    │ (Scheduled)   │    │ (Async Tasks) │
            │               │    │               │    │               │
            │ Port: 8000    │    │ Tâches planif │    │ Emails/SMS    │
            └───────┬───────┘    └───────┬───────┘    └───────┬───────┘
                    │                    │                     │
                    └────────────────────┼─────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        │                                │                                │
    ┌───▼──────────┐          ┌─────────▼──────────┐          ┌──────────▼────┐
    │ PostgreSQL   │          │      Redis         │          │  Media/Storage │
    │ (Port 5432)  │          │  Cache (Port 6379) │          │ (Uploads)      │
    │              │          │                    │          │                │
    │ • Users      │          │ • Tokens           │          │ • QR Codes     │
    │ • Trips      │          │ • Sessions         │          │ • Avatars      │
    │ • Tickets    │          │ • Celery Tasks     │          │ • Documents    │
    │ • Payments   │          │ • Rate Limiting    │          │                │
    └──────────────┘          └────────────────────┘          └────────────────┘
```

### Flux de données principal

```
1. Voyageur accède au Frontend
2. Frontend appelle l'API Django (JWT Auth)
3. Django traite la requête & accède à PostgreSQL
4. Redis gère le caching & les sessions
5. Celery traite les tâches asynchrones (emails, notifications)
6. Réponse retournée au Frontend
```

---

## 🔧 BACKEND - DJANGO

### Structure des apps Django

Le backend est organisé en **11 applications Django** spécialisées:

#### 1. **👤 `users`** - Gestion des utilisateurs et authentification
**Fichiers clés**: `models.py`, `views.py`, `serializers.py`

**Modèle User**:
- 4 rôles: `VOYAGEUR`, `COMPAGNIE`, `EMBARQUEUR`, `ADMIN`
- Authentification par JWT (Simple JWT)
- Email unique et téléphone indexé
- Avatar optionnel
- Relations avec les compagnies

**Endpoints**:
```
POST   /api/v1/auth/register/      # Inscription
POST   /api/v1/auth/login/         # Connexion
POST   /api/v1/auth/logout/        # Déconnexion
POST   /api/v1/auth/refresh/       # Refresh token
GET    /api/v1/users/me/           # Mon profil
PUT    /api/v1/users/me/           # Modifier profil
POST   /api/v1/users/change-password/
```

#### 2. **🏢 `companies`** - Gestion des compagnies de transport
**Modèle Company**:
- Statuts: `PENDING`, `APPROVED`, `REJECTED`, `SUSPENDED`
- Informations légales: `registration_number`, `tax_id`
- Taux de commission personnalisé (0-100%)
- Statistiques en temps réel
- Logo et documents

**Endpoints**:
```
GET    /api/v1/companies/          # Liste des compagnies
POST   /api/v1/companies/          # Créer (admin)
GET    /api/v1/companies/{id}/     # Détails
PUT    /api/v1/companies/{id}/     # Modifier (admin)
POST   /api/v1/companies/{id}/approve/   # Approuver (admin)
POST   /api/v1/companies/{id}/reject/    # Rejeter (admin)
```

#### 3. **🚌 `trips`** - Gestion des voyages et villes
**Modèles**:

**City**:
- Nom unique avec slug
- Coordonnées GPS (latitude/longitude)
- Statut actif/inactif

**Trip**:
- Statuts: `SCHEDULED`, `BOARDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`
- Liaison compagnie ↔ véhicule ↔ trajets
- Prix base + frais plateforme
- Places disponibles en temps réel
- Heures de départ/arrivée précises

**Endpoints**:
```
GET    /api/v1/trips/              # Tous les voyages
POST   /api/v1/trips/search/       # Chercher (filtres)
POST   /api/v1/trips/              # Créer (compagnie)
GET    /api/v1/trips/{id}/         # Détails + places dispo
PUT    /api/v1/trips/{id}/         # Modifier (compagnie)
POST   /api/v1/trips/{id}/cancel/  # Annuler (compagnie)
POST   /api/v1/trips/{id}/board/   # Commencer embarquement
```

#### 4. **🎫 `tickets`** - Gestion des réservations et tickets
**Modèle Ticket**:
- UUID primaire + numéro unique TZ{DATE}{6 chiffres}
- Statuts: `PENDING`, `CONFIRMED`, `CANCELLED`, `USED`, `EXPIRED`, `REFUNDED`
- Informations passager (peut différer de l'utilisateur)
- Siège numéroté unique par voyage
- QR code sécurisé (JWT RS256)
- Prix + frais plateforme = montant total
- Embardure avec agent et timestamp

**Logique métier**:
- Un ticket en attente → doit être payé dans 15 minutes (configurable)
- Après paiement → QR code généré et peut embarquer
- Validation du ticket par scan QR lors embarquement

**Endpoints**:
```
POST   /api/v1/tickets/            # Réserver (voyageur)
GET    /api/v1/tickets/            # Tous (selon rôle)
GET    /api/v1/tickets/my-tickets/ # Mes tickets (voyageur)
GET    /api/v1/tickets/{id}/       # Détail + QR code
PUT    /api/v1/tickets/{id}/       # Modifier (admin)
POST   /api/v1/tickets/{id}/cancel/ # Annuler (voyageur/admin)
POST   /api/v1/tickets/{id}/verify/ # Vérifier QR code (embarqueur)
```

#### 5. **💳 `payments`** - Gestion des paiements
**Modèle Payment**:
- Méthodes: Orange Money, MTN, Moov, Wave, Visa, Mastercard
- Statuts: `PENDING`, `PROCESSING`, `SUCCESS`, `FAILED`, `CANCELLED`, `REFUNDED`
- Transaction ID unique (tracking)
- Montant original, frais, montant final
- Webhook CinetPay pour confirmation
- Historique des tentatives

**Flux de paiement**:
```
1. Client initialise paiement → Payment.PENDING
2. Redirection vers CinetPay
3. Webhook retour → Payment.SUCCESS + Ticket.CONFIRMED + QR code généré
4. Alternative: Payment.FAILED → ticket reste en attente
```

**Endpoints**:
```
POST   /api/v1/payments/initialize/  # Initialiser
POST   /api/v1/payments/webhook/     # Webhook CinetPay
GET    /api/v1/payments/             # Historique
POST   /api/v1/payments/{id}/refund/ # Rembourser
```

#### 6. **🚪 `boarding`** - Gestion des embarquements
**Modèle BoardingPass**:
- Scan d'un QR code par l'embarqueur
- Statuts de scan: `VALID`, `INVALID`, `ALREADY_USED`, `EXPIRED`, `WRONG_TRIP`
- Localisation GPS du scan
- Info appareil et système
- Historique complet pour audit

**Endpoints**:
```
POST   /api/v1/boarding/            # Scanner QR
GET    /api/v1/boarding/            # Historique scans
POST   /api/v1/boarding/sync-offline/ # Sync données offline
```

#### 7. **🚗 `fleet`** - Gestion de la flotte de véhicules
**Modèle Vehicle**:
- Types: BUS, MINIBUS, VAN, CAR
- Statuts: ACTIVE, MAINTENANCE, INACTIVE
- Immatriculation unique
- Capacité sièges + configuration JSON
- Équipements (climatisation, toilettes, WiFi)
- Document assurage

**Endpoints**:
```
GET    /api/v1/vehicles/
POST   /api/v1/vehicles/            # Créer (compagnie)
GET    /api/v1/vehicles/{id}/
PUT    /api/v1/vehicles/{id}/       # Modifier
DELETE /api/v1/vehicles/{id}/       # Supprimer
POST   /api/v1/vehicles/{id}/maintenance/
```

#### 8. **📢 `notifications`** - Système de notifications
**Modèle Notification**:
- Types: EMAIL, SMS, IN_APP, PUSH
- Catégories: BOOKING_CONFIRMATION, PAYMENT_SUCCESS, TRIP_REMINDER, etc.
- Statuts: PENDING, SENT, FAILED, READ
- Templates personnalisables
- Contenu + métadonnées JSON

**Tâches Celery asynchrones**:
- Envoi emails (confirmation, rappels)
- Envoi SMS (notifications critiques)
- Notifications in-app

**Endpoints**:
```
GET    /api/v1/notifications/
POST   /api/v1/notifications/{id}/mark-read/
DELETE /api/v1/notifications/{id}/
```

#### 9. **📊 `logs`** - Logs immuables (audit trail)
**Modèle ActivityLog**:
- Enregistre TOUTES les actions sensibles
- Immuable (pas de modification après création)
- Utilisateur + action + ressource + ancien/nouveau
- Timestamp précis
- IP de l'utilisateur

**Actions tracées**:
- Login/logout
- Création/modification/suppression ressources
- Paiements
- Embarquements
- Accès données sensibles

**Endpoints**:
```
GET    /api/v1/logs/
GET    /api/v1/logs/by-user/{user_id}/
GET    /api/v1/logs/by-resource/{resource_type}/{resource_id}/
```

#### 10. **🎤 `claims`** - Gestion des réclamations
**Modèle Claim**:
- Types: LOST_ITEM, MISSED_TRIP, ACCIDENT, OTHER
- Priorités: LOW, MEDIUM, HIGH, CRITICAL
- Statuts: OPEN, IN_PROGRESS, RESOLVED, CLOSED
- Attachement de pièces jointes
- Discussion/commentaires

**Endpoints**:
```
POST   /api/v1/claims/             # Créer (voyageur)
GET    /api/v1/claims/             # Voir (selon rôle)
PUT    /api/v1/claims/{id}/        # Modifier statut (admin)
POST   /api/v1/claims/{id}/comment/ # Commenter
```

#### 11. **⚙️ `core`** - Paramètres et configuration globale
**Modèle PlatformSettings**:
- Singleton (une seule instance)
- Paramètres de maintenance
- Limites de prix min/max
- Expiration QR code (24h par défaut)
- Timeout paiement (15 min)
- Email/téléphone support
- Surréservation autorisée ?
- Rappels voyage (X heures avant)

**Autres modèles**:
- **FAQ**: Q&A pour utilisateurs
- **Banner**: Annonces/promotions

**Endpoints**:
```
GET    /api/v1/settings/           # Paramètres actuels
PUT    /api/v1/settings/           # Modifier (admin)
GET    /api/v1/faqs/
POST   /api/v1/faqs/               # Créer (admin)
GET    /api/v1/banners/
```

### Configuration Django

**Fichiers de configuration**:
```
config/settings/
├── base.py           # Configuration partagée
├── development.py    # Développement
├── production.py     # Production
└── test.py          # Tests
```

**Base de données**: PostgreSQL 16+
- ATOMIC_REQUESTS activé
- Connection pooling (CONN_MAX_AGE: 600s)

**Authentification**: JWT avec rotation
- Access token: 5 minutes
- Refresh token: 24 heures
- Algorithme: HS256 (simplifié) ou RS256 pour QR codes

**Pagination**: 20 résultats par défaut

**CORS**: Configuré strictement pour le frontend

**Cache**: Redis (sessions, rate limiting, tokens)

### Tâches Celery

**Celery Worker** (asynchrone):
```python
# Tâches principales
- send_email()          # Envoi emails
- send_sms()            # Envoi SMS  
- generate_report()     # Export données
- sync_payment_status() # Sync paiements
```

**Celery Beat** (planifiées):
```python
- Envoyer rappels voyage (X heures avant départ)
- Nettoyer notifications anciennes (> 30 jours)
- Générer rapports quotidiens/mensuels
- Mettre à jour statuts voyages expirés
- Archiver anciennes activités
```

### Permissions et contrôle d'accès

**Système de rôles**:
```
VOYAGEUR (Voyageur)
├── Peut réserver tickets
├── Voir ses tickets
├── Annuler ses tickets
├── Créer réclamations
└── Voir notifications

COMPAGNIE (Administrateur compagnie)
├── Créer/modifier voyages
├── Gérer flotte véhicules
├── Voir statistiques
├── Gérer embarqueurs
└── Voir tickets vendus

EMBARQUEUR (Agent embarquement)
├── Scanner QR codes
├── Voir voyages du jour
├── Valider tickets
└── Sync mode offline

ADMIN (Administrateur système)
├── Accès complet
├── Approuver compagnies
├── Voir tous les logs
├── Gérer utilisateurs
└── Configurer paramètres
```

**Classes de permissions**:
- `IsAuthenticated` - Doit être connecté
- `IsVoyageur` - Doit avoir le rôle voyageur
- `CanManageTicket` - Voyageur (ses tickets) ou admin
- `IsCompagnie` - Compagnie de transport
- `IsEmbarqueur` - Agent embarquement
- `IsAdmin` - Administrateur

---

## 🎨 FRONTEND - NEXT.JS

### Stack technologique

**Framework**: Next.js 16 (App Router)
```json
{
  "react": "19.2.0",
  "typescript": "^5",
  "tailwindcss": "^4",
  "framer-motion": "^12.23.24",
  "react-hook-form": "^7.66.0",
  "zod": "^4.1.12",
  "zustand": "^5.0.8",
  "@tanstack/react-query": "^5.90.9",
  "axios": "^1.13.2",
  "lucide-react": "^0.553.0",
  "@radix-ui/react-*": "Latest"
}
```

### Structure des dossiers

```
frontend/
├── app/                        # App Router de Next.js
│   ├── layout.tsx             # Layout root
│   ├── page.tsx               # Page d'accueil
│   └── globals.css            # Styles globaux
│
├── src/
│   ├── components/            # Composants réutilisables
│   │   ├── auth/             # Authentification
│   │   ├── boarding/         # Embarquement
│   │   ├── common/           # Génériques (Button, Card, etc)
│   │   ├── layout/           # Header, Footer, Sidebar
│   │   ├── payments/         # Paiements
│   │   ├── tickets/          # Tickets/Réservations
│   │   ├── trips/            # Voyages
│   │   └── ui/               # Radix UI wrappers
│   │
│   ├── features/              # Feature-specific logic
│   │   ├── auth/             # Auth store & hooks
│   │   ├── payments/         # Payment logic
│   │   ├── tickets/          # Ticket management
│   │   └── trips/            # Trip search & filtering
│   │
│   ├── hooks/                 # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   └── ...
│   │
│   ├── lib/                   # Utilitaires
│   │   ├── api.ts            # Configuration Axios
│   │   ├── validators.ts      # Validations Zod
│   │   └── utils.ts           # Helpers généraux
│   │
│   ├── middleware.ts          # Auth middleware Next.js
│   ├── providers/             # Context providers
│   ├── services/              # API service calls
│   ├── store/                 # Zustand stores
│   ├── types/                 # Types TypeScript
│   └── utils/                 # Fonctions utilitaires
│
├── public/
│   ├── fonts/
│   ├── icons/
│   └── images/
│
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts
└── eslint.config.mjs
```

### Pages principales (App Router)

```
/                          # Accueil
/auth/login                # Connexion
/auth/register             # Inscription
/auth/forgot-password      # Récupération mot de passe

/dashboard                 # Tableau de bord (selon rôle)
/dashboard/tickets         # Mes tickets
/dashboard/trips           # Mes voyages (compagnie)
/dashboard/vehicles        # Mes véhicules
/dashboard/statistics      # Statistiques
/dashboard/settings        # Paramètres compte

/trips                     # Recherche voyages
/trips/{id}               # Détail voyage
/tickets/book/{tripId}    # Réservation

/boarding                  # Scanner QR (embarqueur)

/payments                  # Historique paiements
/payments/receipt/{id}    # Reçu paiement

/claims                    # Mes réclamations
/claims/new               # Créer réclamation

/admin                     # Admin dashboard
/admin/companies           # Gestion compagnies
/admin/users              # Gestion utilisateurs
/admin/logs               # Audit trail
/admin/settings           # Paramètres plateforme
```

### État global (Zustand)

```typescript
// stores/auth.store.ts
- user: User | null
- token: string | null
- login(email, password)
- logout()
- setUser(user)

// stores/search.store.ts
- departure: City | null
- arrival: City | null
- departureDate: Date | null
- setSearch(departure, arrival, date)

// stores/booking.store.ts
- selectedTrip: Trip | null
- selectedSeats: string[]
- passengerInfo: PassengerInfo | null
- setTrip(trip)
- addSeat(seatNumber)
- removeSeat(seatNumber)
- setPassengerInfo(info)

// stores/notifications.store.ts
- notifications: Notification[]
- addNotification(notif)
- removeNotification(id)
```

### Requêtes API (React Query)

```typescript
// Exemples d'utilisation
useQuery({
  queryKey: ['trips', filters],
  queryFn: () => api.get('/trips', { params: filters })
})

useMutation({
  mutationFn: (data) => api.post('/tickets', data),
  onSuccess: () => queryClient.invalidateQueries(['tickets'])
})
```

### Validation (Zod)

```typescript
// Schemas principaux
LoginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

TripSearchSchema = z.object({
  departure_city_id: z.string().uuid(),
  arrival_city_id: z.string().uuid(),
  departure_date: z.date()
})

BookingSchema = z.object({
  trip_id: z.string().uuid(),
  seat_numbers: z.array(z.string()),
  passenger_first_name: z.string(),
  passenger_last_name: z.string(),
  passenger_phone: z.string().phone(),
  payment_method: z.enum(['orange_money', 'mtn_money', ...])
})
```

### Composants UI (Radix UI + TailwindCSS)

```tsx
// Composants principaux
<Button />                 # Bouton
<Card />                   # Carte
<Dialog />                 # Modal
<DropdownMenu />           # Menu déroulant
<Input />                  # Champ texte
<Separator />              # Séparateur
<Badge />                  # Badge
<Tabs />                   # Onglets
<Pagination />             # Pagination
```

### Responsive Design

- **Mobile**: < 640px (prioritaire)
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

TailwindCSS utility-first: `md:`, `lg:` breakpoints

---

## 💾 BASE DE DONNÉES

### Schéma de données (PostgreSQL)

```sql
-- Utilisateurs
Table: users_user
  - id (UUID)
  - email (unique)
  - phone_number (unique)
  - role (voyageur|compagnie|embarqueur|admin)
  - is_active, is_verified
  - avatar_url
  - company_id (FK → companies)

-- Compagnies
Table: companies_company
  - id (UUID)
  - name (unique)
  - registration_number (unique)
  - status (pending|approved|rejected|suspended)
  - commission_rate (décimal)
  - total_trips, total_tickets_sold, total_revenue
  - logo_url, document_url
  - validated_at

-- Véhicules
Table: fleet_vehicle
  - id (UUID)
  - company_id (FK)
  - registration_number (unique)
  - vehicle_type, brand, model, year
  - total_seats, seat_configuration (JSON)
  - status (active|maintenance|inactive)
  - amenities (JSON)

-- Villes
Table: trips_city
  - id (UUID)
  - name (unique)
  - country, latitude, longitude
  - is_active

-- Voyages
Table: trips_trip
  - id (UUID)
  - company_id (FK)
  - vehicle_id (FK)
  - departure_city_id (FK), arrival_city_id (FK)
  - departure_datetime, arrival_datetime
  - base_price, platform_fee
  - status (scheduled|boarding|in_progress|completed|cancelled)
  - available_seats
  - is_cancellable

-- Tickets
Table: tickets_ticket
  - id (UUID)
  - ticket_number (unique)
  - trip_id (FK)
  - passenger_id (FK)
  - seat_number (unique par trip)
  - price, platform_fee, total_amount
  - status (pending|confirmed|cancelled|used|expired|refunded)
  - is_paid
  - qr_code (JWT), qr_code_image
  - boarding_time, boarded_by_id (FK)
  - cancelled_at, refund_amount

-- Paiements
Table: payments_payment
  - id (UUID)
  - transaction_id (unique)
  - user_id (FK)
  - trip_id (FK)
  - company_id (FK)
  - amount, payment_fee, amount_paid
  - payment_method (orange_money|mtn_money|...)
  - status (pending|processing|success|failed|cancelled|refunded)
  - metadata (JSON)

-- Embarquements
Table: boarding_boardingpass
  - id (UUID)
  - ticket_id (FK)
  - trip_id (FK)
  - boarding_agent_id (FK)
  - scan_status (valid|invalid|already_used|expired|wrong_trip)
  - scanned_at
  - latitude, longitude
  - device_info (JSON)

-- Notifications
Table: notifications_notification
  - id (UUID)
  - user_id (FK)
  - notification_type (email|sms|in_app|push)
  - category (booking_confirmation|payment_success|...)
  - status (pending|sent|failed|read)
  - subject, content
  - metadata (JSON)

-- Logs d'activité (Immuables)
Table: logs_activitylog
  - id (BigAutoField)
  - user_id (FK)
  - action (create|update|delete|login|logout|...)
  - resource_type (ticket|payment|trip|...)
  - resource_id
  - old_values, new_values (JSON)
  - ip_address
  - created_at
  - Indices: (user_id, created_at), (resource_type, resource_id)

-- Réclamations
Table: claims_claim
  - id (UUID)
  - ticket_id (FK)
  - claimant_id (FK)
  - claim_type (lost_item|missed_trip|accident|other)
  - priority (low|medium|high|critical)
  - status (open|in_progress|resolved|closed)
  - description, resolution
  - created_at, resolved_at

-- FAQ
Table: core_faq
  - id (UUID)
  - question, answer
  - category, order
  - is_active

-- Bannières
Table: core_banner
  - id (UUID)
  - title, content, image_url
  - link_url
  - is_active, start_date, end_date

-- Paramètres plateforme
Table: core_platformsettings
  - id = 1 (singleton)
  - max_tickets_per_booking
  - allow_overbooking, overbooking_percentage
  - maintenance_mode, maintenance_message
  - qr_code_expiration_hours
  - payment_timeout_minutes
  - min_ticket_price, max_ticket_price
  - support_email, support_phone
```

### Indices importants

```sql
-- Recherche rapide des voyages
CREATE INDEX idx_trips_departure_datetime ON trips_trip(departure_datetime);
CREATE INDEX idx_trips_company_status ON trips_trip(company_id, status);
CREATE INDEX idx_trips_cities ON trips_trip(departure_city_id, arrival_city_id);

-- Recherche des tickets
CREATE INDEX idx_tickets_trip_seat ON tickets_ticket(trip_id, seat_number);
CREATE INDEX idx_tickets_status_paid ON tickets_ticket(status, is_paid);
CREATE INDEX idx_tickets_passenger ON tickets_ticket(passenger_id, status);

-- Recherche des paiements
CREATE INDEX idx_payments_user_status ON payments_payment(user_id, status);
CREATE INDEX idx_payments_transaction ON payments_payment(transaction_id);

-- Logs d'audit
CREATE INDEX idx_logs_resource ON logs_activitylog(resource_type, resource_id);
CREATE INDEX idx_logs_user_date ON logs_activitylog(user_id, created_at);
```

### Relations clés

```
User → Compagnie (many-to-one) [embarqueurs + compagnies]
   ↓
Trip ← Company (one-to-many)
Trip ← Vehicle (foreign key)
   ↓
Ticket → Trip (foreign key)
Ticket → User (passenger)
Ticket → Payment (one-to-one)
   ↓
BoardingPass → Ticket (foreign key)
   ↓
Notification → User (foreign key)
ActivityLog → User (foreign key)
Claim → Ticket (foreign key)
```

---

## 🔐 SÉCURITÉ

### Authentification & Autorisation

**JWT (JSON Web Tokens)**
```
Access Token (5 min):
- Utilisé pour chaque requête API
- Contient: user_id, email, role, permissions
- Signé avec SECRET_KEY (HS256)

Refresh Token (24h):
- Stocké en DB ou cache Redis
- Peut être révoqué immédiatement
- Permet obtenir nouveau access token

QR Code Token (24h après départ):
- Signé avec clé RSA (RS256) - public/private keys
- Format: JWT RS256 contenant ticket_id + validation
- Vérifié par l'embarqueur
- Impossible de forger sans clé privée
```

**Stockage des clés RSA**:
```
keys/
├── private_key.pem    # Génération QR codes (SECRET)
└── public_key.pem     # Validation QR codes
```

### Rate Limiting

```python
# django-ratelimit
@ratelimit(key='ip', rate='100/h', method='GET')
def api_view(request):
    # Max 100 requêtes par heure par IP
```

Configuration par endpoint:
- Login: 5 tentatives/30 min
- API générale: 100 requêtes/heure
- Paiement: 10 requêtes/heure

### Protection CORS

```python
CORS_ALLOWED_ORIGINS = [
    'https://ticketzen.com',
    'https://app.ticketzen.com',
    'http://localhost:3000',  # Dev
]
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
CORS_ALLOW_HEADERS = ['Authorization', 'Content-Type']
```

### Sécurité des données

- ✅ Passwords: PBKDF2 (min 8 caractères)
- ✅ Données sensibles: Chiffrage PII si nécessaire
- ✅ Logs immuables: Toutes actions critiques tracées
- ✅ HTTPS obligatoire en production
- ✅ CSRF protection sur formulaires

### Validation des entrées

```python
# Utilisation de Pydantic et validateurs Django
from pydantic import BaseModel, validator, EmailStr

class BookingRequest(BaseModel):
    trip_id: UUID
    seat_numbers: List[str]
    passenger_first_name: str = Field(..., min_length=2, max_length=150)
    passenger_email: EmailStr
    payment_method: Literal['orange_money', 'mtn_money', ...]
    
    @validator('seat_numbers')
    def validate_seats(cls, v):
        if len(v) == 0 or len(v) > 10:
            raise ValueError('Entre 1 et 10 places par réservation')
        return v
```

### Permissions granulaires

```python
# Exemple: Vu que le voyageur ne peut voir que SES tickets
class CanManageTicket(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Admin peut tout voir
        if request.user.role == 'admin':
            return True
        
        # Voyageur voir ses tickets
        if request.user.role == 'voyageur':
            return obj.passenger == request.user
        
        # Compagnie voir ses tickets
        if request.user.role == 'compagnie':
            return obj.trip.company == request.user.company
```

---

## 🚀 DÉPLOIEMENT

### Docker & Docker Compose

**Configuration**:
```yaml
Services:
- db: PostgreSQL 16 (port 5432)
- redis: Redis 7 (port 6379)
- backend: Django Gunicorn (port 8000)
- celery_worker: Celery worker
- celery_beat: Celery beat (tâches planifiées)
```

**Volumes**:
- `postgres_data`: Base de données persistent
- `redis_data`: Cache persistent
- `static_volume`: Fichiers statiques collectés
- `media_volume`: Uploads utilisateurs

**Démarrage**:
```bash
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

### Variables d'environnement

**`.env` (Développement)**:
```env
# Django
DJANGO_ENV=development
DEBUG=True
SECRET_KEY=dev-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données
DB_ENGINE=postgresql
DB_NAME=ticketzen_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_LIFETIME=300
JWT_REFRESH_TOKEN_LIFETIME=86400

# CinetPay (Mock en développement)
CINETPAY_MODE=DEMO
CINETPAY_API_KEY=demo-key
CINETPAY_SITE_ID=demo-site
CINETPAY_SECRET_KEY=demo-secret

# Emails (optionnel)
EMAIL_BACKEND=console
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Frontend
FRONTEND_URL=http://localhost:3000
```

**`.env` (Production)**:
```env
# Django
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=very-secure-random-key
ALLOWED_HOSTS=api.ticketzen.com

# Base de données (RDS, Digital Ocean, etc)
DB_HOST=prod-db-host
DB_PASSWORD=secure-password

# Redis (Managed service)
REDIS_HOST=prod-redis-host

# CinetPay (Real credentials)
CINETPAY_MODE=PRODUCTION
CINETPAY_API_KEY=real-api-key
CINETPAY_SITE_ID=real-site-id

# SSL/TLS
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Logs
LOGGING_LEVEL=INFO
SENTRY_DSN=your-sentry-dsn

# Frontend
FRONTEND_URL=https://ticketzen.com
```

### CI/CD Workflow

```yaml
# GitHub Actions (.github/workflows/deploy.yml)
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build & Push Docker image
      - name: Deploy to production
      - name: Run migrations
      - name: Collect static files
```

---

## 💡 POINTS CLÉS ET RECOMMANDATIONS

### ✅ Points forts du projet

1. **Architecture bien structurée**
   - Séparation claire des responsabilités par apps Django
   - Frontend/Backend complètement découplés
   - API RESTful cohérente
   - ✅ Configuration Django de QUALITÉ HAUTE

2. **Sécurité EXCELLENTE**
   - ✅ JWT avec rotation des tokens (ACCESS: 1h, REFRESH: 7j)
   - ✅ QR codes signés (RS256) difficiles à forger
   - ✅ Rate limiting configuré (100/h user, 10/h payment)
   - ✅ CORS strictement configuré
   - ✅ Logs immuables pour audit trail
   - ✅ CSRF protection activée
   - ✅ Middleware de sécurité (XSS, Clickjacking)
   - ✅ Validation des passwords (min 8 caractères)

3. **Scalabilité**
   - PostgreSQL pour données persistantes
   - Redis pour caching et sessions (avec compresseurs)
   - Celery pour tâches asynchrones (25-30 min timeout)
   - Docker pour déploiement facile
   - Connection pooling (600s)

4. **Backend Django SOLIDE**
   - ✅ Authentification personnalisée (4 rôles)
   - ✅ Logs détaillés (Rotating file handler: 10 MB × 10)
   - ✅ Documentation API (Swagger/OpenAPI drf-spectacular)
   - ✅ Email/SMS notifications
   - ✅ Exception handling personnalisé

5. **Internationalisation**
   - Tout traduit en français
   - Timezone Côte d'Ivoire
   - Support de plusieurs monnaies locales

### ⚠️ PROBLÈMES IDENTIFIÉS - ACTIONS URGENTES REQUISES

#### Backend

1. **Tests unitaires et d'intégration**
   - Coverage: pytest, pytest-django, pytest-cov
   - Actuellement: pytest déclaré dans requirements mais pas de tests visibles
   - Ajouter: Tests pour chaque ViewSet, Serializer, Model

2. **Documentation API**
   - Excellent: drf-spectacular déjà intégré (Swagger)
   - Amélioration: Ajouter plus de descriptions dans docstrings
   - Exemples de requêtes/réponses

3. **Monitoring et observabilité**
   - Considérer: Sentry pour bug tracking
   - Prometheus + Grafana pour métriques
   - ELK stack pour logs centralisés

4. **Optimisation des requêtes**
   - Audit: N+1 queries (select_related, prefetch_related)
   - Cache: Redis pour requêtes fréquentes
   - Pagination: Par défaut 20, adapté aux besoins

#### Frontend

1. **Tests**
   - Setup: Cypress et Playwright déclarés
   - À faire: E2E tests pour flows critiques
   - Unit tests pour composants complexes

2. **Performance**
   - Optimiser: Images avec next/image
   - Code splitting: Automatique avec Next.js
   - Lazy loading: Pour composants lourds

3. **Accessibilité**
   - WCAG 2.1 Level AA
   - Tests: axe-core, manual testing
   - ARIA labels sur composants

4. **PWA (Progressive Web App)**
   - Service workers
   - Offline support
   - Installation sur home screen

### 🔄 Flux critiques à tester

1. **Authentification**
   ```
   Register → Verify Email → Login → Get Token → Refresh Token → Logout
   ```

2. **Réservation de ticket**
   ```
   Search Trips → Select Trip → Choose Seats → Enter Passenger Info → 
   → Init Payment → CinetPay Redirect → Payment Callback → 
   → Generate QR Code → Confirmation Email
   ```

3. **Embarquement**
   ```
   Scan QR Code → Validate (offline) → Mark as Used → Sync → 
   → Update Trip Status → Send Notification
   ```

4. **Remboursement**
   ```
   Cancel Ticket → Process Refund → Update Payment Status → 
   → Send Notification → Return Money
   ```

### 📊 Métriques à surveiller

```
Performance:
- Response time API: < 200ms (p95)
- Page load: < 3s (3G)
- Lighthouse score: > 90

Fiabilité:
- Uptime: > 99.5%
- Error rate: < 0.1%
- Success rate paiements: > 95%

Utilisation:
- DAU (Daily Active Users)
- Monthly revenue
- Tickets vendus/mois
- Taux de satisfaction clients
```

### 🛠️ Stack de développement recommandé

**Backend**:
```bash
# Linting & Formatting
pip install flake8 black isort
black .
isort .
flake8

# Type checking
pip install mypy
mypy apps/

# Sécurité
pip install bandit safety
bandit -r apps/
safety check
```

**Frontend**:
```bash
# Linting
npm run lint

# Type checking
tsc --noEmit

# Formatting
npm run format

# Tests
npm run test
npm run test:e2e
```

### 📚 Documentation à prioriser

1. API Documentation (Swagger): ✅ Déjà en place
2. Architecture Decision Records (ADR)
3. Database schema documentation
4. Deployment guide
5. Troubleshooting guide
6. Contributing guidelines

---

## 📞 CONTACTS & SUPPORT

- **Propriétaire**: soulemaneyeo99
- **Repository**: github.com/soulemaneyeo99/ticket_zen
- **Support**: support@ticketzen.com
- **Documentation**: https://docs.ticketzen.com

---

## 📈 Roadmap suggérée

### Phase 1 (Actuellement)
- ✅ API complète
- ✅ Frontend basique
- ✅ Système paiement

### Phase 2 (Court terme - Q1 2026)
- [ ] Tests unitaires (>80% coverage)
- [ ] Mobile app (React Native)
- [ ] Analytics dashboard
- [ ] Multi-langue (FR/EN)

### Phase 3 (Moyen terme - Q2-Q3 2026)
- [ ] PWA pour offline support
- [ ] Système de loyalty/points
- [ ] Intégration API tiers (APIs de bus, etc)
- [ ] A/B testing

### Phase 4 (Long terme - Q4 2026)
- [ ] AI pour recommandations de trajets
- [ ] Marketplace de services
- [ ] Blockchain pour tickets immuables
- [ ] Expansion régionale

---

**Document généré**: 26 novembre 2025  
**Version**: 1.0  
**Dernière mise à jour**: 26/11/2025

