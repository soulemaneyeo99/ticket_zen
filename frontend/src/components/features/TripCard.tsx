'use client';

import { useState } from 'react';
import { Trip } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Bus, Clock, Wifi, Snowflake, MapPin, ChevronDown, ChevronUp } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import Link from 'next/link';
import dynamic from 'next/dynamic';

// Dynamically import RouteMap to avoid SSR issues with Leaflet
const RouteMap = dynamic(() => import('@/components/features/RouteMap'), {
    ssr: false,
    loading: () => (
        <div className="w-full h-64 bg-slate-100 rounded-lg flex items-center justify-center">
            <div className="text-slate-500">Chargement de la carte...</div>
        </div>
    ),
});

export function TripCard({ trip }: { trip: Trip }) {
    const [showMap, setShowMap] = useState(false);
    const departTime = format(parseISO(trip.departure_datetime), 'HH:mm');
    const arrivalTime = format(parseISO(trip.arrival_datetime), 'HH:mm');
    const price = parseInt(trip.price).toLocaleString();

    return (
        <Card className="overflow-hidden hover:shadow-lg transition-shadow border-slate-200">
            {/* Top: Company & Price */}
            <div className="p-4 bg-slate-50 flex justify-between items-start border-b border-slate-100">
                <div className="flex items-center gap-3">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    {trip.company.logo ? (
                        <img
                            src={trip.company.logo}
                            alt={trip.company.name}
                            className="w-10 h-10 rounded-full object-cover bg-white border"
                        />
                    ) : (
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <Bus className="w-5 h-5 text-blue-600" />
                        </div>
                    )}
                    <div>
                        <h3 className="font-bold text-slate-900">{trip.company.name}</h3>
                        <div className="flex gap-2 text-xs text-slate-500">
                            {trip.vehicle.has_wifi && (
                                <span className="flex items-center gap-1">
                                    <Wifi className="w-3 h-3" /> WiFi
                                </span>
                            )}
                            {trip.vehicle.has_ac && (
                                <span className="flex items-center gap-1">
                                    <Snowflake className="w-3 h-3" /> AC
                                </span>
                            )}
                        </div>
                    </div>
                </div>
                <div className="text-right">
                    <span className="block text-xl font-bold text-amber-600">
                        {price} FCFA
                    </span>
                    <Badge
                        variant={trip.available_seats > 5 ? 'secondary' : 'destructive'}
                        className="text-xs"
                    >
                        {trip.available_seats} places
                    </Badge>
                </div>
            </div>

            {/* Middle: Schedule */}
            <div className="p-4 bg-white">
                <div className="flex items-center justify-between">
                    <div className="text-center w-1/3">
                        <div className="text-2xl font-bold text-slate-900">{departTime}</div>
                        <div className="text-sm text-slate-500 truncate">
                            {trip.departure_city.name}
                        </div>
                    </div>

                    <div className="flex-1 flex flex-col items-center px-2">
                        <div className="text-xs text-slate-400 flex items-center gap-1 mb-1">
                            <Clock className="w-3 h-3" />
                        </div>
                        <div className="w-full h-px bg-slate-200 relative flex items-center justify-center">
                            <div className="absolute right-0 -top-1 w-2 h-2 border-t border-r border-slate-300 rotate-45" />
                        </div>
                    </div>

                    <div className="text-center w-1/3">
                        <div className="text-2xl font-bold text-slate-900">{arrivalTime}</div>
                        <div className="text-sm text-slate-500 truncate">
                            {trip.arrival_city.name}
                        </div>
                    </div>
                </div>
            </div>

            {/* Map Section (Collapsible) */}
            {showMap && (
                <div className="px-4 pb-4">
                    <RouteMap
                        departureCity={trip.departure_city}
                        arrivalCity={trip.arrival_city}
                        distance={trip.distance_km}
                        height="250px"
                    />
                </div>
            )}

            {/* Bottom: CTA */}
            <div className="p-3 bg-slate-50 space-y-2">
                <button
                    onClick={() => setShowMap(!showMap)}
                    className="w-full flex items-center justify-center gap-2 py-2 text-sm text-blue-700 hover:text-blue-800 font-medium transition-colors"
                >
                    <MapPin className="w-4 h-4" />
                    {showMap ? 'Masquer' : 'Voir'} l&apos;itinéraire
                    {showMap ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>

                <Link href={`/trips/${trip.id}/book`}>
                    <Button className="w-full bg-blue-900 hover:bg-blue-800 text-white h-11 font-semibold">
                        Réserver ce billet
                    </Button>
                </Link>
            </div>
        </Card>
    );
}