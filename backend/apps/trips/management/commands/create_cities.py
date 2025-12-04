"""
Script pour créer les villes de Côte d'Ivoire dans la base de données
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.trips.models import City


class Command(BaseCommand):
    help = 'Crée les principales villes de Côte d\'Ivoire'

    def handle(self, *args, **options):
        cities_data = [
            {'name': 'Abidjan', 'latitude': 5.3600, 'longitude': -4.0083},
            {'name': 'Yamoussoukro', 'latitude': 6.8276, 'longitude': -5.2893},
            {'name': 'Bouaké', 'latitude': 7.6900, 'longitude': -5.0300},
            {'name': 'Daloa', 'latitude': 6.8770, 'longitude': -6.4503},
            {'name': 'San-Pédro', 'latitude': 4.7485, 'longitude': -6.6363},
            {'name': 'Korhogo', 'latitude': 9.4580, 'longitude': -5.6296},
            {'name': 'Man', 'latitude': 7.4125, 'longitude': -7.5539},
            {'name': 'Gagnoa', 'latitude': 6.1319, 'longitude': -5.9506},
            {'name': 'Abengourou', 'latitude': 6.7297, 'longitude': -3.4967},
            {'name': 'Divo', 'latitude': 5.8372, 'longitude': -5.3572},
            {'name': 'Soubré', 'latitude': 5.7856, 'longitude': -6.6039},
            {'name': 'Bondoukou', 'latitude': 8.0406, 'longitude': -2.8000},
            {'name': 'Odienné', 'latitude': 9.5000, 'longitude': -7.5667},
            {'name': 'Séguéla', 'latitude': 7.9611, 'longitude': -6.6731},
            {'name': 'Sassandra', 'latitude': 4.9500, 'longitude': -6.0833},
            {'name': 'Grand-Bassam', 'latitude': 5.2111, 'longitude': -3.7389},
            {'name': 'Adzopé', 'latitude': 6.1069, 'longitude': -3.8589},
            {'name': 'Agboville', 'latitude': 5.9281, 'longitude': -4.2139},
        ]

        created_count = 0
        updated_count = 0

        for city_data in cities_data:
            city, created = City.objects.update_or_create(
                name=city_data['name'],
                defaults={
                    'slug': slugify(city_data['name']),
                    'country': 'Côte d\'Ivoire',
                    'latitude': city_data.get('latitude'),
                    'longitude': city_data.get('longitude'),
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Ville créée: {city.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'→ Ville mise à jour: {city.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Terminé! {created_count} villes créées, {updated_count} mises à jour.'
            )
        )
