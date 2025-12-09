import { apiGet, apiDelete, apiPost } from '@/lib/api';
import { PaginatedResponse, Trip, City } from '@/types/api';

export interface SearchTripsParams {
    departure_city: number;
    arrival_city: number;
    date: string; // YYYY-MM-DD
}

export const tripsService = {
    search: async (params: SearchTripsParams) => {
        const queryParams = {
            departure_city: params.departure_city,
            arrival_city: params.arrival_city,
            departure_date: params.date,
            passengers: 1 // Default to 1 as it's not yet in the form
        };
        return apiGet<PaginatedResponse<Trip>>('/trips/search/', queryParams);
    },

    getById: async (id: string) => {
        return apiGet<Trip>(`/trips/${id}/`);
    },

    getAll: async (params?: Record<string, unknown>) => {
        return apiGet<PaginatedResponse<Trip>>('/trips/', params);
    },

    delete: async (id: string) => {
        return apiDelete<void>(`/trips/${id}/`);
    },

    getCities: async () => {
        return apiGet<City[]>('/cities/');
    },

    create: async (data: Omit<Trip, 'id' | 'created_at' | 'updated_at'>) => {
        return apiPost<Trip>('/trips/', data);
    },
};