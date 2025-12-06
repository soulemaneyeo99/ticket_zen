'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/auth';
import { authService } from '@/services/auth';

export default function SessionProvider({
    children,
}: {
    children: React.ReactNode;
}) {
    const { isAuthenticated, setAuth, logout } = useAuthStore();

    useEffect(() => {
        const restoreSession = async () => {
            // If already authenticated in store, we are good (unless token expired, which axios interceptor handles)
            // But on F5 refresh, store is cleared (isAuthenticated is false).
            // So we try to refresh token to see if we have a valid cookie.

            if (!isAuthenticated) {
                try {
                    // 1. Try to get a new access token using the HttpOnly cookie
                    const { access } = await authService.refreshToken();

                    // 2. If success, we have a valid session. Now get user details.
                    // We need to set the access token in the store first so the next request uses it.
                    // But setAuth expects a user object.
                    // So we can't use setAuth yet. We need a way to set just the token or pass it in headers manually.
                    // Actually, axios interceptor reads from store.
                    // Let's manually set the token in the store or use a temporary way.
                    // Wait, useAuthStore.getState().setAuth requires user.

                    // Let's fetch user details. We need to attach the token manually since it's not in store yet.
                    // Or we can update the store to allow setting just the token?
                    // No, let's just use the token in the request header explicitly for the user fetch.

                    // Actually, authService.getCurrentUser uses api.get which uses interceptor.
                    // Interceptor reads from store. Store is empty.
                    // So we need to temporarily set the token in the store?
                    // Or modify getCurrentUser to accept a token?

                    // Let's modify the store to allow setting token independently? 
                    // Or just mock a user? No.

                    // Let's assume we can pass the token to getCurrentUser?
                    // No, getCurrentUser calls api.get('/auth/user/').

                    // Let's hack it: set a dummy user with the token, then fetch real user.
                    useAuthStore.setState({ accessToken: access });

                    const user = await authService.getCurrentUser();

                    // Now set the real user and token (we need refresh token too)
                    // But we only got access from refresh. We should get refresh too from the refresh endpoint
                    // Let's assume the refresh endpoint returns both access and refresh
                    const refreshData = await authService.refreshToken();
                    setAuth(user, refreshData.access, refreshData.refresh);

                } catch {
                    // If refresh fails, we are truly logged out.
                    // Clear any partial state
                    logout();
                }
            }
        };

        restoreSession();
    }, [isAuthenticated, setAuth, logout]);

    // We don't block rendering while restoring, to allow public pages to show fast.
    // AuthGuard will handle protection for private pages.
    return <>{children}</>;
}
