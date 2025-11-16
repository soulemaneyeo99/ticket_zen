# 💳 Système de Paiement - Ticket Zen

## Overview

Le système de paiement de Ticket Zen est conçu pour être flexible et extensible. Il utilise **CinetPay** comme provider de paiement avec un mode **mocké** pour le développement.

## Architecture

### Structure
```
apps/payments/
├── models.py              # Modèle Payment
├── serializers.py         # Serializers DRF
├── views.py              # ViewSets pour les APIs
├── services.py           # Logique métier des paiements
├── providers/
│   ├── base.py          # Classe abstraite BasePaymentProvider
│   └── cinetpay.py      # Implémentation CinetPay
└── management/
    └── commands/
        └── test_payment_flow.py  # Commande pour tester les paiements
```

## Modes de fonctionnement

### 1. Mode Mocké (Développement)

Par défaut, le système fonctionne en mode mocké pour faciliter le développement :
```python
# Dans cinetpay.py
self.is_mocked = True  # Activer le mode mocké
```

**Avantages :**
- Pas besoin de credentials CinetPay réels
- Tests rapides sans API externe
- Contrôle total sur les scénarios (succès, échec, remboursement)

### 2. Mode Production

Pour activer le mode production :

1. Configurer les credentials dans `.env` :
```env
CINETPAY_API_KEY=your_real_api_key
CINETPAY_SITE_ID=your_site_id
CINETPAY_SECRET_KEY=your_secret_key
CINETPAY_MODE=PRODUCTION
CINETPAY_NOTIFY_URL=https://yourdomain.com/api/v1/payments/webhook/
```

2. Désactiver le mode mocké :
```python
self.is_mocked = False
```

## Flow de paiement

### 1. Initialisation
```python
POST /api/v1/payments/initialize/
{
    "ticket_id": "uuid",
    "payment_method": "orange_money",
    "phone_number": "+225XXXXXXXX",
    "return_url": "https://app.com/payment-success"
}
```

**Réponse :**
```json
{
    "message": "Paiement initialisé avec succès",
    "payment": {...},
    "payment_url": "https://payment.provider.com/pay/..."
}
```

### 2. Redirection utilisateur

L'utilisateur est redirigé vers `payment_url` pour effectuer le paiement.

### 3. Webhook CinetPay

CinetPay envoie une notification à `notify_url` :
```python
POST /api/v1/payments/webhook/
{
    "cpm_trans_id": "TZ...",
    "cpm_trans_status": "00",  # 00 = succès
    "cpm_amount": "5000",
    ...
}
```

### 4. Traitement

Le système :
- Valide la signature du webhook
- Met à jour le statut du paiement
- Confirme le ticket
- Génère le QR code
- Envoie les notifications

## Méthodes de paiement supportées
```python
PAYMENT_METHOD_CHOICES = [
    ('orange_money', 'Orange Money'),
    ('mtn_money', 'MTN Money'),
    ('moov_money', 'Moov Money'),
    ('wave', 'Wave'),
    ('visa', 'Visa'),
    ('mastercard', 'Mastercard'),
]
```

## Tester le système

### Via commande Django
```bash
# Test paiement réussi
python manage.py test_payment_flow --scenario=success

# Test paiement échoué
python manage.py test_payment_flow --scenario=failed

# Test remboursement
python manage.py test_payment_flow --scenario=refund
```

### Via code Python
```python
from apps.payments.services import MockPaymentTestHelper

helper = MockPaymentTestHelper()

# Simuler un paiement
result = helper.simulate_payment_flow(
    ticket=my_ticket,
    payment_method='orange_money',
    phone_number='+225XXXXXXXX'
)

if result['success']:
    print(f"✅ Paiement réussi: {result['payment'].transaction_id}")
```

### Via API directement
```bash
# 1. Créer un paiement
curl -X POST http://localhost:8000/api/v1/payments/initialize/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "your-ticket-uuid",
    "payment_method": "orange_money",
    "phone_number": "+225XXXXXXXX"
  }'

# 2. Simuler le webhook (mode mocké)
curl -X POST http://localhost:8000/api/v1/payments/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "cpm_trans_id": "YOUR_TRANSACTION_ID",
    "cpm_trans_status": "00",
    "cpm_amount": "5000",
    "cpm_site_id": "test"
  }'
```

## Sécurité

### Validation Webhook
```python
def validate_webhook_signature(self, webhook_data, signature):
    signature_string = (
        f"{webhook_data.get('cpm_site_id')}"
        f"{webhook_data.get('cpm_trans_id')}"
        f"{webhook_data.get('cpm_trans_status')}"
        f"{webhook_data.get('cpm_amount')}"
        f"{self.secret_key}"
    )
    calculated_signature = hashlib.sha256(signature_string.encode()).hexdigest()
    return calculated_signature == signature
```

### Vérifications

- ✅ Signature webhook validée
- ✅ Site ID vérifié
- ✅ Montant cohérent
- ✅ Transaction unique (pas de replay)
- ✅ Logging complet

## Remboursements
```python
POST /api/v1/payments/{payment_id}/refund/
{
    "refund_amount": 5000,
    "refund_reason": "Voyage annulé"
}
```

**Processus :**
1. Vérification des permissions (admin uniquement)
2. Validation du paiement
3. Appel API remboursement
4. Mise à jour statut paiement et ticket
5. Libération du siège
6. Notification client

## Statistiques
```python
GET /api/v1/payments/?company_id=X&date_from=2025-01-01

# Retourne
{
    "total_payments": 150,
    "total_amount": 750000,
    "successful_payments": 145,
    "failed_payments": 5,
    "by_payment_method": {...}
}
```

## Logs

Toutes les transactions sont loguées dans `ActivityLog` :
- Initialisation paiement
- Succès/Échec
- Remboursements
- Changements de statut

## Migration vers production

1. Obtenir credentials CinetPay réels
2. Configurer `.env` avec vraies valeurs
3. Désactiver `is_mocked = False`
4. Configurer webhook URL publique
5. Tester avec petits montants
6. Activer en production

## Support

Pour questions sur l'intégration CinetPay :
- Documentation : https://docs.cinetpay.com
- Support : support@cinetpay.com