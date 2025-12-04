import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/types';

interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    accessToken: string | null;
    refreshToken: string | null;
    setAuth: (user: User, accessToken: string, refreshToken?: string) => void;
    logout: () => void;
    updateUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            isAuthenticated: false,
            accessToken: null,
            refreshToken: null,
            setAuth: (user, accessToken, refreshToken) => set({
                user,
                isAuthenticated: true,
                accessToken,
                refreshToken: refreshToken || null
            }),
            logout: () => set({ user: null, isAuthenticated: false, accessToken: null, refreshToken: null }),
            updateUser: (user) => set({ user }),
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({
                user: state.user,
                isAuthenticated: state.isAuthenticated,
                refreshToken: state.refreshToken // Persist refresh token
            }),
        }
    )
);
