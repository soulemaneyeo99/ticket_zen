'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/auth.store';
import { authService } from '@/services/auth.service';
import { usePathname } from 'next/navigation';

export default function AuthProvider({ children }: { children: React.ReactNode }) {
    const { setAuth, logout, isAuthenticated } = useAuthStore();
    const pathname = usePathname();
    const [isRestoring, setIsRestoring] = useState(true);

    useEffect(() => {
        const initAuth = async () => {
            // If already authenticated, we don't need to restore
            if (isAuthenticated) {
                setIsRestoring(false);
                return;
            }

            try {
                // 1. Try to refresh token using HttpOnly cookie
                const { access } = await authService.refreshToken();

                // 2. Temporarily set access token in store so axios interceptor can use it
                useAuthStore.setState({ accessToken: access });

                // 3. Fetch user details
                const user = await authService.getCurrentUser();

                // 4. Update store with user and token
                setAuth(user, access);
            } catch (error) {
                // If refresh fails, we are truly logged out
                logout();
                // We do NOT redirect here. We let the page load as guest.
                // Protected pages should be wrapped in a specific AuthGuard or handled by middleware.
            } finally {
                setIsRestoring(false);
            }
        };

        initAuth();
    }, [isAuthenticated, setAuth, logout]);

    // Optional: Show a loading spinner only if we are on a protected route?
    // For now, we render children immediately to avoid blocking UI, 
    // but we might show a small indicator or just let the content load.
    // If we block, the user sees a white screen.

    return <>{children}</>;
}
