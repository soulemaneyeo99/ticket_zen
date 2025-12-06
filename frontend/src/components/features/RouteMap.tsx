'use client';

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { fetchRouteCoordinates, formatDistance, getMapBounds } from '@/lib/map-utils';

// Fix for default marker icons in Next.js
// eslint-disable-next-line @typescript-eslint/no-explicit-any
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icons for departure and arrival
const departureIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

const arrivalIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

interface City {
    name: string;
    latitude: number;
    longitude: number;
}

interface RouteMapProps {
    departureCity: City;
    arrivalCity: City;
    distance?: number;
    className?: string;
    height?: string;
}

// Component to fit bounds
function FitBounds({ bounds }: { bounds: [[number, number], [number, number]] }) {
    const map = useMap();

    useEffect(() => {
        map.fitBounds(bounds, { padding: [50, 50] });
    }, [map, bounds]);

    return null;
}

export default function RouteMap({
    departureCity,
    arrivalCity,
    distance: providedDistance,
    className = '',
    height = '400px',
}: RouteMapProps) {
    const [routeCoordinates, setRouteCoordinates] = useState<[number, number][]>([]);
    const [calculatedDistance, setCalculatedDistance] = useState<number | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    const bounds = getMapBounds(
        departureCity.latitude,
        departureCity.longitude,
        arrivalCity.latitude,
        arrivalCity.longitude
    );

    useEffect(() => {
        const loadRoute = async () => {
            try {
                setLoading(true);
                setError(false);

                const result = await fetchRouteCoordinates(
                    departureCity.latitude,
                    departureCity.longitude,
                    arrivalCity.latitude,
                    arrivalCity.longitude
                );

                setRouteCoordinates(result.coordinates);
                setCalculatedDistance(result.distance);
            } catch (err) {
                console.error('Failed to load route:', err);
                setError(true);
                // Fallback to straight line
                setRouteCoordinates([
                    [departureCity.latitude, departureCity.longitude],
                    [arrivalCity.latitude, arrivalCity.longitude],
                ]);
            } finally {
                setLoading(false);
            }
        };

        loadRoute();
    }, [departureCity, arrivalCity]);

    const displayDistance = providedDistance || calculatedDistance;

    return (
        <div className={`relative ${className}`} style={{ height }}>
            {loading && (
                <div className="absolute inset-0 bg-slate-100 flex items-center justify-center z-10 rounded-lg">
                    <div className="text-slate-600 flex flex-col items-center gap-2">
                        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                        <span className="text-sm">Chargement de la carte...</span>
                    </div>
                </div>
            )}

            <MapContainer
                bounds={bounds}
                scrollWheelZoom={false}
                className="w-full h-full rounded-lg z-0"
                style={{ height: '100%' }}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <FitBounds bounds={bounds} />

                {/* Departure marker */}
                <Marker
                    position={[departureCity.latitude, departureCity.longitude]}
                    icon={departureIcon}
                >
                    <Popup>
                        <div className="text-center">
                            <p className="font-bold text-green-700">Départ</p>
                            <p className="text-sm">{departureCity.name}</p>
                        </div>
                    </Popup>
                </Marker>

                {/* Arrival marker */}
                <Marker
                    position={[arrivalCity.latitude, arrivalCity.longitude]}
                    icon={arrivalIcon}
                >
                    <Popup>
                        <div className="text-center">
                            <p className="font-bold text-red-700">Arrivée</p>
                            <p className="text-sm">{arrivalCity.name}</p>
                        </div>
                    </Popup>
                </Marker>

                {/* Route line */}
                {routeCoordinates.length > 0 && (
                    <Polyline
                        positions={routeCoordinates}
                        pathOptions={{
                            color: '#3b82f6',
                            weight: 4,
                            opacity: 0.7,
                            dashArray: error ? '10, 10' : undefined,
                        }}
                    />
                )}
            </MapContainer>

            {/* Distance badge */}
            {displayDistance && (
                <div className="absolute top-4 right-4 bg-white px-4 py-2 rounded-lg shadow-lg z-[1000] border border-slate-200">
                    <div className="flex items-center gap-2">
                        <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                        </svg>
                        <span className="font-bold text-slate-900">{formatDistance(displayDistance)}</span>
                    </div>
                </div>
            )}

            {error && (
                <div className="absolute bottom-4 left-4 bg-amber-50 px-3 py-2 rounded-lg shadow-sm z-[1000] border border-amber-200">
                    <p className="text-xs text-amber-700">Tracé approximatif</p>
                </div>
            )}
        </div>
    );
}
