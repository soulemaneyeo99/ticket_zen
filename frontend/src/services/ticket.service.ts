import { api } from '@/lib/axios';
import { PaginatedResponse, User } from '@/types';
import { Trip } from './trip.service';

export interface Ticket {
    id: string; // UUID
    ticket_number: string;
    trip: Trip;
    user: User;
    passenger_first_name: string;
    passenger_last_name: string;
    passenger_phone: string;
    passenger_email?: string;
    seat_number: string;
    price: number;
    status: 'pending' | 'confirmed' | 'cancelled' | 'used' | 'refunded';
    qr_code: string;
    payment_status: 'pending' | 'paid' | 'failed';
    created_at: string;
}

export interface CreateTicketData {
    trip: number;
    passenger_first_name: string;
    passenger_last_name: string;
    passenger_phone: string;
    passenger_email: string;
    seat_number: string;
    price: number;
}

export const ticketService = {
    getAll: async (params?: any): Promise<PaginatedResponse<Ticket>> => {
        const response = await api.get('/tickets/', { params });
        return response.data;
    },

    getMyTickets: async (): Promise<PaginatedResponse<Ticket>> => {
        return ticketService.getAll();
    },

    getById: async (id: string): Promise<Ticket> => {
        const response = await api.get(`/tickets/${id}/`);
        return response.data;
    },

    create: async (data: Partial<Ticket> | CreateTicketData): Promise<Ticket> => {
        const response = await api.post('/tickets/', data);
        return response.data;
    },

    cancel: async (id: string): Promise<void> => {
        await api.post(`/tickets/${id}/cancel/`);
    },

    verify: async (qrData: string): Promise<any> => {
        const response = await api.post('/tickets/verify_ticket/', { qr_data: qrData });
        return response.data;
    },

    download: async (id: string): Promise<Blob> => {
        const response = await api.get(`/tickets/${id}/download/`, { responseType: 'blob' });
        return response.data;
    }
};
