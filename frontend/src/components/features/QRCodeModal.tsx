'use client';

import { useQuery } from '@tanstack/react-query';
import { ticketsService } from '@/services/tickets';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Download, Share2, MapPin, Calendar, User } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { fr } from 'date-fns/locale';
import { QRCodeCanvas } from 'qrcode.react';

export function QRCodeModal({ ticketId, open, onClose }: {
    ticketId: string;
    open: boolean;
    onClose: () => void;
}) {
    const { data: ticket, isLoading } = useQuery({
        queryKey: ['ticket', ticketId],
        queryFn: () => ticketsService.getById(ticketId),
        enabled: open,
    });

    const handleDownload = () => {
        const canvas = document.getElementById('qr-code-canvas') as HTMLCanvasElement;
        if (canvas) {
            const url = canvas.toDataURL('image/png');
            const link = document.createElement('a');
            link.download = `ticket-${ticket?.ticket_number || ticket?.id}.png`;
            link.href = url;
            link.click();
        }
    };

    return (
        <Dialog open={open} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle className="text-center text-2xl font-bold">
                        Votre Ticket Digital
                    </DialogTitle>
                </DialogHeader>

                {isLoading ? (
                    <div className="space-y-4 py-6">
                        <Skeleton className="h-64 w-64 mx-auto" />
                        <Skeleton className="h-20 w-full" />
                    </div>
                ) : ticket ? (
                    <div className="space-y-6 py-4">
                        {/* QR Code */}
                        <div className="bg-white p-6 rounded-xl border-2 border-slate-200">
                            <QRCodeCanvas
                                id="qr-code-canvas"
                                value={ticket.qr_code}
                                size={256}
                                level="H"
                                className="mx-auto"
                            />
                        </div>

                        {/* Ticket Info */}
                        <div className="bg-slate-50 rounded-xl p-4 space-y-3">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-slate-600">N° Ticket</span>
                                <span className="font-mono font-bold text-slate-900">{ticket.ticket_number || ticket.id.substring(0, 8)}</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                                <MapPin className="w-4 h-4 text-blue-600" />
                                <span className="font-medium">{ticket.trip.departure_city.name} → {ticket.trip.arrival_city.name}</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                                <Calendar className="w-4 h-4 text-blue-600" />
                                <span>{format(parseISO(ticket.trip.departure_datetime), "EEEE d MMMM 'à' HH:mm", { locale: fr })}</span>
                            </div>
                            <div className="flex items-center gap-2 text-sm">
                                <User className="w-4 h-4 text-blue-600" />
                                <span>{ticket.passenger_details.first_name} {ticket.passenger_details.last_name}</span>
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="grid grid-cols-2 gap-3">
                            <Button variant="outline" onClick={handleDownload}>
                                <Download className="w-4 h-4 mr-2" /> Télécharger
                            </Button>
                            <Button variant="outline">
                                <Share2 className="w-4 h-4 mr-2" /> Partager
                            </Button>
                        </div>

                        <p className="text-xs text-center text-slate-500">
                            Présentez ce QR code à l'embarquement
                        </p>
                    </div>
                ) : null}
            </DialogContent>
        </Dialog>
    );
}