'use client';

import { useAuthStore } from '@/store/auth.store';
import { Button } from '@/components/ui/button';
import { authService } from '@/services/auth.service';
import { useRouter } from 'next/navigation';

export default function AgentDashboard() {
    const { user, logout } = useAuthStore();
    const router = useRouter();

    const handleLogout = async () => {
        await authService.logout();
        logout();
        router.push('/login');
    };

    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-4">Espace Embarqueur</h1>
            <p className="mb-4">Bienvenue, {user?.first_name} {user?.last_name} !</p>
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-2">Scanner QR Code</h2>
                <Button className="w-full py-8 text-lg">
                    Démarrer le scan
                </Button>
            </div>
            <Button onClick={handleLogout} variant="destructive" className="mt-8">
                Se déconnecter
            </Button>
        </div>
    );
}
