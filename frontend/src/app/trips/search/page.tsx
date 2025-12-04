'use client';

import { Suspense, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { tripsService } from '@/services/trips';
import { TripCard } from '@/components/features/TripCard';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { ArrowLeft, SlidersHorizontal, Bus } from 'lucide-react';
import Link from 'next/link';
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from '@/components/ui/sheet';

function SearchResults() {
    const searchParams = useSearchParams();
    const departureCityId = Number(searchParams.get('departure_city'));
    const arrivalCityId = Number(searchParams.get('arrival_city'));
    const date = searchParams.get('date') || '';

    const { data, isLoading, isError } = useQuery({
        queryKey: ['trips', departureCityId, arrivalCityId, date],
        queryFn: () =>
            tripsService.search({
                departure_city: departureCityId,
                arrival_city: arrivalCityId,
                date,
            }),
        enabled: !!departureCityId && !!arrivalCityId && !!date,
    });

    if (isLoading) {
        return (
            <div className="space-y-4">
                {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="bg-white p-4 rounded-xl border border-slate-100 space-y-3">
                        <div className="flex justify-between">
                            <Skeleton className="h-10 w-10 rounded-full" />
                            <Skeleton className="h-6 w-24" />
                        </div>
                        <div className="flex justify-between items-center">
                            <Skeleton className="h-8 w-20" />
                            <Skeleton className="h-px w-20" />
                            <Skeleton className="h-8 w-20" />
                        </div>
                        <Skeleton className="h-10 w-full rounded-lg" />
                    </div>
                ))}
            </div>
        );
    }

    if (isError) {
        return (
            <div className="text-center py-12">
                <p className="text-red-500">Une erreur est survenue lors du chargement des voyages.</p>
            </div>
        )
    }

    if (!data?.results?.length) {
        return (
            <div className="text-center py-16 px-4">
                <div className="bg-slate-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Bus className="w-10 h-10 text-slate-400" />
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-2">Aucun voyage trouvé</h3>
                <p className="text-slate-500 max-w-xs mx-auto">
                    Désolé, nous n'avons pas trouvé de voyages pour cette date. Essayez de changer vos critères.
                </p>
                <Button className="mt-6" variant="outline" asChild>
                    <Link href="/">Nouvelle recherche</Link>
                </Button>
            </div>
        );
    }

    return (
        <div className="space-y-4 pb-20">
            <div className="text-sm text-slate-500 mb-2 font-medium">
                {data.count} voyages trouvés
            </div>
            {data.results.map((trip) => (
                <TripCard key={trip.id} trip={trip} />
            ))}
        </div>
    );
}

export default function SearchPage() {
    return (
        <div className="min-h-screen bg-slate-50">
            {/* Header */}
            <div className="bg-white border-b sticky top-0 z-20 px-4 py-3 shadow-sm">
                <div className="container mx-auto max-w-2xl flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Link
                            href="/"
                            className="p-2 -ml-2 hover:bg-slate-100 rounded-full transition-colors"
                        >
                            <ArrowLeft className="w-5 h-5 text-slate-700" />
                        </Link>
                        <div>
                            <h1 className="font-bold text-slate-900 text-lg leading-tight">
                                Résultats
                            </h1>
                            <p className="text-xs text-slate-500">Abidjan → Bouaké • 12 Oct</p>
                        </div>
                    </div>

                    <Sheet>
                        <SheetTrigger asChild>
                            <Button variant="ghost" size="icon" className="text-slate-700">
                                <SlidersHorizontal className="w-5 h-5" />
                            </Button>
                        </SheetTrigger>
                        <SheetContent>
                            <SheetHeader>
                                <SheetTitle>Filtres</SheetTitle>
                                <SheetDescription>Affinez votre recherche</SheetDescription>
                            </SheetHeader>
                            <div className="py-6 space-y-6">
                                {/* Placeholder for filters */}
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Prix</label>
                                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                                        <div className="h-full w-1/2 bg-blue-600"></div>
                                    </div>
                                    <div className="flex justify-between text-xs text-slate-500">
                                        <span>5000F</span>
                                        <span>25000F</span>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Compagnies</label>
                                    <div className="space-y-2">
                                        {['UTB', 'AHT', 'SOTRA'].map(c => (
                                            <div key={c} className="flex items-center gap-2">
                                                <div className="w-4 h-4 border rounded bg-blue-600 border-blue-600 flex items-center justify-center">
                                                    <div className="w-2 h-2 bg-white rounded-sm"></div>
                                                </div>
                                                <span className="text-sm">{c}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <Button className="w-full bg-blue-900 text-white">Appliquer</Button>
                            </div>
                        </SheetContent>
                    </Sheet>
                </div>
            </div>

            {/* Results */}
            <div className="container max-w-2xl mx-auto p-4">
                <Suspense fallback={<Skeleton className="h-40 w-full rounded-xl" />}>
                    <SearchResults />
                </Suspense>
            </div>
        </div>
    );
}