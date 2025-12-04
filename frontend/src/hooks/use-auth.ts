import { useAuthStore } from '@/store/auth';
import { authService } from '@/services/auth';
import { useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

export const useAuth = () => {
    const router = useRouter();
    const { user, isAuthenticated, logout: storeLogout } = useAuthStore();

    // Login Mutation
    const loginMutation = useMutation({
        mutationFn: authService.login,
        onSuccess: (data) => {
            // Store update is already handled in authService.login, but we can do it here too or just rely on store
            // My authService.login ALREADY calls setAuth. So I don't need to call it here.
            // But for clarity, I'll let the service handle the store update as implemented in auth.ts

            toast.success(`Bienvenue, ${data.user.first_name} !`);

            // Redirection based on role
            const routes: Record<string, string> = {
                client: '/client',
                compagnie: '/company',
                admin: '/admin',
                embarqueur: '/agent',
            };
            router.push(routes[data.user.role] || '/');
        },
        onError: () => {
            toast.error('Email ou mot de passe incorrect');
        },
    });

    // Register Mutation
    const registerMutation = useMutation({
        mutationFn: authService.register,
        onSuccess: (data) => {
            toast.success('Compte créé !');
            // If auto-login happened in service
            if (data.tokens) {
                router.push('/');
            } else {
                router.push('/login');
            }
        },
        onError: (error: any) => {
            const msg =
                error.response?.data?.email?.[0] || "Erreur lors de l'inscription";
            toast.error(msg);
        },
    });

    // Logout
    const logout = async () => {
        try {
            await authService.logout();
        } catch { }
        // storeLogout is called in authService.logout too, but safe to call here
        storeLogout();
        router.push('/');
    };

    return {
        user,
        isAuthenticated,
        login: loginMutation.mutate,
        register: registerMutation.mutate,
        logout,
        isLoggingIn: loginMutation.isPending,
        isRegistering: registerMutation.isPending,
    };
};