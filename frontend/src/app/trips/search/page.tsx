'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { tripService } from '@/services/trip.service';
import { Trip } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { format, addDays, parseISO, isSameDay } from 'date-fns';
import { fr } from 'date-fns/locale';
import {
    MapPin,
    Clock,
    ArrowRight,
    Bus,
    Wifi,
    Zap,
    Armchair,
    Filter,
    ArrowLeft
} from 'lucide-react';
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';

function SearchPageContent() {
    const searchParams = useSearchParams();
    const router = useRouter();

    const departureCityId = searchParams.get('departure_city');
    const arrivalCityId = searchParams.get('arrival_city');
    const dateParam = searchParams.get('date');

    const [trips, setTrips] = useState<Trip[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedDate, setSelectedDate] = useState<Date>(
        dateParam ? parseISO(dateParam) : new Date()
    );

    // Derived state for header (using first trip or params)
    const [routeInfo, setRouteInfo] = useState({ from: '...', to: '...' });

    useEffect(() => {
        const fetchTrips = async () => {
            if (!departureCityId || !arrivalCityId) return;

            setLoading(true);
            try {
                const dateStr = format(selectedDate, 'yyyy-MM-dd');
                const data = await tripService.searchTrips({
                    departure_city: departureCityId,
                    arrival_city: arrivalCityId,
                    date: dateStr
                });
                setTrips(data.results || []);

                // Update header info if we have results
                if (data.results.length > 0) {
                    setRouteInfo({
                        from: data.results[0].departure_city_name,
                        to: data.results[0].arrival_city_name
                    });
                }
            } catch (error) {
                console.error('Error fetching trips:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchTrips();
    }, [departureCityId, arrivalCityId, selectedDate]);

    const handleDateSelect = (date: Date) => {
        setSelectedDate(date);
        // Update URL without full reload
        const params = new URLSearchParams(searchParams);
        params.set('date', format(date, 'yyyy-MM-dd'));
        router.replace(`/trips/search?${params.toString()}`);
    };

    // Generate date strip (today + next 14 days)
    const dateStrip = Array.from({ length: 14 }, (_, i) => addDays(new Date(), i));

    return (
        <div className="min-h-screen bg-gray-50 pb-20">
            {/* Header Mobile */}
            <div className="bg-blue-600 text-white p-4 sticky top-0 z-10 shadow-md">
                <div className="flex items-center gap-4 mb-4">
                    <Link href="/" className="p-2 hover:bg-blue-700 rounded-full transition-colors">
                        <ArrowLeft className="w-6 h-6" />
                    </Link>
                    <div className="flex-1">
                        <h1 className="font-bold text-lg flex items-center gap-2">
                            {routeInfo.from} <ArrowRight className="w-4 h-4" /> {routeInfo.to}
                        </h1>
                        <p className="text-blue-100 text-sm capitalize">
                            {format(selectedDate, 'EEEE d MMMM', { locale: fr })}
                        </p>
                    </div>
                    <Button variant="ghost" size="icon" className="text-white hover:bg-blue-700">
                        <Filter className="w-5 h-5" />
                    </Button>
                </div>

                {/* Date Strip */}
                <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide -mx-4 px-4">
                    {dateStrip.map((date) => {
                        const isSelected = isSameDay(date, selectedDate);
                        return (
                            <button
                                key={date.toISOString()}
                                onClick={() => handleDateSelect(date)}
                                className={`
                                    flex flex-col items-center justify-center min-w-[60px] p-2 rounded-xl transition-all
                                    ${isSelected
                                        ? 'bg-white text-blue-600 shadow-lg scale-105 font-bold'
                                        : 'bg-blue-700/50 text-blue-100 hover:bg-blue-700'}
                                `}
                            >
                                <span className="text-xs uppercase">{format(date, 'EEE', { locale: fr })}</span>
                                <span className="text-lg font-bold">{format(date, 'd')}</span>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Content */}
            <div className="container max-w-md mx-auto p-4 space-y-4">
                {loading ? (
                    // Loading Skeletons
                    Array.from({ length: 3 }).map((_, i) => (
                        <Card key={i} className="border-none shadow-sm">
                            <CardContent className="p-4 space-y-3">
                                <div className="flex justify-between">
                                    <Skeleton className="h-4 w-24" />
                                    <Skeleton className="h-4 w-16" />
                                </div>
                                <div className="flex justify-between items-center">
                                    <Skeleton className="h-8 w-20" />
                                    <Skeleton className="h-px w-12" />
                                    <Skeleton className="h-8 w-20" />
                                </div>
                                <Skeleton className="h-10 w-full rounded-lg" />
                            </CardContent>
                        </Card>
                    ))
                ) : trips.length > 0 ? (
                    trips.map((trip) => (
                        <Card key={trip.id} className="border-none shadow-sm hover:shadow-md transition-shadow overflow-hidden group">
                            <CardContent className="p-0">
                                {/* Top Part: Company & Price */}
                                <div className="p-4 border-b border-gray-100 flex justify-between items-start">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600">
                                            <Bus className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-gray-900">{trip.company_name}</h3>
                                            <div className="flex gap-2 text-xs text-gray-500 mt-1">
                                                <span className="flex items-center gap-1"><Wifi className="w-3 h-3" /> WiFi</span>
                                                <span className="flex items-center gap-1"><Zap className="w-3 h-3" /> Prise</span>
                                                <span className="flex items-center gap-1"><Armchair className="w-3 h-3" /> Confort</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <span className="block text-lg font-bold text-blue-600">
                                            {parseInt(trip.base_price).toLocaleString()} FCFA
                                        </span>
                                        <Badge variant="secondary" className="text-xs font-normal">
                                            {trip.available_seats} places
                                        </Badge>
                                    </div>
                                </div>

                                {/* Middle Part: Schedule */}
                                <div className="p-4 bg-white">
                                    <div className="flex items-center justify-between relative">
                                        {/* Departure */}
                                        <div className="text-center w-1/3">
                                            <div className="text-xl font-bold text-gray-900">
                                                {format(parseISO(trip.departure_datetime), 'HH:mm')}
                                            </div>
                                            <div className="text-xs text-gray-500 truncate px-1">
                                                {trip.departure_city_name}
                                            </div>
                                        </div>

                                        {/* Duration Arrow */}
                                        <div className="flex-1 flex flex-col items-center px-2">
                                            <div className="text-xs text-gray-400 mb-1 flex items-center gap-1">
                                                <Clock className="w-3 h-3" />
                                                {Math.floor((trip.estimated_duration || 0) / 60)}h{((trip.estimated_duration || 0) % 60).toString().padStart(2, '0')}
                                            </div>
                                            <div className="w-full h-px bg-gray-200 relative">
                                                <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 border-t border-r border-gray-300 rotate-45"></div>
                                            </div>
                                        </div>

                                        {/* Arrival (Estimated) */}
                                        <div className="text-center w-1/3">
                                            <div className="text-xl font-bold text-gray-900">
                                                {/* Calculate arrival time roughly */}
                                                {format(addDays(parseISO(trip.departure_datetime), 0), 'HH:mm')}
                                            </div>
                                            <div className="text-xs text-gray-500 truncate px-1">
                                                {trip.arrival_city_name}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Bottom Part: Action */}
                                <div className="p-3 bg-gray-50">
                                    <Link href={`/trips/${trip.id}/book`} className="block">
                                        <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold h-11 rounded-xl shadow-blue-200 shadow-lg">
                                            Réserver ce billet
                                        </Button>
                                    </Link>
                                </div>
                            </CardContent>
                        </Card>
                    ))
                ) : (
                    // Empty State
                    <div className="text-center py-12 px-4">
                        <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <Bus className="w-10 h-10 text-gray-400" />
                        </div>
                        <h3 className="text-lg font-bold text-gray-900 mb-2">Aucun voyage trouvé</h3>
                        <p className="text-gray-500 mb-6">
                            Désolé, nous n'avons pas trouvé de voyages pour cette date. Essayez de changer de date ci-dessus.
                        </p>
                        <Button
                            variant="outline"
                            onClick={() => handleDateSelect(addDays(new Date(), 1))}
                            className="rounded-full"
                        >
                            Voir les voyages de demain
                        </Button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default function SearchPage() {
    return (
        <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><Skeleton className="h-12 w-12 rounded-full" /></div>}>
            <SearchPageContent />
        </Suspense>
    );
}
