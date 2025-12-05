/**
 * Utility functions for map and route calculations
 */

/**
 * Calculate distance between two coordinates using Haversine formula
 * @param lat1 Latitude of first point
 * @param lon1 Longitude of first point
 * @param lat2 Latitude of second point
 * @param lon2 Longitude of second point
 * @returns Distance in kilometers
 */
export function calculateDistance(
    lat1: number,
    lon1: number,
    lat2: number,
    lon2: number
): number {
    const R = 6371; // Radius of the Earth in km
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);

    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(toRad(lat1)) *
        Math.cos(toRad(lat2)) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c;

    return Math.round(distance * 10) / 10; // Round to 1 decimal
}

function toRad(degrees: number): number {
    return degrees * (Math.PI / 180);
}

/**
 * Format distance for display
 */
export function formatDistance(km: number): string {
    if (km < 1) {
        return `${Math.round(km * 1000)} m`;
    }
    return `${km.toFixed(1)} km`;
}

/**
 * Fetch route coordinates from OpenRouteService
 * Falls back to straight line if API fails
 */
export async function fetchRouteCoordinates(
    startLat: number,
    startLon: number,
    endLat: number,
    endLon: number
): Promise<{ coordinates: [number, number][]; distance: number }> {
    try {
        // Using OpenRouteService free tier (no API key needed for basic usage)
        const response = await fetch(
            `https://api.openrouteservice.org/v2/directions/driving-car?start=${startLon},${startLat}&end=${endLon},${endLat}`,
            {
                headers: {
                    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
                },
            }
        );

        if (!response.ok) {
            throw new Error('Route API failed');
        }

        const data = await response.json();
        const route = data.features[0];
        const coordinates: [number, number][] = route.geometry.coordinates.map(
            (coord: number[]) => [coord[1], coord[0]] // Swap to [lat, lon]
        );
        const distance = route.properties.segments[0].distance / 1000; // Convert to km

        return { coordinates, distance: Math.round(distance * 10) / 10 };
    } catch (error) {
        console.warn('Failed to fetch route, using straight line:', error);
        // Fallback to straight line
        const distance = calculateDistance(startLat, startLon, endLat, endLon);
        return {
            coordinates: [
                [startLat, startLon],
                [endLat, endLon],
            ],
            distance,
        };
    }
}

/**
 * Get map bounds for two points with padding
 */
export function getMapBounds(
    lat1: number,
    lon1: number,
    lat2: number,
    lon2: number
): [[number, number], [number, number]] {
    const minLat = Math.min(lat1, lat2);
    const maxLat = Math.max(lat1, lat2);
    const minLon = Math.min(lon1, lon2);
    const maxLon = Math.max(lon1, lon2);

    return [
        [minLat, minLon],
        [maxLat, maxLon],
    ];
}
