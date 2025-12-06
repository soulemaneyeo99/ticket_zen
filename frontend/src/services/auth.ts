import { apiPost } from '@/lib/api';
import { AuthResponse, LoginPayload, RegisterPayload, User } from '@/types/api';
import { useAuthStore } from '@/store/auth';

export const authService = {
    login: async (payload: LoginPayload) => {
        const data = await apiPost<AuthResponse>('/auth/login/', payload);
        useAuthStore.getState().setAuth(data.user, data.tokens.access, data.tokens.refresh);
        return data;
    },

    register: async (payload: RegisterPayload) => {
        const data = await apiPost<AuthResponse>('/auth/register/', payload);
        // Auto login after register if backend returns tokens, otherwise user might need to login
        // Assuming backend returns tokens on register as per common practice, but if not, adjust.
        // The prompt says Response: {user: User, tokens: {access, refresh}} for login, 
        // but for register it just says Body. I'll assume it returns AuthResponse or I'll handle it.
        // Actually prompt doesn't specify register response. I'll assume it returns AuthResponse for better UX.
        if (data.tokens) {
            useAuthStore.getState().setAuth(data.user, data.tokens.access, data.tokens.refresh);
        }
        return data;
    },

    logout: async () => {
        const refreshToken = useAuthStore.getState().refreshToken;
        if (refreshToken) {
            try {
                await apiPost('/auth/logout/', { refresh_token: refreshToken });
            } catch (error) {
                console.error('Logout failed on server', error);
            }
        }
        useAuthStore.getState().logout();
    },

    refreshToken: async () => {
        const refreshToken = useAuthStore.getState().refreshToken;
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }
        const data = await apiPost<{ access: string; refresh: string }>('/auth/refresh/', { refresh: refreshToken });
        return data;
    },

    getCurrentUser: async () => {
        const data = await apiPost<{ user: User }>('/auth/user/', {});
        return data.user;
    },
};
