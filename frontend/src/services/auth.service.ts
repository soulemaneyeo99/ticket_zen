import axios from 'axios';
import { api } from '@/lib/axios';
import { User, AuthResponse } from '@/types';
import { z } from 'zod';

export const loginSchema = z.object({
    email: z.string().email('Email invalide'),
    password: z.string().min(1, 'Mot de passe requis'),
});

export type LoginCredentials = z.infer<typeof loginSchema>;

export const registerSchema = z.object({
    email: z.string().email('Email invalide'),
    password: z.string().min(8, 'Le mot de passe doit contenir au moins 8 caractères'),
    password_confirm: z.string().min(8, 'Confirmation requise'),
    first_name: z.string().min(2, 'Prénom requis'),
    last_name: z.string().min(2, 'Nom requis'),
    phone_number: z.string().regex(/^\+?1?\d{9,15}$/, 'Format invalide (+225...)'),
    role: z.enum(['voyageur', 'compagnie']),
}).refine((data) => data.password === data.password_confirm, {
    message: "Les mots de passe ne correspondent pas",
    path: ["password_confirm"],
});

export type RegisterData = z.infer<typeof registerSchema>;

export const authService = {
    login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
        // Use direct axios to hit Next.js API route (relative path)
        const response = await axios.post('/api/auth/login', credentials);
        return response.data;
    },

    register: async (data: RegisterData): Promise<AuthResponse> => {
        // Register also needs to set cookies if it auto-logs in
        // For now, let's assume register just creates user and we login after, 
        // OR we should create a proxy for register too if it returns tokens.
        // Let's check if register returns tokens. Yes it does.
        // So we should probably use a proxy for register too, or just login after register.
        // For simplicity, let's keep register hitting backend directly for now, 
        // but ideally we should have a proxy.
        // Actually, let's just use the backend direct for register, 
        // and then the user has to login (or we auto-login via the proxy).
        const response = await api.post('/auth/register/', data);
        return response.data;
    },

    logout: async (): Promise<void> => {
        // Use direct axios to hit Next.js API route
        await axios.post('/api/auth/logout');
    },

    refreshToken: async (): Promise<{ access: string }> => {
        // Use direct axios to hit Next.js API route
        // The proxy will read the HttpOnly cookie
        const response = await axios.post('/api/auth/refresh');
        return response.data;
    },

    getCurrentUser: async (): Promise<User> => {
        const response = await api.get('/auth/user/');
        return response.data;
    }
};
