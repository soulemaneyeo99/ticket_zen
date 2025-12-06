'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { tripsService } from '@/services/trips';
import { Trip } from '@/types/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, Trash2, Edit, Calendar } from 'lucide-react';
import { toast } from 'sonner';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function TripsPage() {
    const queryClient = useQueryClient();
    const [page] = useState(1);

    const { data, isLoading } = useQuery({
        queryKey: ['trips', page],
        queryFn: () => tripsService.getAll({ page }),
    });

    const deleteMutation = useMutation({
        mutationFn: (id: string) => tripsService.delete(id), // Assuming delete exists or I need to add it
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['trips'] });
            toast.success("Voyage supprimé");
        },
        onError: () => {
            toast.error("Erreur lors de la suppression");
        }
    });

    const handleDelete = (id: string) => {
        if (confirm('Êtes-vous sûr de vouloir supprimer ce voyage ?')) {
            deleteMutation.mutate(id);
        }
    };

    return (
        <div className="p-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Mes Voyages</h1>
                <Link href="/company/trips/new">
                    <Button>
                        <Plus className="w-4 h-4 mr-2" />
                        Créer un voyage
                    </Button>
                </Link>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Liste des voyages programmés</CardTitle>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="text-center py-8">Chargement...</div>
                    ) : data?.results?.length === 0 ? (
                        <div className="text-center py-12 text-gray-500">
                            <Calendar className="w-12 h-12 mx-auto mb-4 opacity-20" />
                            <p>Aucun voyage programmé.</p>
                        </div>
                    ) : (
                        <div className="relative w-full overflow-auto">
                            <table className="w-full caption-bottom text-sm text-left">
                                <thead className="[&_tr]:border-b">
                                    <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Départ</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Arrivée</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Date & Heure</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Véhicule</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Prix</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Statut</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="[&_tr:last-child]:border-0">
                                    {data?.results.map((trip: Trip) => (
                                        <tr key={trip.id} className="border-b transition-colors hover:bg-muted/50">
                                            <td className="p-4 align-middle font-medium">
                                                {trip.departure_city.name}
                                            </td>
                                            <td className="p-4 align-middle">
                                                {trip.arrival_city.name}
                                            </td>
                                            <td className="p-4 align-middle">
                                                {format(new Date(trip.departure_datetime), 'dd MMM yyyy HH:mm', { locale: fr })}
                                            </td>
                                            <td className="p-4 align-middle">
                                                {trip.vehicle.type}
                                            </td>
                                            <td className="p-4 align-middle">{trip.price} FCFA</td>
                                            <td className="p-4 align-middle">
                                                <span className={`px-2 py-1 rounded-full text-xs ${trip.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                                                    trip.status === 'completed' ? 'bg-green-100 text-green-800' :
                                                        'bg-gray-100 text-gray-800'
                                                    }`}>
                                                    {trip.status}
                                                </span>
                                            </td>
                                            <td className="p-4 align-middle text-right">
                                                <Button variant="ghost" size="icon" asChild>
                                                    <Link href={`/company/trips/${trip.id}`}>
                                                        <Edit className="w-4 h-4" />
                                                    </Link>
                                                </Button>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="text-red-500 hover:text-red-700 hover:bg-red-50"
                                                    onClick={() => handleDelete(trip.id)}
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </Button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
