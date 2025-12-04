# Guide de Test - Ticket Zen Frontend

## 🚀 Serveurs en cours d'exécution

- ✅ **Backend**: http://localhost:8000
- ✅ **Frontend**: http://localhost:3000

## 📋 Scénarios de Test

### 1. Page d'Accueil (Landing Page)
**URL**: http://localhost:3000

**À vérifier**:
- [ ] Le titre "Voyagez en toute sérénité avec Ticket Zen" s'affiche
- [ ] Le formulaire de recherche contient 3 champs (Départ, Arrivée, Date)
- [ ] Les 3 cartes de fonctionnalités s'affichent (Rapide, Sécurisé, Numérique)
- [ ] Le footer affiche "© 2024 Ticket Zen"

### 2. Inscription
**URL**: http://localhost:3000/register

**À tester**:
1. Remplir le formulaire avec:
   - Prénom: Test
   - Nom: User
   - Email: test@example.com
   - Téléphone: +2250123456789
   - Rôle: Voyageur
   - Mot de passe: Test1234!
   - Confirmation: Test1234!

2. Cliquer sur "S'inscrire"

**Résultat attendu**:
- Redirection vers `/client` (dashboard voyageur)
- Message de succès affiché

### 3. Connexion
**URL**: http://localhost:3000/login

**À tester**:
1. Se connecter avec:
   - Email: test@example.com
   - Mot de passe: Test1234!

2. Cliquer sur "Se connecter"

**Résultat attendu**:
- Redirection selon le rôle:
  - Voyageur → `/client`
  - Compagnie → `/company`
  - Embarqueur → `/agent`
  - Admin → `/admin`

### 4. Dashboard Voyageur
**URL**: http://localhost:3000/client

**À vérifier**:
- [ ] Affichage du nom de l'utilisateur
- [ ] Section "Mes Réservations"
- [ ] Bouton "Se déconnecter" fonctionne

### 5. Espace Compagnie
**URL**: http://localhost:3000/company

**À tester**:

#### 5.1 Dashboard
- [ ] Affichage des statistiques (Flotte, Voyages, Revenus)
- [ ] Menu latéral avec navigation

#### 5.2 Gestion de la Flotte
**URL**: http://localhost:3000/company/fleet

1. Cliquer sur "Ajouter un véhicule"
2. Remplir le formulaire:
   - Immatriculation: AB-123-CD
   - Type: Bus
   - Marque: Mercedes
   - Modèle: Sprinter
   - Année: 2023
   - Capacité: 50
   - Équipements: Climatisation, WiFi

3. Cliquer sur "Ajouter le véhicule"

**Résultat attendu**:
- Véhicule ajouté à la liste
- Redirection vers la liste des véhicules

#### 5.3 Gestion des Voyages
**URL**: http://localhost:3000/company/trips

1. Cliquer sur "Créer un voyage"
2. Remplir le formulaire:
   - Ville de départ: Abidjan
   - Ville d'arrivée: Yamoussoukro
   - Date/Heure départ: (date future)
   - Date/Heure arrivée: (date future + 3h)
   - Véhicule: (sélectionner dans la liste)
   - Prix: 5000

3. Cliquer sur "Programmer le voyage"

**Résultat attendu**:
- Voyage créé et visible dans la liste

### 6. Recherche et Réservation (Voyageur)

#### 6.1 Recherche de Voyages
**URL**: http://localhost:3000

1. Remplir le formulaire de recherche:
   - Départ: Abidjan
   - Arrivée: Yamoussoukro
   - Date: (date du voyage créé)

2. Cliquer sur "Rechercher"

**Résultat attendu**:
- Redirection vers `/trips/search`
- Affichage des voyages disponibles

#### 6.2 Réservation
1. Cliquer sur "Réserver" sur un voyage
2. Remplir le formulaire passager:
   - Prénom: Jean
   - Nom: Kouassi
   - Téléphone: +2250123456789
   - Email: jean@example.com
   - Moyen de paiement: Mobile Money

3. Cliquer sur "Payer"

**Résultat attendu**:
- Redirection vers la page de paiement (ou simulation)
- Création du ticket

### 7. Espace Embarqueur
**URL**: http://localhost:3000/agent/scan

**À tester**:
1. Entrer un code de ticket dans le champ
2. Cliquer sur "Vérifier"

**Résultat attendu**:
- Affichage du statut du ticket (Valide/Invalide/Déjà scanné)
- Détails du passager et du voyage

### 8. Protection des Routes

**À vérifier**:
1. Se déconnecter
2. Essayer d'accéder à `/company`

**Résultat attendu**:
- Redirection vers `/login`
- Paramètre `from` dans l'URL

### 9. Thème Clair/Sombre

**À vérifier**:
- [ ] Le thème s'adapte aux préférences du système
- [ ] Les couleurs sont cohérentes en mode sombre

## 🐛 Points d'Attention

### Limitations Actuelles
1. **Backend requis**: Le backend Django doit être en cours d'exécution
2. **Données de test**: Créer des données via l'admin Django si nécessaire
3. **Paiement**: L'intégration CinetPay nécessite une configuration supplémentaire

### Erreurs Possibles
- **CORS**: Si erreur CORS, vérifier la configuration backend
- **404 API**: Vérifier que le backend est sur le port 8000
- **Refresh Token**: Si déconnexion automatique, vérifier les cookies

## ✅ Checklist de Validation

### Fonctionnalités Core
- [ ] Inscription fonctionne
- [ ] Connexion fonctionne
- [ ] Déconnexion fonctionne
- [ ] Protection des routes fonctionne

### Compagnie
- [ ] Ajout de véhicule fonctionne
- [ ] Création de voyage fonctionne
- [ ] Liste des voyages s'affiche

### Voyageur
- [ ] Recherche de voyages fonctionne
- [ ] Affichage des résultats fonctionne
- [ ] Formulaire de réservation s'affiche

### UI/UX
- [ ] Design responsive (mobile/desktop)
- [ ] Toasts de notification s'affichent
- [ ] Formulaires valident correctement
- [ ] Navigation fluide entre les pages

## 📝 Notes de Test

**Environnement**:
- Node.js: v18+
- Next.js: 16.0.3
- Backend: Django 5.1.3

**Commandes Utiles**:
```bash
# Redémarrer le frontend
cd /home/dev/projects/ticket_zen/frontend
npm run dev

# Vérifier les logs backend
cd /home/dev/projects/ticket_zen/backend
tail -f logs/debug.log

# Build de production
npm run build
```

## 🎯 Résultats Attendus

Après tous les tests, l'application devrait:
1. ✅ Compiler sans erreurs
2. ✅ Afficher toutes les pages correctement
3. ✅ Gérer l'authentification de manière sécurisée
4. ✅ Permettre la création et recherche de voyages
5. ✅ Être responsive et accessible
