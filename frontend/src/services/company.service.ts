import { api } from '@/lib/api';
import { PaginatedResponse } from '@/types/api';

export interface Company {
    id: number;
    name: string;
    logo?: string;
    address: string;
    phone: string;
    email: string;
    website?: string;
    description?: string;
    status: 'pending' | 'approved' | 'rejected' | 'suspended';
    commission_rate: number;
    created_at: string;
    updated_at: string;
}

export interface CompanyStats {
    total_trips: number;
    total_revenue: number;
    average_occupancy: number;
    active_vehicles: number;
}

export const companyService = {
    getAll: async (params?: Record<string, unknown>): Promise<PaginatedResponse<Company>> => {
        const response = await api.get('/companies/', { params });
        return response.data;
    },

    getById: async (id: number): Promise<Company> => {
        const response = await api.get(`/companies/${id}/`);
        return response.data;
    },

    create: async (data: Partial<Company>): Promise<Company> => {
        const response = await api.post('/companies/', data);
        return response.data;
    },

    update: async (id: number, data: Partial<Company>): Promise<Company> => {
        const response = await api.patch(`/companies/${id}/`, data);
        return response.data;
    },

    delete: async (id: number): Promise<void> => {
        await api.delete(`/companies/${id}/`);
    },

    getStats: async (id: number): Promise<CompanyStats> => {
        const response = await api.get(`/companies/${id}/stats/`);
        return response.data;
    },

    validate: async (id: number, status: 'approved' | 'rejected' | 'suspended', adminNotes?: string): Promise<Company> => {
        const response = await api.post(`/companies/${id}/validate_company/`, { status, admin_notes: adminNotes });
        return response.data;
    }
};
