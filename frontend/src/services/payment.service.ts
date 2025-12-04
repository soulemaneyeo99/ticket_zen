import { api } from '@/lib/axios';
import { PaginatedResponse } from '@/types';

export interface Payment {
    id: string; // UUID
    transaction_id: string;
    amount: number;
    payment_method: 'mobile_money' | 'credit_card' | 'cash';
    status: 'pending' | 'completed' | 'failed' | 'refunded';
    payment_provider: string;
    created_at: string;
}

export interface PaymentInitResponse {
    payment_url: string;
    transaction_id: string;
}

export interface PaymentRequest {
    amount: number;
    currency: string;
    description: string;
    customer_name: string;
    customer_surname: string;
    customer_phone_number: string;
    customer_email: string;
    customer_address: string;
    customer_city: string;
    customer_country: string;
    customer_state: string;
    customer_zip_code: string;
    payment_method: 'MOBILE_MONEY' | 'CREDIT_CARD';
    ticket_id: string; // Changed from trip_id
}

export const paymentService = {
    initiate: async (data: {
        trip_id: number;
        amount: number;
        payment_method: string;
        phone_number?: string;
        passenger_data: any;
    }): Promise<PaymentInitResponse> => {
        const response = await api.post('/payments/initiate/', data);
        return response.data;
    },

    // Alias for initiate to match UI usage and CinetPay structure
    initiatePayment: async (data: PaymentRequest): Promise<PaymentInitResponse> => {
        // Map PaymentRequest to the structure expected by the backend's initiate endpoint
        const payload = {
            ticket_id: data.ticket_id, // Changed from trip_id
            amount: data.amount,
            payment_method: data.payment_method === 'MOBILE_MONEY' ? 'mobile_money' : 'credit_card',
            phone_number: data.customer_phone_number,
            // passenger_data is not needed by backend initialize endpoint as it uses the ticket's passenger
        };
        const response = await api.post('/payments/initiate/', payload);
        return response.data;
    },

    checkStatus: async (transactionId: string): Promise<Payment> => {
        const response = await api.get(`/payments/check_status/?transaction_id=${transactionId}`);
        return response.data;
    },

    getAll: async (params?: any): Promise<PaginatedResponse<Payment>> => {
        const response = await api.get('/payments/', { params });
        return response.data;
    }
};
