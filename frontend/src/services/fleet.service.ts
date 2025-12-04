import { api } from '@/lib/api';
import { PaginatedResponse } from '@/types/api';

export interface Vehicle {
    id: number;
    company: number;
    registration_number: string;
    brand: string;
    model: string;
    year: number;
    capacity: number;
    type: 'bus' | 'minibus' | 'van';
    status: 'active' | 'maintenance' | 'retired';
    photo?: string;
    has_wifi: boolean;
    has_ac: boolean;
    has_usb: boolean;
    has_toilet: boolean;
    created_at: string;
    updated_at: string;
}

export const fleetService = {
    getAll: async (params?: any): Promise<PaginatedResponse<Vehicle>> => {
        const response = await api.get('/vehicles/', { params });
        return response.data;
    },

    getById: async (id: number): Promise<Vehicle> => {
        const response = await api.get(`/vehicles/${id}/`);
        return response.data;
    },

    create: async (data: Partial<Vehicle>): Promise<Vehicle> => {
        const response = await api.post('/vehicles/', data);
        return response.data;
    },

    update: async (id: number, data: Partial<Vehicle>): Promise<Vehicle> => {
        const response = await api.patch(`/vehicles/${id}/`, data);
        return response.data;
    },

    delete: async (id: number): Promise<void> => {
        await api.delete(`/vehicles/${id}/`);
    }
};
