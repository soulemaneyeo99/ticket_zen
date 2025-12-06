'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/hooks/use-auth';
import { ticketsService } from '@/services/tickets';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { User, Calendar, QrCode, Download, Bus, CheckCircle, Clock } from 'lucide-react';
import { format, parseISO, isFuture } from 'date-fns';
import { fr } from 'date-fns/locale';
import Link from 'next/link';
import { QRCodeModal } from '@/components/features/QRCodeModal';

export default function ClientDashboard() {
    const { user, logout } = useAuth();
    const [selectedTicket, setSelectedTicket] = useState<string | null>(null);

    const { data: ticketsData, isLoading } = useQuery({
        queryKey: ['my-tickets'],
        queryFn: ticketsService.getMyTickets,
        enabled: !!user,
    });

    const tickets = ticketsData?.results || [];
    const upcomingTickets = tickets.filter(t => isFuture(parseISO(t.trip.departure_datetime)));
    const pastTickets = tickets.filter(t => !isFuture(parseISO(t.trip.departure_datetime)));

    if (!user) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50">
                <Card className="max-w-md mx-auto p-8 text-center">
                    <p className="text-slate-600 mb-4">Connectez-vous pour voir vos réservations</p>
                    <Link href="/">
                        <Button className="bg-blue-600 hover:bg-blue-700">Retour à l&apos;accueil</Button>
                    </Link>
                </Card>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50">
            {/* Header */}
            <header className="bg-gradient-to-r from-blue-600 to-blue-700 text-white pt-12 pb-24 px-4">
                <div className="container mx-auto max-w-5xl">
                    <div className="flex items-center justify-between mb-8">
                        <div className="flex items-center gap-4">
                            <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                                <User className="w-8 h-8 text-white" />
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold">Bonjour, {user.first_name} !</h1>
                                <p className="text-blue-100">Prêt pour votre prochain voyage ?</p>
                            </div>
                        </div>
                        <Button variant="ghost" className="text-white hover:bg-white/10" onClick={logout}>
                            Déconnexion
                        </Button>
                    </div>

                    {/* Stats Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <StatCard
                            label="Voyages à venir"
                            value={upcomingTickets.length}
                            icon={<Calendar className="w-6 h-6" />}
                            color="blue"
                        />
                        <StatCard
                            label="Voyages effectués"
                            value={pastTickets.length}
                            icon={<CheckCircle className="w-6 h-6" />}
                            color="green"
                        />
                        <StatCard
                            label="Points Fidélité"
                            value={120}
                            icon={<Bus className="w-6 h-6" />}
                            color="amber"
                        />
                    </div>
                </div>
            </header>

            {/* Content */}
            <div className="container mx-auto max-w-5xl px-4 -mt-12">
                <Card className="border-0 shadow-xl bg-white min-h-[500px]">
                    <div className="p-6 border-b">
                        <div className="flex items-center justify-between">
                            <h2 className="text-2xl font-bold text-slate-900">Mes Réservations</h2>
                            <Link href="/trips/search">
                                <Button className="bg-blue-600 hover:bg-blue-700">
                                    Nouvelle réservation
                                </Button>
                            </Link>
                        </div>
                    </div>

                    <div className="p-6">
                        <Tabs defaultValue="upcoming" className="w-full">
                            <TabsList className="grid w-full grid-cols-2 mb-8">
                                <TabsTrigger value="upcoming" className="text-base">
                                    À venir ({upcomingTickets.length})
                                </TabsTrigger>
                                <TabsTrigger value="history" className="text-base">
                                    Historique ({pastTickets.length})
                                </TabsTrigger>
                            </TabsList>

                            <TabsContent value="upcoming" className="space-y-6">
                                {isLoading ? (
                                    <TicketsLoadingSkeleton />
                                ) : upcomingTickets.length === 0 ? (
                                    <EmptyState
                                        icon={<Bus className="w-12 h-12" />}
                                        title="Aucun voyage à venir"
                                        description="Réservez votre prochain voyage dès maintenant"
                                        action={
                                            <Link href="/trips/search">
                                                <Button className="bg-blue-600 hover:bg-blue-700 mt-4">
                                                    Rechercher un billet
                                                </Button>
                                            </Link>
                                        }
                                    />
                                ) : (
                                    upcomingTickets.map(ticket => (
                                        <TicketCard
                                            key={ticket.id}
                                            ticket={ticket}
                                            onViewQR={() => setSelectedTicket(ticket.id)}
                                        />
                                    ))
                                )}
                            </TabsContent>

                            <TabsContent value="history" className="space-y-6">
                                {isLoading ? (
                                    <TicketsLoadingSkeleton />
                                ) : pastTickets.length === 0 ? (
                                    <EmptyState
                                        icon={<Clock className="w-12 h-12" />}
                                        title="Aucun historique"
                                        description="Vos voyages passés apparaîtront ici"
                                    />
                                ) : (
                                    pastTickets.map(ticket => (
                                        <TicketCard key={ticket.id} ticket={ticket} isPast />
                                    ))
                                )}
                            </TabsContent>
                        </Tabs>
                    </div>
                </Card>
            </div>

            {/* QR Code Modal */}
            {selectedTicket && (
                <QRCodeModal
                    ticketId={selectedTicket}
                    open={!!selectedTicket}
                    onClose={() => setSelectedTicket(null)}
                />
            )}
        </div>
    );
}

