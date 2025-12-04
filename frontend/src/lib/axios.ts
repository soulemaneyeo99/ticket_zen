import axios from 'axios';

const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
    baseURL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true, // Important for cookies if we used them directly, but we use proxy
});

// Interceptor to add token from client-side storage (if we store access token in memory/local storage)
// Or if we use the Next.js proxy, the proxy handles the token injection.
// For this architecture, we'll store the access token in memory (Zustand) and refresh via HttpOnly cookie.

import { useAuthStore } from '@/store/auth.store';

api.interceptors.request.use(
    (config) => {
        const accessToken = useAuthStore.getState().accessToken;
        if (accessToken) {
            config.headers.Authorization = `Bearer ${accessToken}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

import { authService } from '@/services/auth.service';

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Handle 401 Unauthorized (Token expired)
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            // Only try to refresh if we had a token in the first place
            const currentUser = useAuthStore.getState().user;
            const refreshToken = useAuthStore.getState().refreshToken;

            if (currentUser && refreshToken) {
                try {
                    // Refresh the token
                    const { access } = await authService.refreshToken();

                    // Update the store
                    useAuthStore.getState().setAuth(
                        currentUser,
                        access
                    );

                    // Update the header for the retry
                    originalRequest.headers.Authorization = `Bearer ${access}`;

                    // Retry the original request
                    return api(originalRequest);
                } catch (refreshError) {
                    // If refresh fails, just logout but DON'T force redirect
                    // This allows public pages (like search) to continue working as guest
                    useAuthStore.getState().logout();

                    // Only redirect if we are on a protected route (optional logic)
                    // For now, just let the app handle the unauthenticated state
                    return Promise.reject(refreshError);
                }
            }
        }
        return Promise.reject(error);
    }
);

