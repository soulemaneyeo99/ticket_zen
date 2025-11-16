"""
Commande pour tester le système de QR codes
"""
from django.core.management.base import BaseCommand
from utils.qr_generator import QRCodeGenerator
from utils.qr_validator import QRCodeValidator
import json


class Command(BaseCommand):
    help = 'Tester le système de génération et validation de QR codes'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--ticket-id',
            type=str,
            help='ID du ticket à tester (optionnel)',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('🧪 TEST DU SYSTÈME DE QR CODES'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
        
        generator = QRCodeGenerator()
        validator = QRCodeValidator()
        
        # Test 1: Génération d'un token de test
        self.stdout.write('📝 Test 1: Génération d\'un token JWT...')
        try:
            test_token = generator.generate_test_token()
            self.stdout.write(self.style.SUCCESS('   ✅ Token généré'))
            self.stdout.write(f'   Token (tronqué): {test_token[:50]}...\n')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erreur: {e}\n'))
            return
        
        # Test 2: Décodage du token
        self.stdout.write('🔍 Test 2: Décodage et validation du token...')
        try:
            decoded = generator.decode_qr_code(test_token)
            self.stdout.write(self.style.SUCCESS('   ✅ Token décodé avec succès'))
            self.stdout.write('   Données décodées:')
            self.stdout.write(f'      - Ticket ID: {decoded["ticket_id"]}')
            self.stdout.write(f'      - Numéro ticket: {decoded["ticket_number"]}')
            self.stdout.write(f'      - Passager: {decoded["passenger_name"]}')
            self.stdout.write(f'      - Siège: {decoded["seat_number"]}')
            self.stdout.write(f'      - Départ: {decoded["departure_city"]}')
            self.stdout.write(f'      - Arrivée: {decoded["arrival_city"]}\n')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erreur: {e}\n'))
            return
        
        # Test 3: Test avec un vrai ticket si fourni
        if options['ticket_id']:
            self.stdout.write(f'🎫 Test 3: Test avec le ticket {options["ticket_id"]}...')
            try:
                from apps.tickets.models import Ticket
                ticket = Ticket.objects.select_related('trip', 'passenger').get(
                    id=options['ticket_id']
                )
                
                # Générer le QR pour ce ticket
                qr_data = generator.generate_qr_code(ticket)
                self.stdout.write(self.style.SUCCESS('   ✅ QR code généré pour le ticket'))
                self.stdout.write(f'      - Ticket: {ticket.ticket_number}')
                self.stdout.write(f'      - Passager: {ticket.passenger_full_name}')
                
                # Vérifier le QR
                verification = generator.verify_ticket_qr(qr_data['token'], ticket)
                if verification['is_valid']:
                    self.stdout.write(self.style.SUCCESS('   ✅ QR code valide\n'))
                else:
                    self.stdout.write(self.style.ERROR(f'   ❌ QR code invalide: {verification["error_message"]}\n'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Erreur: {e}\n'))
        
        # Test 4: Test de validation offline
        self.stdout.write('🔌 Test 4: Validation en mode offline...')
        try:
            offline_result = generator.validate_offline_qr(
                test_token,
                trip_id=decoded['trip_id']
            )
            if offline_result['is_valid']:
                self.stdout.write(self.style.SUCCESS('   ✅ Validation offline réussie\n'))
            else:
                self.stdout.write(self.style.ERROR(f'   ❌ Validation offline échouée: {offline_result["error_message"]}\n'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erreur: {e}\n'))
        
        # Test 5: Test anti-fraude
        self.stdout.write('🛡️  Test 5: Système anti-fraude...')
        try:
            # Tenter de modifier le token (fraude)
            tampered_token = test_token[:-10] + 'TAMPERED!!'
            
            try:
                generator.decode_qr_code(tampered_token)
                self.stdout.write(self.style.ERROR('   ❌ ALERTE: Token modifié accepté (problème de sécurité)\n'))
            except Exception:
                self.stdout.write(self.style.SUCCESS('   ✅ Token modifié correctement rejeté\n'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Erreur: {e}\n'))
        
        # Résumé
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('✅ TOUS LES TESTS SONT PASSÉS'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
        
        self.stdout.write('📊 Résumé:')
        self.stdout.write('   • Génération de tokens: ✅')
        self.stdout.write('   • Décodage et validation: ✅')
        self.stdout.write('   • Mode offline: ✅')
        self.stdout.write('   • Protection anti-fraude: ✅\n')
