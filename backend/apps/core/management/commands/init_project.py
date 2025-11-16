"""
Commande Django pour initialiser le projet Ticket Zen
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.utils import timezone
import os


class Command(BaseCommand):
    help = 'Initialiser le projet Ticket Zen (clés RSA, données de base, etc.)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Ignorer les migrations',
        )
        parser.add_argument(
            '--with-demo-data',
            action='store_true',
            help='Créer des données de démonstration',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('🎫 INITIALISATION DU PROJET TICKET ZEN'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
        
        # 1. Vérifier la connexion à la base de données
        self.stdout.write('📊 Vérification de la connexion à la base de données...')
        try:
            connection.ensure_connection()
            self.stdout.write(self.style.SUCCESS('   ✅ Connexion réussie\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erreur de connexion: {e}\n'))
            return
        
        # 2. Appliquer les migrations
        if not options['skip_migrations']:
            self.stdout.write('🔄 Application des migrations...')
            try:
                call_command('migrate', '--noinput')
                self.stdout.write(self.style.SUCCESS('   ✅ Migrations appliquées\n'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Erreur migrations: {e}\n'))
                return
        
        # 3. Générer les clés RSA pour QR codes
        self.stdout.write('🔐 Génération des clés RSA pour QR codes...')
        try:
            from utils.qr_generator import ensure_rsa_keys_exist
            keys = ensure_rsa_keys_exist()
            self.stdout.write(self.style.SUCCESS('   ✅ Clés RSA générées'))
            self.stdout.write(f'      - Clé privée: {keys["private_key_path"]}')
            self.stdout.write(f'      - Clé publique: {keys["public_key_path"]}\n')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erreur génération clés: {e}\n'))
        
        # 4. Créer les paramètres de la plateforme
        self.stdout.write('⚙️  Initialisation des paramètres de la plateforme...')
        try:
            from apps.core.models import PlatformSettings
            settings, created = PlatformSettings.objects.get_or_create(pk=1)
            if created:
                self.stdout.write(self.style.SUCCESS('   ✅ Paramètres créés avec valeurs par défaut\n'))
            else:
                self.stdout.write(self.style.SUCCESS('   ✅ Paramètres déjà existants\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erreur paramètres: {e}\n'))
        
        # 5. Créer les villes de base
        self.stdout.write('🏙️  Création des villes de base...')
        try:
            cities_created = self._create_base_cities()
            self.stdout.write(self.style.SUCCESS(f'   ✅ {cities_created} villes créées\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erreur villes: {e}\n'))
        
        # 6. Créer des FAQs de base
        self.stdout.write('❓ Création des FAQs de base...')
        try:
            faqs_created = self._create_base_faqs()
            self.stdout.write(self.style.SUCCESS(f'   ✅ {faqs_created} FAQs créées\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erreur FAQs: {e}\n'))
        
        # 7. Créer des données de démonstration si demandé
        if options['with_demo_data']:
            self.stdout.write('🎭 Création des données de démonstration...')
            try:
                self._create_demo_data()
                self.stdout.write(self.style.SUCCESS('   ✅ Données de démo créées\n'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Erreur données démo: {e}\n'))
        
        # 8. Créer les dossiers nécessaires
        self.stdout.write('📁 Création des dossiers nécessaires...')
        try:
            self._create_directories()
            self.stdout.write(self.style.SUCCESS('   ✅ Dossiers créés\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erreur dossiers: {e}\n'))
        
        # 9. Résumé final
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('🎉 INITIALISATION TERMINÉE AVEC SUCCÈS !'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
        
        self.stdout.write('📝 Prochaines étapes:')
        self.stdout.write('   1. Créer un superuser: python manage.py createsuperuser')
        self.stdout.write('   2. Lancer le serveur: python manage.py runserver')
        self.stdout.write('   3. Accéder à l\'API: http://localhost:8000/api/v1/')
        self.stdout.write('   4. Documentation: http://localhost:8000/api/docs/\n')
    
    def _create_base_cities(self):
        """Créer les villes de base de Côte d'Ivoire"""
        from apps.trips.models import City
        from django.utils.text import slugify
        
        cities = [
            {'name': 'Abidjan', 'latitude': 5.3600, 'longitude': -4.0083},
            {'name': 'Yamoussoukro', 'latitude': 6.8276, 'longitude': -5.2893},
            {'name': 'Bouaké', 'latitude': 7.6900, 'longitude': -5.0300},
            {'name': 'Daloa', 'latitude': 6.8772, 'longitude': -6.4503},
            {'name': 'San-Pédro', 'latitude': 4.7485, 'longitude': -6.6363},
            {'name': 'Korhogo', 'latitude': 9.4580, 'longitude': -5.6297},
            {'name': 'Man', 'latitude': 7.4125, 'longitude': -7.5539},
            {'name': 'Gagnoa', 'latitude': 6.1319, 'longitude': -5.9506},
            {'name': 'Divo', 'latitude': 5.8372, 'longitude': -5.3572},
            {'name': 'Sassandra', 'latitude': 4.9500, 'longitude': -6.0833},
        ]
        
        created_count = 0
        for city_data in cities:
            city, created = City.objects.get_or_create(
                name=city_data['name'],
                defaults={
                    'slug': slugify(city_data['name']),
                    'country': 'Côte d\'Ivoire',
                    'latitude': city_data['latitude'],
                    'longitude': city_data['longitude'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        return created_count
    
    def _create_base_faqs(self):
        """Créer des FAQs de base"""
        from apps.core.models import FAQ
        
        faqs = [
            {
                'category': FAQ.GENERAL,
                'question': 'Qu\'est-ce que Ticket Zen ?',
                'answer': 'Ticket Zen est une plateforme digitale qui vous permet de réserver et d\'acheter vos tickets de transport interurbain en ligne de manière simple et sécurisée.',
                'order': 1
            },
            {
                'category': FAQ.BOOKING,
                'question': 'Comment réserver un ticket ?',
                'answer': 'Pour réserver un ticket, recherchez votre trajet en indiquant la ville de départ, d\'arrivée et la date. Choisissez votre siège, puis procédez au paiement.',
                'order': 1
            },
            {
                'category': FAQ.PAYMENT,
                'question': 'Quels sont les moyens de paiement acceptés ?',
                'answer': 'Nous acceptons Orange Money, MTN Money, Moov Money, Wave, Visa et Mastercard.',
                'order': 1
            },
            {
                'category': FAQ.PAYMENT,
                'question': 'Le paiement en ligne est-il sécurisé ?',
                'answer': 'Oui, tous nos paiements sont sécurisés et cryptés. Nous utilisons CinetPay, une plateforme de paiement certifiée.',
                'order': 2
            },
            {
                'category': FAQ.CANCELLATION,
                'question': 'Puis-je annuler ma réservation ?',
                'answer': 'Oui, vous pouvez annuler votre réservation jusqu\'à 24 heures avant le départ. Le remboursement sera effectué sous 7 jours ouvrables.',
                'order': 1
            },
            {
                'category': FAQ.BOOKING,
                'question': 'Comment utiliser mon QR code ?',
                'answer': 'Présentez votre QR code reçu par email à l\'embarqueur lors de l\'embarquement. Le QR code sera scanné pour valider votre ticket.',
                'order': 2
            },
            {
                'category': FAQ.ACCOUNT,
                'question': 'Comment créer un compte ?',
                'answer': 'Cliquez sur "S\'inscrire", remplissez le formulaire avec vos informations et validez votre email.',
                'order': 1
            },
        ]
        
        created_count = 0
        for faq_data in faqs:
            faq, created = FAQ.objects.get_or_create(
                question=faq_data['question'],
                defaults=faq_data
            )
            if created:
                created_count += 1
        
        return created_count
    
    def _create_demo_data(self):
        """Créer des données de démonstration"""
        from apps.users.models import User
        from apps.companies.models import Company
        from apps.fleet.models import Vehicle
        from apps.trips.models import Trip, City
        from datetime import timedelta
        
        # Créer des utilisateurs de test
        test_users = [
            {
                'email': 'voyageur@demo.com',
                'password': 'demo123',
                'first_name': 'Jean',
                'last_name': 'Voyageur',
                'phone_number': '+225DEMO0001',
                'role': 'voyageur'
            },
            {
                'email': 'compagnie@demo.com',
                'password': 'demo123',
                'first_name': 'Transport',
                'last_name': 'Demo',
                'phone_number': '+225DEMO0002',
                'role': 'compagnie'
            },
        ]
        
        for user_data in test_users:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'phone_number': user_data['phone_number'],
                    'role': user_data['role'],
                    'is_active': True,
                    'is_verified': True
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f'      ✅ Utilisateur créé: {user.email}')
        
        # Créer une compagnie de démo
        company_user = User.objects.get(email='compagnie@demo.com')
        company, created = Company.objects.get_or_create(
            registration_number='DEMO123',
            defaults={
                'name': 'Transport Demo Express',
                'slug': 'transport-demo-express',
                'email': 'compagnie@demo.com',
                'phone_number': '+225DEMO0002',
                'address': 'Abidjan, Plateau',
                'city': 'Abidjan',
                'description': 'Compagnie de démonstration',
                'status': Company.APPROVED,
                'is_active': True,
                'commission_rate': 5.00
            }
        )
        if created:
            company_user.company = company
            company_user.save()
            self.stdout.write(f'      ✅ Compagnie créée: {company.name}')
        
        # Créer un véhicule de démo
        vehicle, created = Vehicle.objects.get_or_create(
            registration_number='DEMO-001-CI',
            defaults={
                'company': company,
                'vehicle_type': Vehicle.BUS,
                'brand': 'Mercedes',
                'model': 'Sprinter',
                'year': 2023,
                'total_seats': 30,
                'status': Vehicle.ACTIVE,
                'is_active': True,
                'has_ac': True,
                'has_wifi': True
            }
        )
        if created:
            self.stdout.write(f'      ✅ Véhicule créé: {vehicle.registration_number}')
        
        # Créer quelques voyages de démo
        abidjan = City.objects.get(name='Abidjan')
        yamoussoukro = City.objects.get(name='Yamoussoukro')
        bouake = City.objects.get(name='Bouaké')
        
        trips_data = [
            {
                'departure_city': abidjan,
                'arrival_city': yamoussoukro,
                'departure_datetime': timezone.now() + timedelta(days=1, hours=8),
                'estimated_arrival_datetime': timezone.now() + timedelta(days=1, hours=11),
                'estimated_duration': 180,
                'distance_km': 230,
                'base_price': 5000,
            },
            {
                'departure_city': abidjan,
                'arrival_city': bouake,
                'departure_datetime': timezone.now() + timedelta(days=2, hours=6),
                'estimated_arrival_datetime': timezone.now() + timedelta(days=2, hours=10),
                'estimated_duration': 240,
                'distance_km': 348,
                'base_price': 7000,
            },
        ]
        
        for trip_data in trips_data:
            trip, created = Trip.objects.get_or_create(
                company=company,
                vehicle=vehicle,
                departure_datetime=trip_data['departure_datetime'],
                defaults={
                    **trip_data,
                    'departure_location': f'Gare de {trip_data["departure_city"].name}',
                    'arrival_location': f'Gare de {trip_data["arrival_city"].name}',
                    'total_seats': 30,
                    'available_seats': 30,
                    'status': Trip.SCHEDULED,
                    'is_active': True,
                    'created_by': company_user
                }
            )
            if created:
                self.stdout.write(f'      ✅ Voyage créé: {trip.departure_city.name} → {trip.arrival_city.name}')
    
    def _create_directories(self):
        """Créer les dossiers nécessaires"""
        from django.conf import settings
        
        directories = [
            settings.MEDIA_ROOT / 'companies/logos',
            settings.MEDIA_ROOT / 'companies/documents',
            settings.MEDIA_ROOT / 'vehicles/photos',
            settings.MEDIA_ROOT / 'tickets/qr_codes',
            settings.MEDIA_ROOT / 'avatars',
            settings.MEDIA_ROOT / 'claims/attachments',
            settings.MEDIA_ROOT / 'exports',
            settings.BASE_DIR / 'logs',
            settings.BASE_DIR / 'keys',
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)