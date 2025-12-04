'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { fleetService, Vehicle } from '@/services/fleet.service';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, Trash2, Edit, Bus } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// Since I haven't created the Table component yet, I'll use a simple HTML table structure or create the component.
// Let's create the Table component first in the next step or inline it.
// I'll inline a simple table for now to avoid blocking.

export default function FleetPage() {
    const { toast } = useToast();
    const queryClient = useQueryClient();
    const [page, setPage] = useState(1);

    const { data, isLoading } = useQuery({
        queryKey: ['vehicles', page],
        queryFn: () => fleetService.getAll({ page }),
    });

    const deleteMutation = useMutation({
        mutationFn: fleetService.delete,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['vehicles'] });
            toast({ title: "Véhicule supprimé" });
        },
        onError: () => {
            toast({ variant: "destructive", title: "Erreur lors de la suppression" });
        }
    });

    const handleDelete = (id: number) => {
        if (confirm('Êtes-vous sûr de vouloir supprimer ce véhicule ?')) {
            deleteMutation.mutate(id);
        }
    };

    return (
        <div className="p-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Ma Flotte</h1>
                <Link href="/company/fleet/new">
                    <Button>
                        <Plus className="w-4 h-4 mr-2" />
                        Ajouter un véhicule
                    </Button>
                </Link>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Liste des véhicules</CardTitle>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="text-center py-8">Chargement...</div>
                    ) : data?.results?.length === 0 ? (
                        <div className="text-center py-12 text-gray-500">
                            <Bus className="w-12 h-12 mx-auto mb-4 opacity-20" />
                            <p>Aucun véhicule enregistré.</p>
                        </div>
                    ) : (
                        <div className="relative w-full overflow-auto">
                            <table className="w-full caption-bottom text-sm text-left">
                                <thead className="[&_tr]:border-b">
                                    <tr className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Immatriculation</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Marque/Modèle</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Type</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Places</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground">Statut</th>
                                        <th className="h-12 px-4 align-middle font-medium text-muted-foreground text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="[&_tr:last-child]:border-0">
                                    {data?.results.map((vehicle: Vehicle) => (
                                        <tr key={vehicle.id} className="border-b transition-colors hover:bg-muted/50">
                                            <td className="p-4 align-middle font-medium">{vehicle.registration_number}</td>
                                            <td className="p-4 align-middle">{vehicle.brand} {vehicle.model} ({vehicle.year})</td>
                                            <td className="p-4 align-middle capitalize">{vehicle.type}</td>
                                            <td className="p-4 align-middle">{vehicle.capacity}</td>
                                            <td className="p-4 align-middle">
                                                <span className={`px-2 py-1 rounded-full text-xs ${vehicle.status === 'active' ? 'bg-green-100 text-green-800' :
                                                    vehicle.status === 'maintenance' ? 'bg-yellow-100 text-yellow-800' :
                                                        'bg-red-100 text-red-800'
                                                    }`}>
                                                    {vehicle.status}
                                                </span>
                                            </td>
                                            <td className="p-4 align-middle text-right">
                                                <Button variant="ghost" size="icon" asChild>
                                                    <Link href={`/company/fleet/${vehicle.id}`}>
                                                        <Edit className="w-4 h-4" />
                                                    </Link>
                                                </Button>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="text-red-500 hover:text-red-700 hover:bg-red-50"
                                                    onClick={() => handleDelete(vehicle.id)}
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
