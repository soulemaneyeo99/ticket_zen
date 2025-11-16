"""
Commande Django pour tester le flow de paiement
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.users.models import User
from apps.companies.models import Company
from apps.trips.models import Trip, City
from apps.fleet.models import Vehicle
from apps.tickets.models import Ticket
from apps.payments.services import MockPaymentTestHelper
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Tester le flow de paiement complet (mocké)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--scenario',
            type=str,
            default='success',
            help='Scénario à tester: success, failed, refund'
        )
    
    @transaction.atomic
    def handle(self, *args, **options):
        scenario = options['scenario']
        
        self.stdout.write(self.style.SUCCESS(f'\n🧪 Test du flow de paiement - Scénario: {scenario}\n'))
        
        # Créer les données de test
        test_data = self.create_test_data()
        
        # Créer un ticket
        ticket = self.create_test_ticket(test_data)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Ticket créé: {ticket.ticket_number}'))
        self.stdout.write(f'   Montant: {ticket.total_amount} FCFA')
        self.stdout.write(f'   Voyage: {ticket.trip.departure_city.name} → {ticket.trip.arrival_city.name}\n')
        
        # Tester selon le scénario
        helper = MockPaymentTestHelper()
        
        if scenario == 'success':
            result = helper.simulate_payment_flow(
                ticket=ticket,
                payment_method='orange_money',
                phone_number='+225XXXXXXXX'
            )
            
            if result['success']:
                self.stdout.write(self.style.SUCCESS('\n✅ PAIEMENT RÉUSSI'))
                self.stdout.write(f'   Transaction ID: {result["payment"].transaction_id}')
                self.stdout.write(f'   Statut: {result["payment"].get_status_display()}')
                self.stdout.write(f'   Montant: {result["payment"].amount} FCFA')
                
                # Vérifier le ticket
                ticket.refresh_from_db()
                self.stdout.write(f'\n✅ Ticket confirmé: {ticket.status}')
                self.stdout.write(f'   QR Code généré: {"Oui" if ticket.qr_code else "Non"}')
            else:
                self.stdout.write(self.style.ERROR(f'\n❌ ÉCHEC: {result["message"]}'))
        
        elif scenario == 'failed':
            result = helper.simulate_failed_payment_flow(
                ticket=ticket,
                payment_method='mtn_money',
                phone_number='+225XXXXXXXX'
            )
            
            self.stdout.write(self.style.WARNING('\n⚠️ PAIEMENT ÉCHOUÉ (SIMULATION)'))
            self.stdout.write(f'   Transaction ID: {result["payment"].transaction_id}')
            self.stdout.write(f'   Statut: {result["payment"].get_status_display()}')
            
            # Vérifier le ticket
            ticket.refresh_from_db()
            self.stdout.write(f'\n   Ticket: {ticket.status}')
        
        elif scenario == 'refund':
            # D'abord créer un paiement réussi
            result = helper.simulate_payment_flow(
                ticket=ticket,
                payment_method='wave',
                phone_number='+225XXXXXXXX'
            )
            
            if result['success']:
                self.stdout.write(self.style.SUCCESS('\n✅ Paiement initial réussi'))
                
                # Tester le remboursement
                refund_result = helper.test_refund(result['payment'])
                
                if refund_result['success']:
                    self.stdout.write(self.style.SUCCESS('\n✅ REMBOURSEMENT RÉUSSI'))
                    self.stdout.write(f'   Refund ID: {refund_result["refund_transaction_id"]}')
                    
                    result['payment'].refresh_from_db()
                    self.stdout.write(f'   Statut paiement: {result["payment"].get_status_display()}')
                    self.stdout.write(f'   Montant remboursé: {result["payment"].refund_amount} FCFA')
                else:
                    self.stdout.write(self.style.ERROR(f'\n❌ Remboursement échoué: {refund_result["message"]}'))
        
        else:
            self.stdout.write(self.style.ERROR(f'\n❌ Scénario inconnu: {scenario}'))
            self.stdout.write('   Scénarios disponibles: success, failed, refund')
        
        self.stdout.write('\n')
    
    def create_test_data(self):
        """Créer les données de test nécessaires"""
        # Créer un voyageur
        voyageur, created = User.objects.get_or_create(
            email='voyageur@test.com',
            defaults={
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'phone_number': '+225XXXXXXXX',
                'role': 'voyageur',
                'is_active': True
            }
        )
        if created:
            voyageur.set_password('testpass123')
            voyageur.save()
        
        # Créer une compagnie
        company, _ = Company.objects.get_or_create(
            registration_number='TEST123',
            defaults={
                'name': 'Test Transport Company',
                'slug': 'test-transport',
                'email': 'company@test.com',
                'phone_number': '+225YYYYYYYY',
                'address': 'Abidjan, Cocody',
                'city': 'Abidjan',
                'status': Company.APPROVED,
                'is_active': True,
                'commission_rate': 5.00
            }
        )
        
        # Créer un utilisateur compagnie
        company_user, created = User.objects.get_or_create(
            email='company@test.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'Company',
                'phone_number': '+225YYYYYYYY',
                'role': 'compagnie',
                'company': company,
                'is_active': True
            }
        )
        if created:
            company_user.set_password('testpass123')
            company_user.save()
        
        # Créer des villes
        abidjan, _ = City.objects.get_or_create(
            name='Abidjan',
            defaults={'slug': 'abidjan', 'is_active': True}
        )
        yamoussoukro, _ = City.objects.get_or_create(
            name='Yamoussoukro',
            defaults={'slug': 'yamoussoukro', 'is_active': True}
        )
        
        # Créer un véhicule
        vehicle, _ = Vehicle.objects.get_or_create(
            registration_number='TEST-001-CI',
            defaults={
                'company': company,
                'vehicle_type': Vehicle.BUS,
                'brand': 'Mercedes',
                'model': 'Sprinter',
                'year': 2023,
                'total_seats': 30,
                'status': Vehicle.ACTIVE,
                'is_active': True
            }
        )
        
        # Créer un voyage
        departure_time = timezone.now() + timedelta(days=1, hours=8)
        arrival_time = departure_time + timedelta(hours=3)
        
        trip, _ = Trip.objects.get_or_create(
            company=company,
            vehicle=vehicle,
            departure_datetime=departure_time,
            defaults={
                'departure_city': abidjan,
                'arrival_city': yamoussoukro,
                'departure_location': 'Gare de Adjamé',
                'arrival_location': 'Gare de Yamoussoukro',
                'estimated_arrival_datetime': arrival_time,
                'estimated_duration': 180,
                'distance_km': 230,
                'base_price': 5000,
                'total_seats': 30,
                'available_seats': 30,
                'status': Trip.SCHEDULED,
                'is_active': True,
                'created_by': company_user
            }
        )
        
        return {
            'voyageur': voyageur,
            'company': company,
            'company_user': company_user,
            'trip': trip,
            'vehicle': vehicle,
            'abidjan': abidjan,
            'yamoussoukro': yamoussoukro
        }
    
    def create_test_ticket(self, test_data):
        """Créer un ticket de test"""
        from apps.core.models import PlatformSettings
        
        settings = PlatformSettings.load()
        
        ticket = Ticket.objects.create(
            trip=test_data['trip'],
            passenger=test_data['voyageur'],
            passenger_first_name=test_data['voyageur'].first_name,
            passenger_last_name=test_data['voyageur'].last_name,
            passenger_phone=test_data['voyageur'].phone_number,
            passenger_email=test_data['voyageur'].email,
            seat_number='A1',
            price=test_data['trip'].base_price,
            platform_fee=test_data['trip'].base_price * settings.default_commission_rate / 100,
            status=Ticket.PENDING
        )
        
        return ticket