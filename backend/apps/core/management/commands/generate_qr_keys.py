"""
Commande pour générer les clés RSA pour QR codes
"""
from django.core.management.base import BaseCommand
from utils.qr_generator import QRCodeGenerator


class Command(BaseCommand):
    help = 'Générer les clés RSA pour les QR codes sécurisés'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la regénération même si les clés existent',
        )
    
    def handle(self, *args, **options):
        import os
        from django.conf import settings
        
        private_key_path = settings.QR_CODE_RSA_PRIVATE_KEY_PATH
        public_key_path = settings.QR_CODE_RSA_PUBLIC_KEY_PATH
        
        # Vérifier si les clés existent déjà
        if os.path.exists(private_key_path) and os.path.exists(public_key_path):
            if not options['force']:
                self.stdout.write(self.style.WARNING(
                    '\n⚠️  Les clés RSA existent déjà !\n'
                ))
                self.stdout.write(f'   Clé privée: {private_key_path}')
                self.stdout.write(f'   Clé publique: {public_key_path}\n')
                self.stdout.write('   Utilisez --force pour regénérer les clés.\n')
                return
            else:
                self.stdout.write(self.style.WARNING(
                    '\n⚠️  Regénération des clés RSA (--force activé)...\n'
                ))
                # Supprimer les anciennes clés
                if os.path.exists(private_key_path):
                    os.remove(private_key_path)
                if os.path.exists(public_key_path):
                    os.remove(public_key_path)
        
        # Générer les nouvelles clés
        self.stdout.write('🔐 Génération des clés RSA pour QR codes sécurisés...\n')
        
        try:
            generator = QRCodeGenerator()
            
            self.stdout.write(self.style.SUCCESS('✅ Clés RSA générées avec succès !\n'))
            self.stdout.write(f'   📁 Clé privée: {generator.private_key_path}')
            self.stdout.write(f'   📁 Clé publique: {generator.public_key_path}\n')
            
            # Tester les clés
            self.stdout.write('🧪 Test des clés...')
            test_token = generator.generate_test_token()
            
            try:
                decoded = generator.decode_qr_code(test_token)
                self.stdout.write(self.style.SUCCESS('   ✅ Test réussi - Les clés fonctionnent correctement\n'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Erreur lors du test: {e}\n'))
            
            # Avertissement de sécurité
            self.stdout.write(self.style.WARNING('⚠️  IMPORTANT - SÉCURITÉ'))
            self.stdout.write(self.style.WARNING('='*70))
            self.stdout.write('   • NE JAMAIS commiter les clés dans Git')
            self.stdout.write('   • Garder la clé privée STRICTEMENT confidentielle')
            self.stdout.write('   • En production, stocker les clés de manière sécurisée')
            self.stdout.write('   • Faire des backups sécurisés des clés')
            self.stdout.write(self.style.WARNING('='*70 + '\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Erreur lors de la génération: {e}\n'))
            raise