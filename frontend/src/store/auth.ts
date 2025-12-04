import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/types/api';

interface AuthState {
    user: User | null;
    accessToken: string | null;
    refreshToken: string | null;
    isAuthenticated: boolean;
    setAuth: (user: User, accessToken: string, refreshToken: string) => void;
    setAccessToken: (token: string) => void;
    logout: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            setAuth: (user, accessToken, refreshToken) =>
                set({ user, accessToken, refreshToken, isAuthenticated: true }),
            setAccessToken: (accessToken) => set({ accessToken }),
            logout: () =>
                set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false }),
        }),
        {
            name: 'ticket-zen-auth', // unique name for localStorage key
        }
    )
);