"""
Vue temporaire pour initialiser les villes
À supprimer après utilisation
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils.text import slugify
from apps.trips.models import City


@api_view(['POST'])
@permission_classes([AllowAny])
def initialize_cities(request):
    """Endpoint temporaire pour créer les villes"""
    
    # Vérifier un token secret pour sécurité
    secret = request.data.get('secret')
    if secret != 'init-cities-2024':
        return Response({'error': 'Unauthorized'}, status=403)
    
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
        else:
            updated_count += 1

    return Response({
        'success': True,
        'message': f'{created_count} villes créées, {updated_count} mises à jour',
        'total': created_count + updated_count
    })
