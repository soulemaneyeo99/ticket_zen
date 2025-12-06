import { apiGet, apiDelete, apiPost } from '@/lib/api';
import { PaginatedResponse, Trip, City } from '@/types/api';

export interface SearchTripsParams {
    departure_city: number;
    arrival_city: number;
    date: string; // YYYY-MM-DD
}

export const tripsService = {
    search: async (params: SearchTripsParams) => {
        // The prompt says: GET /api/v1/trips/search/?departure_city=ID&arrival_city=ID&date=YYYY-MM-DD
        // apiGet handles params automatically if passed as second argument
        return apiGet<PaginatedResponse<Trip>>('/trips/search/', params as unknown as Record<string, unknown>);
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