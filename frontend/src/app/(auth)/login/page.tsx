'use client';

import { Suspense, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/auth.store';
import { authService, LoginCredentials } from '@/services/auth.service';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { Bus, Lock, Mail, ArrowRight, Loader2 } from 'lucide-react';
import { z } from 'zod';

const loginSchema = z.object({
    email: z.string().email('Email invalide'),
    password: z.string().min(1, 'Mot de passe requis'),
});

function LoginForm() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { setAuth } = useAuthStore();
    const { toast } = useToast();
    const [isLoading, setIsLoading] = useState(false);

    const { register, handleSubmit, formState: { errors } } = useForm<LoginCredentials>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data: LoginCredentials) => {
        setIsLoading(true);
        try {
            const response = await authService.login(data);
            setAuth(response.user, response.tokens.access);

            toast({
                title: "Connexion réussie",
                description: `Bienvenue, ${response.user.first_name} !`,
                className: "bg-green-50 border-green-200 text-green-800",
            });

            // Redirect based on role
            const from = searchParams.get('from');
            if (from) {
                router.push(from);
            } else {
                switch (response.user.role) {
                    case 'compagnie':
                        router.push('/company');
                        break;
                    case 'embarqueur':
                        router.push('/agent');
                        break;
                    case 'admin':
                        router.push('/admin');
                        break;
                    default:
                        router.push('/client');
                }
            }
        } catch (error) {
            toast({
                variant: "destructive",
                title: "Erreur de connexion",
                description: "Email ou mot de passe incorrect.",
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex bg-gray-50">
            {/* Left Side - Visual */}
            <div className="hidden lg:flex lg:w-1/2 bg-blue-600 relative overflow-hidden items-center justify-center">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-blue-900 opacity-90"></div>
                <div className="absolute inset-0 bg-[url('/hero-bus.png')] bg-cover bg-center mix-blend-overlay opacity-20"></div>

                <div className="relative z-10 text-white p-12 max-w-lg">
                    <div className="mb-8 bg-white/10 w-16 h-16 rounded-2xl flex items-center justify-center backdrop-blur-sm">
                        <Bus className="w-8 h-8" />
                    </div>
                    <h1 className="text-4xl font-bold mb-6">Voyagez plus loin avec Ticket Zen</h1>
                    <p className="text-blue-100 text-lg leading-relaxed mb-8">
                        Accédez à la plus grande plateforme de réservation de tickets de bus en Côte d'Ivoire. Gérez vos voyages, vos flottes et vos réservations en un seul endroit.
                    </p>
                    <div className="flex items-center space-x-4 text-sm font-medium text-blue-200">
                        <div className="flex -space-x-2">
                            {[1, 2, 3, 4].map(i => (
                                <div key={i} className="w-8 h-8 rounded-full bg-blue-400 border-2 border-blue-600"></div>
                            ))}
                        </div>
                        <span>Rejoint par +10,000 voyageurs</span>
                    </div>
                </div>
            </div>

            {/* Right Side - Form */}
            <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
                <div className="w-full max-w-md space-y-8">
                    <div className="text-center lg:text-left">
                        <Link href="/" className="inline-flex items-center text-blue-600 font-bold text-xl mb-8 lg:hidden">
                            <Bus className="w-6 h-6 mr-2" /> Ticket Zen
                        </Link>
                        <h2 className="text-3xl font-bold text-gray-900">Bon retour !</h2>
                        <p className="mt-2 text-gray-600">Connectez-vous pour accéder à votre espace.</p>
                    </div>

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                                    <Input
                                        id="email"
                                        type="email"
                                        placeholder="exemple@email.com"
                                        className="pl-10 h-12 bg-gray-50 border-gray-200 focus:bg-white transition-all"
                                        {...register('email')}
                                    />
                                </div>
                                {errors.email && <p className="text-sm text-red-500">{errors.email.message}</p>}
                            </div>

                            <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                    <Label htmlFor="password">Mot de passe</Label>
                                    <Link href="/forgot-password" className="text-sm font-medium text-blue-600 hover:text-blue-500">
                                        Mot de passe oublié ?
                                    </Link>
                                </div>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                                    <Input
                                        id="password"
                                        type="password"
                                        placeholder="••••••••"
                                        className="pl-10 h-12 bg-gray-50 border-gray-200 focus:bg-white transition-all"
                                        {...register('password')}
                                    />
                                </div>
                                {errors.password && <p className="text-sm text-red-500">{errors.password.message}</p>}
                            </div>
                        </div>

                        <Button
                            type="submit"
                            className="w-full h-12 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-lg shadow-lg hover:shadow-blue-600/30 transition-all"
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="mr-2 h-5 w-5 animate-spin" /> Connexion...
                                </>
                            ) : (
                                <>
                                    Se connecter <ArrowRight className="ml-2 h-5 w-5" />
                                </>
                            )}
                        </Button>
                    </form>

                    <div className="text-center mt-6">
                        <p className="text-gray-600">
                            Pas encore de compte ?{' '}
                            <Link href="/register" className="font-semibold text-blue-600 hover:text-blue-500">
                                Créer un compte
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function LoginPage() {
    return (
        <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><Loader2 className="w-12 h-12 animate-spin text-blue-600" /></div>}>
            <LoginForm />
        </Suspense>
    );
}
