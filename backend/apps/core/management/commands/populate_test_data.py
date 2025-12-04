"""
Management command to populate the database with test data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta
from decimal import Decimal

from apps.trips.models import City, Trip
from apps.companies.models import Company
from apps.fleet.models import Vehicle
from apps.users.models import User


class Command(BaseCommand):
    help = 'Populate database with test data for development'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate test data...'))

        # Create Cities
        self.stdout.write('Creating cities...')
        cities_data = [
            {'name': 'Abidjan', 'country': 'CI', 'latitude': 5.3600, 'longitude': -4.0083},
            {'name': 'Yamoussoukro', 'country': 'CI', 'latitude': 6.8276, 'longitude': -5.2893},
            {'name': 'Bouaké', 'country': 'CI', 'latitude': 7.6900, 'longitude': -5.0300},
            {'name': 'San-Pédro', 'country': 'CI', 'latitude': 4.7500, 'longitude': -6.6333},
            {'name': 'Korhogo', 'country': 'CI', 'latitude': 9.4580, 'longitude': -5.6297},
            {'name': 'Man', 'country': 'CI', 'latitude': 7.4125, 'longitude': -7.5544},
        ]
        
        cities = {}
        for city_data in cities_data:
            # Check if city exists by name first
            try:
                city = City.objects.get(name=city_data['name'])
                cities[city.name] = city
                self.stdout.write(f'  - City already exists: {city.name}')
            except City.DoesNotExist:
                # Create new city with slug
                city_data['slug'] = slugify(city_data['name'])
                city = City.objects.create(**city_data)
                cities[city.name] = city
                self.stdout.write(f'  ✓ Created city: {city.name}')

        # Create Test Company User
        self.stdout.write('Creating test company user...')
        company_user, created = User.objects.get_or_create(
            email='company@test.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'Company',
                'phone_number': '+2250700000001',
                'role': 'compagnie',
                'is_active': True,
            }
        )
        if created:
            company_user.set_password('password123')
            company_user.save()
            self.stdout.write(f'  ✓ Created company user: {company_user.email}')
        else:
            self.stdout.write(f'  - Company user already exists: {company_user.email}')

        # Create Test Company
        self.stdout.write('Creating test company...')
        company, created = Company.objects.get_or_create(
            name='Transport Express CI',
            defaults={
                'slug': 'transport-express-ci',
                'registration_number': 'CI-TRANS-001',
                'address': 'Abidjan, Plateau',
                'city': 'Abidjan',
                'phone_number': '+2250700000001',
                'email': 'contact@transportexpress.ci',
                'description': 'Compagnie de transport leader en Côte d\'Ivoire',
                'status': 'approved',
                'commission_rate': Decimal('5.00'),
            }
        )
        if created:
            self.stdout.write(f'  ✓ Created company: {company.name}')
        else:
            self.stdout.write(f'  - Company already exists: {company.name}')

        # Link company to user
        if not company_user.company:
            company_user.company = company
            company_user.save()

        # Create Test Vehicles
        self.stdout.write('Creating test vehicles...')
        vehicles_data = [
            {
                'registration_number': 'CI-AB-1234',
                'brand': 'Mercedes',
                'model': 'Sprinter',
                'year': 2022,
                'total_seats': 30,
                'vehicle_type': 'bus',
                'status': 'active',
                'has_wifi': True,
                'has_ac': True,
                'has_usb_ports': True,
                'has_toilet': False,
            },
            {
                'registration_number': 'CI-AB-5678',
                'brand': 'Toyota',
                'model': 'Coaster',
                'year': 2021,
                'total_seats': 25,
                'vehicle_type': 'bus',
                'status': 'active',
                'has_wifi': True,
                'has_ac': True,
                'has_usb_ports': False,
                'has_toilet': False,
            },
        ]

        vehicles = []
        for vehicle_data in vehicles_data:
            vehicle, created = Vehicle.objects.get_or_create(
                registration_number=vehicle_data['registration_number'],
                defaults={**vehicle_data, 'company': company}
            )
            vehicles.append(vehicle)
            if created:
                self.stdout.write(f'  ✓ Created vehicle: {vehicle.registration_number}')
            else:
                self.stdout.write(f'  - Vehicle already exists: {vehicle.registration_number}')

        # Create Test Trips
        self.stdout.write('Creating test trips...')
        # Clear existing trips to ensure clean state
        Trip.objects.all().delete()
        self.stdout.write('  ✓ Cleared existing trips')
        
        base_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Define routes with frequencies
        routes = [
            # Abidjan -> Yamoussoukro (Frequent)
            {
                'departure': 'Abidjan', 'arrival': 'Yamoussoukro',
                'price': 5000, 'duration': 3, 'distance': 240,
                'times': [7, 9, 11, 14, 16, 18]  # Departures at these hours
            },
            # Yamoussoukro -> Abidjan (Return)
            {
                'departure': 'Yamoussoukro', 'arrival': 'Abidjan',
                'price': 5000, 'duration': 3, 'distance': 240,
                'times': [7, 9, 11, 14, 16, 18]
            },
            # Abidjan -> Bouaké
            {
                'departure': 'Abidjan', 'arrival': 'Bouaké',
                'price': 7000, 'duration': 5, 'distance': 350,
                'times': [6, 8, 10, 13, 15]
            },
            # Bouaké -> Abidjan
            {
                'departure': 'Bouaké', 'arrival': 'Abidjan',
                'price': 7000, 'duration': 5, 'distance': 350,
                'times': [6, 8, 10, 13, 15]
            },
            # Abidjan -> San-Pédro
            {
                'departure': 'Abidjan', 'arrival': 'San-Pédro',
                'price': 8000, 'duration': 6, 'distance': 350,
                'times': [7, 9, 14]
            },
            # San-Pédro -> Abidjan
            {
                'departure': 'San-Pédro', 'arrival': 'Abidjan',
                'price': 8000, 'duration': 6, 'distance': 350,
                'times': [7, 9, 14]
            },
            # Abidjan -> Korhogo (Long distance)
            {
                'departure': 'Abidjan', 'arrival': 'Korhogo',
                'price': 10000, 'duration': 9, 'distance': 600,
                'times': [6, 19] # Morning and Night bus
            },
            # Abidjan -> Man
            {
                'departure': 'Abidjan', 'arrival': 'Man',
                'price': 9000, 'duration': 8, 'distance': 580,
                'times': [7, 20]
            }
        ]

        trip_count = 0
        days_to_populate = 14  # Next 2 weeks
        
        for day_offset in range(days_to_populate):
            current_date = base_date + timedelta(days=day_offset)
            
            for route in routes:
                dep_city = cities.get(route['departure'])
                arr_city = cities.get(route['arrival'])
                
                if not dep_city or not arr_city:
                    continue
                    
                for hour in route['times']:
                    vehicle = vehicles[trip_count % len(vehicles)]
                    
                    departure_time = current_date.replace(hour=hour, minute=0)
                    # If time is in past for today, skip unless we want history
                    # But for testing, it's fine to have "missed" trips today
                    
                    arrival_time = departure_time + timedelta(hours=route['duration'])
                    
                    Trip.objects.create(
                        company=company,
                        vehicle=vehicle,
                        departure_city=dep_city,
                        arrival_city=arr_city,
                        departure_datetime=departure_time,
                        departure_location=f"Gare de {dep_city.name}",
                        arrival_location=f"Gare de {arr_city.name}",
                        estimated_arrival_datetime=arrival_time,
                        estimated_duration=route['duration'] * 60, # Minutes
                        distance_km=route['distance'],
                        base_price=Decimal(str(route['price'])),
                        status='scheduled',
                        is_active=True,
                        allows_cancellation=True,
                        cancellation_deadline_hours=24,
                        created_by=company_user,
                    )
                    trip_count += 1

        self.stdout.write(f'  ✓ Created {trip_count} new trips for the next {days_to_populate} days')

        # Create Test Traveler User
        self.stdout.write('Creating test traveler user...')
        traveler, created = User.objects.get_or_create(
            email='traveler@test.com',
            defaults={
                'first_name': 'Jean',
                'last_name': 'Kouassi',
                'phone_number': '+2250700000002',
                'role': 'voyageur',
                'is_active': True,
            }
        )
        if created:
            traveler.set_password('password123')
            traveler.save()
            self.stdout.write(f'  ✓ Created traveler user: {traveler.email}')
        else:
            self.stdout.write(f'  - Traveler user already exists: {traveler.email}')

        self.stdout.write(self.style.SUCCESS('\n✅ Test data population completed!'))
        self.stdout.write(self.style.SUCCESS('\nTest Credentials:'))
        self.stdout.write(f'  Company: company@test.com / password123')
        self.stdout.write(f'  Traveler: traveler@test.com / password123')
