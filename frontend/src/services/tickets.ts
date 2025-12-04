import { apiGet, apiPost } from '@/lib/api';
import { CreateTicketPayload, Ticket, PaginatedResponse } from '@/types/api';

export const ticketsService = {
    create: (payload: CreateTicketPayload) =>
        apiPost<Ticket>('/tickets/', payload),

    getMyTickets: () =>
        apiGet<PaginatedResponse<Ticket>>('/tickets/'),

    getById: (id: string) =>
        apiGet<Ticket>(`/tickets/${id}/`),

    cancel: (id: string) =>
        apiPost<void>(`/tickets/${id}/cancel/`),
};