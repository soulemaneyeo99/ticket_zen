'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import { tripsService } from '@/services/trips';
import { City } from '@/types/api';
import { fleetService, Vehicle } from '@/services/fleet.service';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Loader2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function NewTripPage() {
    const [isLoading, setIsLoading] = useState(false);
    const [cities, setCities] = useState<City[]>([]);
    const [vehicles, setVehicles] = useState<Vehicle[]>([]);

    const router = useRouter();
    const { register, handleSubmit, setValue } = useForm();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [citiesData, vehiclesData] = await Promise.all([
                    tripsService.getCities(),
                    fleetService.getAll()
                ]);
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                setCities(Array.isArray(citiesData) ? citiesData : (citiesData as any).results || []);
                setVehicles(vehiclesData.results || []);
            } catch (error) {
                void error;
                toast.error("Erreur de chargement des données");
            }
        };
        fetchData();
    }, []);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const onSubmit = async (data: any) => {
        setIsLoading(true);
        try {
            await tripsService.create(data);
            toast.success("Voyage créé avec succès");
            router.push('/company/trips');
        } catch (error) {
            void error; // Mark as used
            toast.error("Erreur lors de la création");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="p-8 max-w-2xl mx-auto">
            <Link href="/company/trips" className="flex items-center text-gray-500 hover:text-gray-900 mb-6">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Retour aux voyages
            </Link>

            <Card>
                <CardHeader>
                    <CardTitle>Programmer un voyage</CardTitle>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Ville de départ</Label>
                                <Select onValueChange={(val) => setValue('departure_city', val)}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Choisir..." />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {cities.map(city => (
                                            <SelectItem key={city.id} value={city.id.toString()}>{city.name}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-2">
                                <Label>Ville d&apos;arrivée</Label>
                                <Select onValueChange={(val) => setValue('arrival_city', val)}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Choisir..." />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {cities.map(city => (
                                            <SelectItem key={city.id} value={city.id.toString()}>{city.name}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Date et Heure de départ</Label>
                                <Input type="datetime-local" {...register('departure_time', { required: 'Requis' })} />
                            </div>
                            <div className="space-y-2">
                                <Label>Date et Heure d&apos;arrivée (estimée)</Label>
                                <Input type="datetime-local" {...register('arrival_time', { required: 'Requis' })} />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label>Véhicule</Label>
                            <Select onValueChange={(val) => setValue('vehicle', val)}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Choisir un véhicule..." />
                                </SelectTrigger>
                                <SelectContent>
                                    {vehicles.map(vehicle => (
                                        <SelectItem key={vehicle.id} value={vehicle.id.toString()}>
                                            {vehicle.brand} {vehicle.model} - {vehicle.registration_number} ({vehicle.capacity} places)
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label>Prix du ticket (FCFA)</Label>
                            <Input type="number" {...register('price', { required: 'Requis', min: 0 })} />
                        </div>

                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Création...
                                </>
                            ) : (
                                "Programmer le voyage"
                            )}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
