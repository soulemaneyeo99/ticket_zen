'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import { fleetService } from '@/services/fleet.service';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { Loader2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function NewVehiclePage() {
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();
    const { toast } = useToast();
    const { register, handleSubmit, setValue, formState: { errors } } = useForm();

    const onSubmit = async (data: any) => {
        setIsLoading(true);
        try {
            await fleetService.create(data);
            toast({ title: "Véhicule ajouté avec succès" });
            router.push('/company/fleet');
        } catch (error) {
            toast({ variant: "destructive", title: "Erreur lors de l'ajout" });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="p-8 max-w-2xl mx-auto">
            <Link href="/company/fleet" className="flex items-center text-gray-500 hover:text-gray-900 mb-6">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Retour à la flotte
            </Link>

            <Card>
                <CardHeader>
                    <CardTitle>Ajouter un véhicule</CardTitle>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Immatriculation</Label>
                                <Input {...register('registration_number', { required: 'Requis' })} placeholder="AB-123-CD" />
                                {errors.registration_number && <p className="text-sm text-red-500">Requis</p>}
                            </div>
                            <div className="space-y-2">
                                <Label>Type</Label>
                                <Select onValueChange={(val) => setValue('type', val)}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Choisir..." />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="bus">Bus (Gros porteur)</SelectItem>
                                        <SelectItem value="minibus">Minibus (Massa)</SelectItem>
                                        <SelectItem value="van">Van</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Marque</Label>
                                <Input {...register('brand', { required: 'Requis' })} />
                            </div>
                            <div className="space-y-2">
                                <Label>Modèle</Label>
                                <Input {...register('model', { required: 'Requis' })} />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Année</Label>
                                <Input type="number" {...register('year', { required: 'Requis', min: 1990 })} />
                            </div>
                            <div className="space-y-2">
                                <Label>Capacité (places)</Label>
                                <Input type="number" {...register('capacity', { required: 'Requis', min: 1 })} />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label>Équipements</Label>
                            <div className="flex gap-4">
                                <label className="flex items-center space-x-2">
                                    <input type="checkbox" {...register('has_ac')} className="rounded border-gray-300" />
                                    <span>Climatisation</span>
                                </label>
                                <label className="flex items-center space-x-2">
                                    <input type="checkbox" {...register('has_wifi')} className="rounded border-gray-300" />
                                    <span>WiFi</span>
                                </label>
                                <label className="flex items-center space-x-2">
                                    <input type="checkbox" {...register('has_usb')} className="rounded border-gray-300" />
                                    <span>Prises USB</span>
                                </label>
                            </div>
                        </div>

                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Enregistrement...
                                </>
                            ) : (
                                "Ajouter le véhicule"
                            )}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}
