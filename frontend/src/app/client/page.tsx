'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/store/auth.store';
import { ticketService, Ticket } from '@/services/ticket.service';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, QrCode, Download, MapPin, Calendar, Clock, Bus, User } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function ClientDashboard() {
    const { user } = useAuthStore();
    const [tickets, setTickets] = useState<Ticket[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTickets = async () => {
            try {
                const data = await ticketService.getMyTickets();
                setTickets(data.results || []);
            } catch (error) {
                console.error('Error fetching tickets:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchTickets();
    }, []);

    const upcomingTickets = tickets.filter(t => new Date(t.trip.departure_time) > new Date());
    const pastTickets = tickets.filter(t => new Date(t.trip.departure_time) <= new Date());

    return (
        <div className="min-h-screen bg-gray-50 pb-20">
            {/* Header */}
            <div className="bg-blue-600 text-white pt-12 pb-24 px-4">
                <div className="container mx-auto max-w-5xl">
                    <div className="flex items-center space-x-4 mb-6">
                        <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                            <User className="w-8 h-8 text-white" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold">Bonjour, {user?.first_name} !</h1>
                            <p className="text-blue-100">Prêt pour votre prochain voyage ?</p>
                        </div>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <Card className="bg-white/10 border-0 backdrop-blur-sm text-white">
                            <CardContent className="p-6">
                                <p className="text-blue-100 text-sm font-medium">Voyages à venir</p>
                                <p className="text-3xl font-bold mt-1">{upcomingTickets.length}</p>
                            </CardContent>
                        </Card>
                        <Card className="bg-white/10 border-0 backdrop-blur-sm text-white">
                            <CardContent className="p-6">
                                <p className="text-blue-100 text-sm font-medium">Voyages effectués</p>
                                <p className="text-3xl font-bold mt-1">{pastTickets.length}</p>
                            </CardContent>
                        </Card>
                        <Card className="bg-gradient-to-br from-orange-500 to-orange-600 border-0 text-white shadow-lg">
                            <CardContent className="p-6">
                                <p className="text-orange-100 text-sm font-medium">Points Fidélité</p>
                                <p className="text-3xl font-bold mt-1">120 pts</p>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="container mx-auto max-w-5xl px-4 -mt-12">
                <Card className="border-0 shadow-xl bg-white min-h-[500px]">
                    <CardHeader>
                        <CardTitle>Mes Réservations</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Tabs defaultValue="upcoming" className="w-full">
                            <TabsList className="grid w-full grid-cols-2 mb-8">
                                <TabsTrigger value="upcoming">À venir</TabsTrigger>
                                <TabsTrigger value="history">Historique</TabsTrigger>
                            </TabsList>

                            <TabsContent value="upcoming" className="space-y-6">
                                {loading ? (
                                    <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-blue-600" /></div>
                                ) : upcomingTickets.length === 0 ? (
                                    <div className="text-center py-12 text-gray-500">
                                        <Bus className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                                        <p>Aucun voyage à venir.</p>
                                        <Link href="/trips/search">
                                            <Button variant="link" className="text-blue-600 mt-2">Réserver un billet</Button>
                                        </Link>
                                    </div>
                                ) : (
                                    upcomingTickets.map(ticket => <TicketCard key={ticket.id} ticket={ticket} />)
                                )}
                            </TabsContent>

                            <TabsContent value="history" className="space-y-6">
                                {loading ? (
                                    <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-blue-600" /></div>
                                ) : pastTickets.length === 0 ? (
                                    <div className="text-center py-12 text-gray-500">
                                        <p>Aucun historique de voyage.</p>
                                    </div>
                                ) : (
                                    pastTickets.map(ticket => <TicketCard key={ticket.id} ticket={ticket} isPast />)
                                )}
                            </TabsContent>
                        </Tabs>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

function TicketCard({ ticket, isPast = false }: { ticket: Ticket, isPast?: boolean }) {
    return (
        <div className={`border rounded-xl p-6 transition-all ${isPast ? 'bg-gray-50 opacity-75' : 'bg-white hover:shadow-md border-gray-200'}`}>
            <div className="flex flex-col md:flex-row justify-between md:items-center gap-6">
                <div className="space-y-4 flex-grow">
                    <div className="flex justify-between items-start">
                        <div>
                            <h3 className="font-bold text-lg text-gray-900">{ticket.trip.company_name || 'Compagnie'}</h3>
                            <Badge variant={ticket.status === 'confirmed' ? 'default' : 'secondary'} className="mt-1">
                                {ticket.status === 'confirmed' ? 'Confirmé' : ticket.status}
                            </Badge>
                        </div>
                        <div className="text-right md:hidden">
                            <span className="font-bold text-blue-600">{ticket.price} FCFA</span>
                        </div>
                    </div>

                    <div className="flex items-center space-x-8">
                        <div className="flex flex-col">
                            <span className="text-2xl font-bold text-gray-900">{format(new Date(ticket.trip.departure_time), 'HH:mm')}</span>
                            <span className="text-sm text-gray-500">{typeof ticket.trip.departure_city === 'object' ? ticket.trip.departure_city.name : ''}</span>
                        </div>
                        <div className="flex-grow flex items-center">
                            <div className="h-0.5 w-full bg-gray-200 relative">
                                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-gray-300"></div>
                                <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-gray-300"></div>
                                <Bus className="w-4 h-4 text-gray-400 absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white px-1" />
                            </div>
                        </div>
                        <div className="flex flex-col text-right">
                            <span className="text-2xl font-bold text-gray-900">{format(new Date(ticket.trip.arrival_time), 'HH:mm')}</span>
                            <span className="text-sm text-gray-500">{typeof ticket.trip.arrival_city === 'object' ? ticket.trip.arrival_city.name : ''}</span>
                        </div>
                    </div>

                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center">
                            <Calendar className="w-4 h-4 mr-2" />
                            {format(new Date(ticket.trip.departure_time), 'd MMMM yyyy', { locale: fr })}
                        </div>
                        <div className="flex items-center">
                            <User className="w-4 h-4 mr-2" />
                            {ticket.passenger_first_name} {ticket.passenger_last_name}
                        </div>
                    </div>
                </div>

                <div className="flex flex-col space-y-3 md:w-48 md:border-l md:pl-6 border-gray-100">
                    <div className="hidden md:block text-right mb-2">
                        <span className="font-bold text-xl text-blue-600">{ticket.price} FCFA</span>
                    </div>
                    {!isPast && (
                        <>
                            <Button className="w-full bg-blue-600 hover:bg-blue-700">
                                <QrCode className="w-4 h-4 mr-2" /> Voir QR Code
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
    );
}
