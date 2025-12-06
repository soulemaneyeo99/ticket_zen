'use client';

import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/hooks/use-auth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
    TrendingUp,
    Users,
    Bus,
    Calendar,
    Plus,
    ArrowRight,
    DollarSign,
    Activity
} from 'lucide-react';
import Link from 'next/link';


interface CompanyStats {
    total_trips: number;
    total_revenue: number;
    total_bookings: number;
    active_trips: number;
    active_vehicles: number;
    average_occupancy: number;
}

export default function CompanyDashboard() {
    const { user } = useAuth();

    // Mock stats query - remplacer par vrai endpoint
    const { data: stats, isLoading } = useQuery({
        queryKey: ['company-stats'],
        queryFn: () => Promise.resolve<CompanyStats>({
            total_trips: 45,
            total_revenue: 12500000,
            total_bookings: 320,
            active_trips: 8,
            active_vehicles: 12,
            average_occupancy: 78,
        }),
    });

    return (
        <div className="min-h-screen bg-slate-50">
            {/* Header */}
            <header className="bg-white border-b px-6 py-8">
                <div className="max-w-7xl mx-auto">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-slate-900">Tableau de bord</h1>
                            <p className="text-gray-500">Bienvenue, {user?.first_name} {user?.last_name}</p>
                        </div>
                        <div className="flex gap-3">
                            <Link href="/company/trips/new">
                                <Button className="bg-blue-600 hover:bg-blue-700">
                                    <Plus className="w-4 h-4 mr-2" /> Nouveau Voyage
                                </Button>
                            </Link>
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    {isLoading ? (
                        <>
                            {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-32 rounded-xl" />)}
                        </>
                    ) : (
                        <>
                            <MetricCard
                                title="Revenu Total"
                                value={`${stats?.total_revenue.toLocaleString()} FCFA`}
                                icon={<DollarSign className="w-6 h-6" />}
                                trend="+12% ce mois"
                                trendUp
                                color="green"
                            />
                            <MetricCard
                                title="Réservations"
                                value={stats?.total_bookings || 0}
                                icon={<Users className="w-6 h-6" />}
                                trend="+5% ce mois"
                                trendUp
                                color="blue"
                            />
                            <MetricCard
                                title="Voyages Actifs"
                                value={stats?.active_trips || 0}
                                icon={<Bus className="w-6 h-6" />}
                                trend="2 en cours"
                                trendUp
                                color="amber"
                            />
                            <MetricCard
                                title="Taux de Remplissage"
                                value={`${stats?.average_occupancy}%`}
                                icon={<TrendingUp className="w-6 h-6" />}
                                trend="+2% vs hier"
                                trendUp
                                color="purple"
                            />
                        </>
                    )}
                </div>

                <div className="grid lg:grid-cols-3 gap-8">
                    {/* Recent Bookings */}
                    <div className="lg:col-span-2">
                        <Card className="border-0 shadow-md">
                            <CardHeader className="flex flex-row items-center justify-between pb-4">
                                <CardTitle className="text-xl">Réservations Récentes</CardTitle>
                                <Button variant="ghost" size="sm">Voir tout</Button>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {[1, 2, 3, 4, 5].map(i => (
                                        <BookingRow key={i} />
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Quick Actions & Fleet Status */}
                    <div className="space-y-6">
                        <Card className="border-0 shadow-md bg-gradient-to-br from-blue-600 to-blue-700 text-white">
                            <CardHeader>
                                <CardTitle className="text-xl">Actions Rapides</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <QuickAction
                                    icon={<Calendar className="w-5 h-5" />}
                                    label="Planifier un voyage"
                                    href="/company/trips/new"
                                />
                                <QuickAction
                                    icon={<Bus className="w-5 h-5" />}
                                    label="Ajouter un véhicule"
                                    href="/company/fleet/new"
                                />
                                <QuickAction
                                    icon={<Activity className="w-5 h-5" />}
                                    label="Voir les statistiques"
                                    href="/company/analytics"
                                />
                            </CardContent>
                        </Card>

                        <Card className="border-0 shadow-md">
                            <CardHeader>
                                <CardTitle className="text-xl">État de la Flotte</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <FleetStatus label="En service" value={12} color="green" />
                                    <FleetStatus label="En maintenance" value={2} color="amber" />
                                    <FleetStatus label="Disponible" value={5} color="blue" />

                                    <div className="w-full bg-slate-200 h-2 rounded-full mt-4 overflow-hidden">
                                        <div className="flex h-full">
                                            <div className="bg-green-500 w-[60%]" />
                                            <div className="bg-amber-500 w-[10%]" />
                                            <div className="bg-blue-500 w-[30%]" />
                                        </div>
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

// ============= SUB-COMPONENTS =============

function MetricCard({ title, value, icon, trend, trendUp, color }: {
    title: string;
    value: string | number;
    icon: React.ReactNode;
    trend: string;
    trendUp: boolean;
    color: 'green' | 'blue' | 'amber' | 'purple';
}) {
    const colorClasses = {
        green: 'text-green-600 bg-green-50',
        blue: 'text-blue-600 bg-blue-50',
        amber: 'text-amber-600 bg-amber-50',
        purple: 'text-purple-600 bg-purple-50',
    };

    return (
        <Card className="border-0 shadow-sm hover:shadow-md transition-shadow">
            <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <p className="text-sm font-medium text-slate-500">{title}</p>
                        <h3 className="text-2xl font-bold text-slate-900 mt-1">{value}</h3>
                    </div>
                    <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
                        {icon}
                    </div>
                </div>
                <div className={`text-xs font-medium flex items-center ${trendUp ? 'text-green-600' : 'text-red-600'}`}>
                    <TrendingUp className={`w-3 h-3 mr-1 ${!trendUp && 'rotate-180'}`} />
                    {trend}
                </div>
            </CardContent>
        </Card>
    );
}

function BookingRow() {
    return (
        <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors">
            <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center font-bold text-blue-600">
                    JK
                </div>
                <div>
                    <p className="font-bold text-slate-900">Jean Kouassi</p>
                    <p className="text-sm text-slate-500">Abidjan - Bouaké • 14:00</p>
                </div>
            </div>
            <div className="text-right">
                <p className="font-bold text-slate-900">15,000 FCFA</p>
                <Badge className="bg-green-100 text-green-700 border-0">Payé</Badge>
            </div>
        </div>
    );
}

function QuickAction({ icon, label, href }: { icon: React.ReactNode; label: string; href: string }) {
    return (
        <Link href={href}>
            <div className="bg-white/10 hover:bg-white/20 p-4 rounded-lg cursor-pointer transition-all flex items-center justify-between group">
                <div className="flex items-center gap-3">
                    {icon}
                    <span className="font-medium">{label}</span>
                </div>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
        </Link>
    );
}

function FleetStatus({ label, value, color }: { label: string; value: number; color: 'green' | 'amber' | 'blue' }) {
    const colorClasses = {
        green: 'text-green-600',
        amber: 'text-amber-600',
        blue: 'text-blue-600'
    };

    return (
        <div className="flex justify-between items-center">
            <span className="text-slate-600">{label}</span>
            <span className={`font-bold ${colorClasses[color]}`}>{value}</span>
        </div>
    );
}