'use client';

import { useAuthStore } from '@/store/auth';
import { Button } from '@/components/ui/button';
import { authService } from '@/services/auth';
import { useRouter } from 'next/navigation';

export default function AdminDashboard() {
    const { logout } = useAuthStore();
    const router = useRouter();

    const handleLogout = async () => {
        await authService.logout();
        logout();
        router.push('/login');
    };

    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-4">Administration</h1>
            <p className="mb-4">Bienvenue, Administrateur !</p>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                    <h2 className="text-xl font-semibold mb-2">Utilisateurs</h2>
                    <p className="text-3xl font-bold">0</p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                    <h2 className="text-xl font-semibold mb-2">Compagnies</h2>
                    <p className="text-3xl font-bold">0</p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                    <h2 className="text-xl font-semibold mb-2">Voyages</h2>
                    <p className="text-3xl font-bold">0</p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                    <h2 className="text-xl font-semibold mb-2">Revenus Total</h2>
                    <p className="text-3xl font-bold">0 FCFA</p>
                </div>
            </div>
            <Button onClick={handleLogout} variant="destructive" className="mt-8">
                Se déconnecter
            </Button>
        </div>
    );
}
