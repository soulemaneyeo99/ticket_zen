'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/auth.store';
import { companyService } from '@/services/company.service';

interface CompanyStats {
    total_trips: number;
    total_revenue: number;
    average_occupancy: number;
    active_vehicles: number;
    total_bookings: number;
    active_trips: number;
}
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, TrendingUp, Users, Bus, Calendar, Plus, ArrowRight, DollarSign } from 'lucide-react';
import Link from 'next/link';

export default function CompanyDashboard() {
    const { user } = useAuthStore();
    const [stats, setStats] = useState<CompanyStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                // Mock stats for now - in production, get company ID from user context
                const mockStats: CompanyStats = {
                    total_trips: 45,
                    total_revenue: 12500000,
                    average_occupancy: 78,
                    active_vehicles: 12,
                    total_bookings: 320,
                    active_trips: 8
                };
                setStats(mockStats);
            } catch (error) {
                console.error('Error fetching stats:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    return (
        <div className="min-h-screen bg-gray-50 pb-20">
            {/* Header */}
            <div className="bg-white border-b border-gray-200 pt-8 pb-8 px-4">
                <div className="container mx-auto max-w-6xl">
                    <div className="flex justify-between items-center">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Tableau de bord</h1>
                            <p className="text-gray-500">Bienvenue, {user?.company_name || 'Compagnie'}</p>
                        </div>
                        <div className="flex space-x-4">
                            <Link href="/company/trips/new">
                                <Button className="bg-blue-600 hover:bg-blue-700">
                                    <Plus className="w-4 h-4 mr-2" /> Nouveau Voyage
                                </Button>
                            </Link>
                        </div>
                    </div>
                </div>
            </div>

            <div className="container mx-auto max-w-6xl px-4 py-8">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <StatCard
                        title="Revenu Total"
                        value={stats ? `${stats.total_revenue.toLocaleString()} FCFA` : '...'}
                        icon={<DollarSign className="w-6 h-6 text-green-600" />}
                        trend="+12% ce mois"
                        trendUp={true}
                    />
                    <StatCard
                        title="Réservations"
                        value={stats ? stats.total_bookings.toString() : '...'}
                        icon={<Users className="w-6 h-6 text-blue-600" />}
                        trend="+5% ce mois"
                        trendUp={true}
                    />
                    <StatCard
                        title="Voyages Actifs"
                        value={stats ? stats.active_trips.toString() : '...'}
                        icon={<Bus className="w-6 h-6 text-orange-600" />}
                        trend="2 en cours"
                        trendUp={true}
                    />
                    <StatCard
                        title="Taux de Remplissage"
                        value="78%"
                        icon={<TrendingUp className="w-6 h-6 text-purple-600" />}
                        trend="+2% vs hier"
                        trendUp={true}
                    />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Recent Activity / Bookings */}
                    <div className="lg:col-span-2 space-y-6">
                        <Card className="border-0 shadow-md">
                            <CardHeader className="flex flex-row items-center justify-between">
                                <div>
                                    <CardTitle>Réservations Récentes</CardTitle>
                                    <CardDescription>Les dernières transactions sur votre plateforme</CardDescription>
                                </div>
                                <Button variant="outline" size="sm">Voir tout</Button>
                            </CardHeader>
                            <CardContent>
                                {loading ? (
                                    <div className="flex justify-center py-8"><Loader2 className="w-8 h-8 animate-spin text-blue-600" /></div>
                                ) : (
                                    <div className="space-y-4">
                                        {[1, 2, 3, 4, 5].map((i) => (
                                            <div key={i} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                                <div className="flex items-center space-x-4">
                                                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center font-bold text-blue-600">
                                                        JK
                                                    </div>
                                                    <div>
                                                        <p className="font-bold text-gray-900">Jean Kouassi</p>
                                                        <p className="text-sm text-gray-500">Abidjan - Bouaké • 14:00</p>
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <p className="font-bold text-gray-900">15,000 FCFA</p>
                                                    <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50">Payé</Badge>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>

                    {/* Quick Actions & Status */}
                    <div className="space-y-6">
                        <Card className="border-0 shadow-md bg-blue-600 text-white">
                            <CardHeader>
                                <CardTitle>Actions Rapides</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <Link href="/company/trips/new" className="block">
                                    <div className="bg-white/10 hover:bg-white/20 p-4 rounded-lg cursor-pointer transition-colors flex items-center justify-between">
                                        <div className="flex items-center space-x-3">
                                            <Calendar className="w-5 h-5" />
                                            <span className="font-medium">Planifier un voyage</span>
                                        </div>
                                        <ArrowRight className="w-4 h-4" />
                                    </div>
                                </Link>
                                <Link href="/company/fleet/new" className="block">
                                    <div className="bg-white/10 hover:bg-white/20 p-4 rounded-lg cursor-pointer transition-colors flex items-center justify-between">
                                        <div className="flex items-center space-x-3">
                                            <Bus className="w-5 h-5" />
                                            <span className="font-medium">Ajouter un véhicule</span>
                                        </div>
                                        <ArrowRight className="w-4 h-4" />
                                    </div>
                                </Link>
                            </CardContent>
                        </Card>

                        <Card className="border-0 shadow-md">
                            <CardHeader>
                                <CardTitle>État de la Flotte</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-600">En service</span>
                                        <span className="font-bold text-green-600">12</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-600">En maintenance</span>
                                        <span className="font-bold text-orange-600">2</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-gray-600">Disponible</span>
                                        <span className="font-bold text-blue-600">5</span>
                                    </div>
                                    <div className="w-full bg-gray-200 h-2 rounded-full mt-2 overflow-hidden">
                                        <div className="bg-green-500 h-full w-[60%] float-left"></div>
                                        <div className="bg-orange-500 h-full w-[10%] float-left"></div>
                                        <div className="bg-blue-500 h-full w-[30%] float-left"></div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatCard({ title, value, icon, trend, trendUp }: { title: string, value: string, icon: React.ReactNode, trend: string, trendUp: boolean }) {
    return (
        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <p className="text-sm font-medium text-gray-500">{title}</p>
                        <h3 className="text-2xl font-bold text-gray-900 mt-1">{value}</h3>
                    </div>
                    <div className="p-2 bg-gray-50 rounded-lg">
                        {icon}
                    </div>
                </div>
                <div className={`text-xs font-medium ${trendUp ? 'text-green-600' : 'text-red-600'} flex items-center`}>
                    {trendUp ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingUp className="w-3 h-3 mr-1 rotate-180" />}
                    {trend}
                </div>
            </CardContent>
        </Card>
    );
}
