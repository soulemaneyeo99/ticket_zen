import { api } from '@/lib/axios';
import { PaginatedResponse, Trip, City } from '@/types';
import { Vehicle } from './fleet.service';
import { Company } from './company.service';

export const tripService = {
    getAll: async (params?: any): Promise<PaginatedResponse<Trip>> => {
        const response = await api.get('/trips/', { params });
        return response.data;
    },

    getById: async (id: number): Promise<Trip> => {
        const response = await api.get(`/trips/${id}/`);
        return response.data;
    },

    // Alias for getById to match UI usage
    getTrip: async (id: string | number): Promise<Trip> => {
        const response = await api.get(`/trips/${id}/`);
        return response.data;
    },

    create: async (data: Partial<Trip>): Promise<Trip> => {
        const response = await api.post('/trips/', data);
        return response.data;
    },

    update: async (id: number, data: Partial<Trip>): Promise<Trip> => {
        const response = await api.patch(`/trips/${id}/`, data);
        return response.data;
    },

    delete: async (id: number): Promise<void> => {
        await api.delete(`/trips/${id}/`);
    },

    // Renamed to match UI usage
    searchTrips: async (params: { departure_city?: string; arrival_city?: string; date?: string }): Promise<PaginatedResponse<Trip>> => {
        // Validate required parameters
        if (!params.departure_city || !params.arrival_city || !params.date) {
            console.error('Missing required search parameters:', params);
            throw new Error('Departure city, arrival city, and date are required');
        }

        const payload = {
            departure_city: parseInt(params.departure_city),
            arrival_city: parseInt(params.arrival_city),
            departure_date: params.date
        };

        console.log('Search payload:', payload);

        try {
            const response = await api.post('/trips/search/', payload);
            return response.data;
        } catch (error: any) {
            console.error('Search error:', error.response?.data || error.message);
            throw error;
        }
    },

    getCities: async (): Promise<City[]> => {
        const response = await api.get('/cities/');
        // Handle both paginated and list responses
        return Array.isArray(response.data) ? response.data : response.data.results;
    }
};
