import { api } from '@/lib/axios';
import { Ticket } from './ticket.service';

export interface BoardingPass {
    id: number;
    ticket: Ticket;
    scanned_at: string;
    status: 'valid' | 'invalid' | 'duplicate';
    location: string;
}

export const boardingService = {
    scan: async (qrData: string, location?: string): Promise<BoardingPass> => {
        const response = await api.post('/boarding/scan/', {
            qr_data: qrData,
            location: location || 'Unknown'
        });
        return response.data;
    },

    getHistory: async (): Promise<BoardingPass[]> => {
        const response = await api.get('/boarding/history/');
        return response.data;
    }
};
