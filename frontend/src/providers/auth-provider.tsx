'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/store/auth';
import { authService } from '@/services/auth';

export default function AuthProvider({ children }: { children: React.ReactNode }) {
    const { user, setAuth, logout } = useAuthStore();

    useEffect(() => {
        // Restaurer la session au mount (via refresh token dans cookie HttpOnly)
        const restoreSession = async () => {
            // Si déjà authentifié dans le store, skip
            if (user) return;

            try {
                // Tenter de refresh via le cookie HttpOnly
                const { data } = await fetch('/api/auth/refresh', { method: 'POST' }).then(r => r.json());

                if (data?.access) {
                    // Récupérer les infos user avec le nouveau token
                    const currentUser = await authService.getCurrentUser();
                    setAuth(currentUser, data.access, data.refresh);
                }
            } catch {
                // Pas de session valide, continuer en guest
                logout();
            }
        };

        restoreSession();
    }, [user, setAuth, logout]);

    // Écouter les événements de logout
    useEffect(() => {
        const handleLogout = () => logout();
        window.addEventListener('auth:logout', handleLogout);
        return () => window.removeEventListener('auth:logout', handleLogout);
    }, [logout]);

    return <>{children}</>;
}