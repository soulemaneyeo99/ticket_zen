'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { tripService, City } from '@/services/trip.service';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Calendar, MapPin, Search, Bus, Shield, Smartphone, Clock, CreditCard, CheckCircle } from 'lucide-react';
import Link from 'next/link';

export default function HomePage() {
    const router = useRouter();
    const [cities, setCities] = useState<City[]>([]);
    const { register, handleSubmit, setValue } = useForm();

    useEffect(() => {
        tripService.getCities().then(data => setCities(Array.isArray(data) ? data : (data as any).results || [])).catch(() => { });

        // Emergency cleanup: Check if we have a token but it's invalid (causing 400s)
        // For now, let's just ensure we start clean on the homepage if we're not explicitly logged in
        // actually, we don't want to log out valid users. 
        // But given the loop, let's trust the axios interceptor to handle the logout.
    }, []);

    const onSearch = (data: any) => {
        const params = new URLSearchParams();
        if (data.departure_city) params.set('departure_city', data.departure_city);
        if (data.arrival_city) params.set('arrival_city', data.arrival_city);
        if (data.date) params.set('date', data.date);

        router.push(`/trips/search?${params.toString()}`);
    };

    return (
        <div className="min-h-screen flex flex-col bg-gray-50">
            {/* Hero Section with Image Background */}
            <header className="relative h-[600px] flex items-center justify-center text-white overflow-hidden">
                {/* Background Image with Overlay */}
                <div className="absolute inset-0 z-0">
                    <img
                        src="/hero-bus.png"
                        alt="Voyage en bus Côte d'Ivoire"
                        className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-900/90 via-blue-800/80 to-transparent"></div>
                </div>

                <div className="relative z-10 container mx-auto px-4">
                    {/* Navigation */}
                    <nav className="absolute top-0 left-0 right-0 px-4 py-6">
                        <div className="container mx-auto flex justify-between items-center">
                            <div className="flex items-center space-x-2">
                                <div className="bg-white p-2 rounded-lg">
                                    <Bus className="w-6 h-6 text-blue-600" />
                                </div>
                                <span className="text-2xl font-bold text-white">Ticket Zen</span>
                            </div>
                            <div className="flex items-center space-x-4">
                                <Link href="/login">
                                    <Button variant="ghost" className="text-white hover:bg-white/20 hover:text-white">
                                        Connexion
                                    </Button>
                                </Link>
                                <Link href="/register">
                                    <Button className="bg-orange-500 hover:bg-orange-600 text-white border-none shadow-lg hover:shadow-orange-500/20 transition-all">
                                        S'inscrire
                                    </Button>
                                </Link>
                            </div>
                        </div>
                    </nav>

                    {/* Hero Content */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mt-20">
                        <div className="text-left space-y-6">
                            <div className="inline-block px-4 py-1 bg-orange-500/20 border border-orange-400/30 rounded-full backdrop-blur-sm">
                                <span className="text-orange-300 font-medium text-sm">✨ La référence du transport ivoirien</span>
                            </div>
                            <h1 className="text-5xl md:text-7xl font-bold leading-tight">
                                Votre voyage commence <span className="text-orange-400">ici</span>
                            </h1>
                            <p className="text-xl text-blue-100 max-w-xl leading-relaxed">
                                Réservez vos tickets de bus en toute simplicité vers toutes les destinations de Côte d'Ivoire. Rapide, sûr et fiable.
                            </p>
                            <div className="flex flex-wrap gap-4 pt-4">
                                <div className="flex items-center space-x-2 text-blue-200">
                                    <CheckCircle className="w-5 h-5 text-orange-400" />
                                    <span>Paiement Mobile Money</span>
                                </div>
                                <div className="flex items-center space-x-2 text-blue-200">
                                    <CheckCircle className="w-5 h-5 text-orange-400" />
                                    <span>Ticket 100% Digital</span>
                                </div>
                            </div>
                        </div>

                        {/* Search Form - Floating Card */}
                        <Card className="bg-white/95 backdrop-blur-md shadow-2xl border-0 rounded-2xl overflow-hidden transform hover:scale-[1.01] transition-transform duration-300">
                            <div className="bg-blue-600 p-4 text-white text-center">
                                <h3 className="font-bold text-lg">Réserver un trajet</h3>
                            </div>
                            <CardContent className="p-6 md:p-8">
                                <form onSubmit={handleSubmit(onSearch)} className="space-y-5">
                                    <div className="space-y-2">
                                        <Label className="text-gray-700 font-semibold flex items-center">
                                            <MapPin className="w-4 h-4 mr-2 text-blue-600" />
                                            Ville de départ
                                        </Label>
                                        <Select onValueChange={(val) => setValue('departure_city', val)}>
                                            <SelectTrigger className="h-12 bg-gray-50 border-gray-200 focus:ring-2 focus:ring-blue-500 transition-all">
                                                <SelectValue placeholder="D'où partez-vous ?" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {cities.map(city => (
                                                    <SelectItem key={city.id} value={city.id.toString()}>{city.name}</SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>

                                    <div className="space-y-2">
                                        <Label className="text-gray-700 font-semibold flex items-center">
                                            <MapPin className="w-4 h-4 mr-2 text-orange-500" />
                                            Ville d'arrivée
                                        </Label>
                                        <Select onValueChange={(val) => setValue('arrival_city', val)}>
                                            <SelectTrigger className="h-12 bg-gray-50 border-gray-200 focus:ring-2 focus:ring-blue-500 transition-all">
                                                <SelectValue placeholder="Où allez-vous ?" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {cities.map(city => (
                                                    <SelectItem key={city.id} value={city.id.toString()}>{city.name}</SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>

                                    <div className="space-y-2">
                                        <Label className="text-gray-700 font-semibold flex items-center">
                                            <Calendar className="w-4 h-4 mr-2 text-blue-600" />
                                            Date de départ
                                        </Label>
                                        <Input
                                            type="date"
                                            {...register('date')}
                                            className="h-12 bg-gray-50 border-gray-200 focus:ring-2 focus:ring-blue-500 transition-all"
                                        />
                                    </div>

                                    <Button type="submit" className="w-full h-14 bg-blue-600 hover:bg-blue-700 text-white font-bold text-lg shadow-lg hover:shadow-blue-600/30 transition-all rounded-xl mt-4">
                                        <Search className="w-5 h-5 mr-2" />
                                        Rechercher mon billet
                                    </Button>
                                </form>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </header>

            {/* Features Section - Modern Cards */}
            <section className="py-20 px-4">
                <div className="container mx-auto max-w-6xl">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold text-gray-900 mb-4">Pourquoi choisir Ticket Zen ?</h2>
                        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                            La plateforme de réservation de tickets la plus moderne et sécurisée de Côte d'Ivoire
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <FeatureCard
                            icon={<Clock className="w-12 h-12 text-blue-600" />}
                            title="Rapide et Simple"
                            description="Réservez votre ticket en moins de 2 minutes sans vous déplacer. Interface intuitive et processus optimisé."
                            gradient="from-blue-50 to-blue-100/50"
                        />
                        <FeatureCard
                            icon={<Shield className="w-12 h-12 text-green-600" />}
                            title="Paiement Sécurisé"
                            description="Payez en toute sécurité via Mobile Money ou Carte Bancaire. Vos données sont protégées."
                            gradient="from-green-50 to-green-100/50"
                        />
                        <FeatureCard
                            icon={<Smartphone className="w-12 h-12 text-purple-600" />}
                            title="Ticket Numérique"
                            description="Recevez votre ticket par SMS et Email avec QR code. Plus besoin d'imprimer !"
                            gradient="from-purple-50 to-purple-100/50"
                        />
                    </div>
                </div>
            </section>

            {/* How It Works Section */}
            <section className="py-20 px-4 bg-gradient-to-br from-blue-50 to-white">
                <div className="container mx-auto max-w-6xl">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold text-gray-900 mb-4">Comment ça marche ?</h2>
                        <p className="text-xl text-gray-600">Simple, rapide et efficace</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                        <StepCard number="1" title="Recherchez" description="Sélectionnez votre trajet et la date" />
                        <StepCard number="2" title="Choisissez" description="Comparez les horaires et prix" />
                        <StepCard number="3" title="Payez" description="Paiement sécurisé en ligne" />
                        <StepCard number="4" title="Voyagez" description="Présentez votre QR code" />
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 text-white py-12 px-4 mt-auto">
                <div className="container mx-auto max-w-6xl">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
                        <div>
                            <div className="flex items-center space-x-2 mb-4">
                                <Bus className="w-6 h-6" />
                                <span className="text-xl font-bold">Ticket Zen</span>
                            </div>
                            <p className="text-gray-400">La billetterie digitale pour vos voyages en Côte d'Ivoire.</p>
                        </div>
                        <div>
                            <h3 className="font-semibold mb-4">Liens rapides</h3>
                            <ul className="space-y-2 text-gray-400">
                                <li><Link href="/about" className="hover:text-white transition-colors">À propos</Link></li>
                                <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
                                <li><Link href="/faq" className="hover:text-white transition-colors">FAQ</Link></li>
                            </ul>
                        </div>
                        <div>
                            <h3 className="font-semibold mb-4">Pour les compagnies</h3>
                            <ul className="space-y-2 text-gray-400">
                                <li><Link href="/register" className="hover:text-white transition-colors">Devenir partenaire</Link></li>
                                <li><Link href="/company" className="hover:text-white transition-colors">Espace compagnie</Link></li>
                            </ul>
                        </div>
                        <div>
                            <h3 className="font-semibold mb-4">Support</h3>
                            <ul className="space-y-2 text-gray-400">
                                <li><Link href="/help" className="hover:text-white transition-colors">Centre d'aide</Link></li>
                                <li><Link href="/terms" className="hover:text-white transition-colors">Conditions</Link></li>
                                <li><Link href="/privacy" className="hover:text-white transition-colors">Confidentialité</Link></li>
                            </ul>
                        </div>
                    </div>
                    <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
                        <p>&copy; 2024 Ticket Zen. Tous droits réservés.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}

function FeatureCard({ icon, title, description, gradient }: {
    icon: React.ReactNode,
    title: string,
    description: string,
    gradient: string
}) {
    return (
        <Card className={`text-center hover:shadow-2xl transition-all duration-300 border-0 bg-gradient-to-br ${gradient} group hover:-translate-y-2`}>
            <CardHeader>
                <div className="mb-4 flex justify-center group-hover:scale-110 transition-transform duration-300">
                    {icon}
                </div>
                <CardTitle className="text-xl font-bold text-gray-900">{title}</CardTitle>
            </CardHeader>
            <CardContent>
                <CardDescription className="text-base text-gray-600 leading-relaxed">{description}</CardDescription>
            </CardContent>
        </Card>
    );
}

function StepCard({ number, title, description }: { number: string, title: string, description: string }) {
    return (
        <div className="text-center">
            <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4 shadow-lg">
                {number}
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
            <p className="text-gray-600">{description}</p>
        </div>
    );
}