// ============= SUB-COMPONENTS =============

function StatCard({ label, value, icon, color }: {
    label: string;
    value: number;
    icon: React.ReactNode;
    color: 'blue' | 'green' | 'amber';
}) {
    const colorClasses = {
        blue: 'bg-white/10 text-white',
        green: 'bg-white/10 text-white',
        amber: 'bg-gradient-to-br from-amber-500 to-orange-600 text-white',
    };

    return (
        <Card className={`border-0 backdrop-blur-sm ${colorClasses[color]} shadow-lg`}>
            <CardContent className="p-6">
                <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium opacity-90">{label}</p>
                    {icon}
                </div>
                <p className="text-3xl font-bold">{value}</p>
            </CardContent>
        </Card>
    );
}

function TicketCard({ ticket, isPast = false, onViewQR }: {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    ticket: any;
    isPast?: boolean;
    onViewQR?: () => void;
}) {
    const departTime = format(parseISO(ticket.trip.departure_datetime), 'HH:mm');
    const departDate = format(parseISO(ticket.trip.departure_datetime), 'dd MMM yyyy', { locale: fr });
    const price = parseInt(ticket.price).toLocaleString();

    return (
        <Card className={`border overflow-hidden transition-all ${isPast ? 'bg-slate-50 opacity-75' : 'bg-white hover:shadow-md'}`}>
            <div className="p-6">
                <div className="flex flex-col md:flex-row justify-between gap-6">
                    {/* Left: Trip Info */}
                    <div className="flex-grow space-y-4">
                        <div className="flex justify-between items-start">
                            <div>
                                <h3 className="font-bold text-lg text-slate-900">{ticket.trip.company_name}</h3>
                                <Badge variant={ticket.status === 'confirmed' ? 'default' : 'secondary'} className="mt-1">
                                    {ticket.status === 'confirmed' ? 'Confirmé' : ticket.status}
                                </Badge>
                            </div>
                            <div className="text-right md:hidden">
                                <span className="font-bold text-xl text-blue-600">{price} FCFA</span>
                            </div>
                        </div>

                        <div className="flex items-center gap-8">
                            <div className="flex flex-col">
                                <span className="text-2xl font-bold text-slate-900">{departTime}</span>
                                <span className="text-sm text-slate-500">{ticket.trip.departure_city_name}</span>
                            </div>

                            <div className="flex-grow flex items-center">
                                <div className="h-0.5 w-full bg-slate-200 relative">
                                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-slate-300" />
                                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-slate-300" />
                                    <Bus className="w-4 h-4 text-slate-400 absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white px-1" />
                                </div>
                            </div>

                            <div className="flex flex-col text-right">
                                <span className="text-2xl font-bold text-slate-900">--:--</span>
                                <span className="text-sm text-slate-500">{ticket.trip.arrival_city_name}</span>
                            </div>
                        </div>

                        <div className="flex items-center gap-4 text-sm text-slate-500">
                            <div className="flex items-center gap-2">
                                <Calendar className="w-4 h-4" />
                                {departDate}
                            </div>
                            <div className="flex items-center gap-2">
                                <User className="w-4 h-4" />
                                {ticket.passenger_first_name} {ticket.passenger_last_name}
                            </div>
                        </div>
                    </div>

                    {/* Right: Actions */}
                    <div className="flex flex-col gap-3 md:w-48 md:border-l md:pl-6 border-slate-100">
                        <div className="hidden md:block text-right mb-2">
                            <span className="font-bold text-xl text-blue-600">{price} FCFA</span>
                        </div>
                        {!isPast && (
                            <>
                                <Button className="bg-blue-600 hover:bg-blue-700 w-full" onClick={onViewQR}>
                                    <QrCode className="w-4 h-4 mr-2" /> QR Code
                                </Button>
                                <Button variant="outline" className="w-full">
                                    <Download className="w-4 h-4 mr-2" /> Télécharger
                                </Button>
                            </>
                        )}
                        {isPast && (
                            <Button variant="outline" className="w-full">
                                Reçu de voyage
                            </Button>
                        )}
                    </div>
                </div>
            </div>
        </Card>
    );
}

function TicketsLoadingSkeleton() {
    return (
        <div className="space-y-6">
            {[1, 2, 3].map(i => (
                <Card key={i} className="p-6">
                    <div className="flex justify-between gap-6">
                        <div className="flex-grow space-y-4">
                            <Skeleton className="h-6 w-48" />
                            <div className="flex gap-8">
                                <Skeleton className="h-12 w-24" />
                                <Skeleton className="h-12 flex-grow" />
                                <Skeleton className="h-12 w-24" />
                            </div>
                            <Skeleton className="h-4 w-64" />
                        </div>
                        <div className="w-48 space-y-3">
                            <Skeleton className="h-11 w-full" />
                            <Skeleton className="h-11 w-full" />
                        </div>
                    </div>
                </Card>
            ))}
        </div>
    );
}

function EmptyState({ icon, title, description, action }: {
    icon: React.ReactNode;
    title: string;
    description: string;
    action?: React.ReactNode;
}) {
    return (
        <div className="text-center py-16">
            <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-400">
                {icon}
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">{title}</h3>
            <p className="text-slate-500 mb-6">{description}</p>
            {action}
        </div>
    );
}