'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { apiGet } from '@/lib/api';
import { City } from '@/types/api';
import { Button } from '@/components/ui/button';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Calendar, MapPin, Bus, Shield, Smartphone, Menu, X } from 'lucide-react';
import Link from 'next/link';
import { format } from 'date-fns';
import { useAuthStore } from '@/store/auth';

const searchSchema = z.object({
    departure_city: z.string().min(1, 'Ville de départ requise'),
    arrival_city: z.string().min(1, "Ville d'arrivée requise"),
    date: z.string().min(1, 'Date requise'),
});

type SearchForm = z.infer<typeof searchSchema>;

export default function HomePage() {
    const router = useRouter();
    const { isAuthenticated, user, logout } = useAuthStore();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const {
        register,
        control,
        handleSubmit,
        formState: { errors },
    } = useForm<SearchForm>({
        resolver: zodResolver(searchSchema),
        defaultValues: { date: format(new Date(), 'yyyy-MM-dd') },
    });

    // Fetch cities with React Query
    const { data: cities = [], isLoading: citiesLoading } = useQuery({
        queryKey: ['cities'],
        queryFn: () => apiGet<City[]>('/cities/'),
    });

    console.log('Cities loaded:', cities.length, cities);

    const onSearch = (data: SearchForm) => {
        const params = new URLSearchParams({
            departure_city: data.departure_city,
            arrival_city: data.arrival_city,
            date: data.date,
        });
        router.push(`/trips/search?${params}`);
    };

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col">
            {/* Navbar */}
            <nav className="bg-slate-900 text-white py-4 px-4 sticky top-0 z-50 shadow-md">
                <div className="container mx-auto flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <div className="bg-amber-500 p-1.5 rounded-lg">
                            <Bus className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-xl font-bold tracking-tight">Ticket Zen</span>
                    </div>

                    <div className="hidden md:flex gap-4 items-center">
                        {isAuthenticated ? (
                            <div className="flex items-center gap-4">
                                <span className="text-sm text-slate-300">Bonjour, {user?.first_name}</span>
                                <Button variant="ghost" onClick={() => logout()} className="text-white hover:text-amber-400">Déconnexion</Button>
                            </div>
                        ) : (
                            <>
                                <Link href="/login">
                                    <Button variant="ghost" className="text-white hover:text-amber-400">
                                        Connexion
                                    </Button>
                                </Link>
                                <Link href="/register">
                                    <Button className="bg-amber-500 hover:bg-amber-600 text-slate-900 font-semibold">
                                        S'inscrire
                                    </Button>
                                </Link>
                            </>
                        )}
                    </div>

                    <Button
                        variant="ghost"
                        size="icon"
                        className="md:hidden text-white"
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                    >
                        {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                    </Button>
                </div>

                {/* Mobile Menu */}
                {mobileMenuOpen && (
                    <div className="md:hidden mt-4 pb-4 border-t border-slate-700 pt-4 space-y-3">
                        {isAuthenticated ? (
                            <>
                                <div className="text-sm text-slate-300 px-2">Bonjour, {user?.first_name}</div>
                                <Button
                                    variant="ghost"
                                    onClick={() => {
                                        logout();
                                        setMobileMenuOpen(false);
                                    }}
                                    className="w-full text-white hover:text-amber-400 justify-start"
                                >
                                    Déconnexion
                                </Button>
                            </>
                        ) : (
                            <>
                                <Link href="/login" onClick={() => setMobileMenuOpen(false)}>
                                    <Button variant="ghost" className="w-full text-white hover:text-amber-400 justify-start">
                                        Connexion
                                    </Button>
                                </Link>
                                <Link href="/register" onClick={() => setMobileMenuOpen(false)}>
                                    <Button className="w-full bg-amber-500 hover:bg-amber-600 text-slate-900 font-semibold">
                                        S'inscrire
                                    </Button>
                                </Link>
                            </>
                        )}
                    </div>
                )}
            </nav>

            {/* Hero Section */}
            <div className="relative bg-slate-900 pb-24 pt-12 px-4 overflow-hidden">
                {/* Abstract Background */}
                <div className="absolute inset-0 overflow-hidden">
                    <div className="absolute -top-24 -right-24 w-96 h-96 bg-blue-600 rounded-full blur-3xl opacity-20"></div>
                    <div className="absolute top-1/2 -left-24 w-72 h-72 bg-amber-500 rounded-full blur-3xl opacity-10"></div>
                </div>

                <div className="container mx-auto max-w-5xl relative z-10">
                    <div className="text-center max-w-2xl mx-auto mb-12">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-amber-400 text-sm font-medium mb-6">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                            </span>
                            Nouveau: Paiement Wave disponible
                        </div>
                        <h1 className="text-4xl md:text-6xl font-bold text-white leading-tight mb-6">
                            Voyagez en toute <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-500">Confiance</span>
                        </h1>
                        <p className="text-lg text-slate-300">
                            La plateforme de référence pour vos trajets interurbains en Côte d'Ivoire. Simple, rapide et sécurisé.
                        </p>
                    </div>

                    {/* Search Card - Floating */}
                    <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 max-w-4xl mx-auto transform translate-y-8 border border-slate-100">
                        <form onSubmit={handleSubmit(onSearch)} className="grid md:grid-cols-12 gap-4 items-end">

                            {/* Departure */}
                            <div className="md:col-span-4 space-y-2">
                                <label className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                                    <MapPin className="w-4 h-4 text-blue-600" /> Départ
                                </label>
                                <Controller
                                    control={control}
                                    name="departure_city"
                                    render={({ field }) => (
                                        <Select onValueChange={field.onChange} value={field.value}>
                                            <SelectTrigger className="h-12 bg-slate-50 border-slate-200 focus:ring-blue-500">
                                                <SelectValue placeholder="Ville de départ" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {cities.map((city) => (
                                                    <SelectItem key={city.id} value={city.id.toString()}>
                                                        {city.name}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    )}
                                />
                                {errors.departure_city && <p className="text-xs text-red-500">{errors.departure_city.message}</p>}
                            </div>

                            {/* Arrival */}
                            <div className="md:col-span-4 space-y-2">
                                <label className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                                    <MapPin className="w-4 h-4 text-amber-500" /> Arrivée
                                </label>
                                <Controller
                                    control={control}
                                    name="arrival_city"
                                    render={({ field }) => (
                                        <Select onValueChange={field.onChange} value={field.value}>
                                            <SelectTrigger className="h-12 bg-slate-50 border-slate-200 focus:ring-blue-500">
                                                <SelectValue placeholder="Ville d'arrivée" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {cities.map((city) => (
                                                    <SelectItem key={city.id} value={city.id.toString()}>
                                                        {city.name}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    )}
                                />
                                {errors.arrival_city && <p className="text-xs text-red-500">{errors.arrival_city.message}</p>}
                            </div>

                            {/* Date */}
                            <div className="md:col-span-2 space-y-2">
                                <label className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                                    <Calendar className="w-4 h-4 text-slate-500" /> Date
                                </label>
                                <input
                                    type="date"
                                    {...register('date')}
                                    className="w-full h-12 px-3 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                />
                                {errors.date && <p className="text-xs text-red-500">{errors.date.message}</p>}
                            </div>

                            {/* Submit */}
                            <div className="md:col-span-2">
                                <Button type="submit" className="w-full h-12 bg-amber-500 hover:bg-amber-600 text-slate-900 font-bold">
                                    Rechercher
                                </Button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            {/* Features / Trust Section */}
            <div className="bg-slate-50 pt-32 pb-16 px-4 flex-grow">
                <div className="container mx-auto max-w-6xl">
                    <div className="grid md:grid-cols-3 gap-8">
                        {[
                            { icon: Shield, title: "Paiement Sécurisé", desc: "Transactions cryptées et validées par les opérateurs." },
                            { icon: Smartphone, title: "E-Ticket Instantané", desc: "Recevez votre billet par SMS et QR Code immédiatement." },
                            { icon: Bus, title: "Meilleures Compagnies", desc: "Partenariat officiel avec les transporteurs leaders." },
                        ].map((item, i) => (
                            <div key={i} className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col items-center text-center">
                                <div className="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center mb-4">
                                    <item.icon className="w-6 h-6 text-blue-600" />
                                </div>
                                <h3 className="font-bold text-slate-900 mb-2">{item.title}</h3>
                                <p className="text-slate-500 text-sm">{item.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Footer */}
            <footer className="bg-slate-900 text-slate-400 py-8 text-center text-sm">
                <p>&copy; {new Date().getFullYear()} Ticket Zen. Tous droits réservés.</p>
            </footer>
        </div>
    );
}