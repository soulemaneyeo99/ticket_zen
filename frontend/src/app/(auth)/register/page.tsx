'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authService } from '@/services/auth';
import { RegisterPayload } from '@/types/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Bus, User, Building2, Mail, Phone, Lock, ArrowRight, Loader2 } from 'lucide-react';
import { z } from 'zod';

type RegisterForm = RegisterPayload & {
    password_confirm: string;
};

const registerSchema = z.object({
    first_name: z.string().min(2, 'Prénom requis'),
    last_name: z.string().min(2, 'Nom requis'),
    email: z.string().email('Email invalide'),
    phone_number: z.string().min(10, 'Numéro invalide'),
    password: z.string().min(8, '8 caractères minimum'),
    password_confirm: z.string(),
    role: z.enum(['client', 'compagnie']),
}).refine((data) => data.password === data.password_confirm, {
    message: "Les mots de passe ne correspondent pas",
    path: ["password_confirm"],
});

export default function RegisterPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [selectedRole, setSelectedRole] = useState<'client' | 'compagnie'>('client');

    const { register, handleSubmit, setValue, formState: { errors } } = useForm<RegisterForm>({
        resolver: zodResolver(registerSchema),
        defaultValues: {
            role: 'client'
        }
    });

    const onSubmit = async (data: RegisterForm) => {
        setIsLoading(true);
        try {
            // Remove password_confirm before sending to API
            const { password_confirm, ...payload } = data;
            await authService.register(payload);

            toast.success("Compte créé avec succès. Vous pouvez maintenant vous connecter.");

            router.push('/login');
        } catch (error: any) {
            console.error('Registration error:', error);
            const errorMessage = error?.response?.data?.email?.[0] ||
                error?.response?.data?.phone_number?.[0] ||
                error?.response?.data?.password?.[0] ||
                error?.response?.data?.detail ||
                "Une erreur est survenue. Vérifiez vos informations.";

            toast.error(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const handleRoleSelect = (role: 'client' | 'compagnie') => {
        setSelectedRole(role);
        setValue('role', role);
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
                    <h1 className="text-4xl font-bold mb-6">Rejoignez la communauté Ticket Zen</h1>
                    <p className="text-blue-100 text-lg leading-relaxed mb-8">
                        Créez votre compte gratuitement et commencez à voyager plus intelligemment. Accès instantané à des centaines de trajets quotidiens.
                    </p>
                    <div className="grid grid-cols-2 gap-6">
                        <div className="bg-white/10 p-4 rounded-xl backdrop-blur-sm">
                            <User className="w-6 h-6 mb-2 text-orange-400" />
                            <h3 className="font-bold">Pour les Voyageurs</h3>
                            <p className="text-sm text-blue-200">Réservez en 2 clics</p>
                        </div>
                        <div className="bg-white/10 p-4 rounded-xl backdrop-blur-sm">
                            <Building2 className="w-6 h-6 mb-2 text-orange-400" />
                            <h3 className="font-bold">Pour les Compagnies</h3>
                            <p className="text-sm text-blue-200">Gérez votre flotte</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Side - Form */}
            <div className="w-full lg:w-1/2 flex items-center justify-center p-8 overflow-y-auto">
                <div className="w-full max-w-md space-y-8 my-8">
                    <div className="text-center lg:text-left">
                        <Link href="/" className="inline-flex items-center text-blue-600 font-bold text-xl mb-8 lg:hidden">
                            <Bus className="w-6 h-6 mr-2" /> Ticket Zen
                        </Link>
                        <h2 className="text-3xl font-bold text-gray-900">Créer un compte</h2>
                        <p className="mt-2 text-gray-600">Choisissez votre type de compte pour commencer.</p>
                    </div>

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                        {/* Role Selection */}
                        <div className="grid grid-cols-2 gap-4">
                            <div
                                onClick={() => handleRoleSelect('client')}
                                className={`cursor-pointer p-4 rounded-xl border-2 transition-all ${selectedRole === 'client' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'}`}
                            >
                                <User className={`w-6 h-6 mb-2 ${selectedRole === 'client' ? 'text-blue-600' : 'text-gray-400'}`} />
                                <h3 className={`font-bold ${selectedRole === 'client' ? 'text-blue-900' : 'text-gray-700'}`}>Voyageur</h3>
                            </div>
                            <div
                                onClick={() => handleRoleSelect('compagnie')}
                                className={`cursor-pointer p-4 rounded-xl border-2 transition-all ${selectedRole === 'compagnie' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'}`}
                            >
                                <Building2 className={`w-6 h-6 mb-2 ${selectedRole === 'compagnie' ? 'text-blue-600' : 'text-gray-400'}`} />
                                <h3 className={`font-bold ${selectedRole === 'compagnie' ? 'text-blue-900' : 'text-gray-700'}`}>Compagnie</h3>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="first_name">Prénom</Label>
                                <Input id="first_name" placeholder="Jean" {...register('first_name')} className="h-11" />
                                {errors.first_name && <p className="text-sm text-red-500">{errors.first_name.message}</p>}
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="last_name">Nom</Label>
                                <Input id="last_name" placeholder="Kouassi" {...register('last_name')} className="h-11" />
                                {errors.last_name && <p className="text-sm text-red-500">{errors.last_name.message}</p>}
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="email">Email</Label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                                <Input id="email" type="email" placeholder="exemple@email.com" className="pl-10 h-11" {...register('email')} />
                            </div>
                            {errors.email && <p className="text-sm text-red-500">{errors.email.message}</p>}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="phone">Téléphone</Label>
                            <div className="relative">
                                <Phone className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                                <Input id="phone" placeholder="+225 07..." className="pl-10 h-11" {...register('phone_number')} />
                            </div>
                            {errors.phone_number && <p className="text-sm text-red-500">{errors.phone_number.message}</p>}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password">Mot de passe</Label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                                <Input id="password" type="password" placeholder="••••••••" className="pl-10 h-11" {...register('password')} />
                            </div>
                            {errors.password && <p className="text-sm text-red-500">{errors.password.message}</p>}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password_confirm">Confirmer le mot de passe</Label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                                <Input id="password_confirm" type="password" placeholder="••••••••" className="pl-10 h-11" {...register('password_confirm')} />
                            </div>
                            {errors.password_confirm && <p className="text-sm text-red-500">{errors.password_confirm.message}</p>}
                        </div>

                        <Button
                            type="submit"
                            className="w-full h-12 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-lg shadow-lg hover:shadow-blue-600/30 transition-all"
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="mr-2 h-5 w-5 animate-spin" /> Création...
                                </>
                            ) : (
                                <>
                                    Créer mon compte <ArrowRight className="ml-2 h-5 w-5" />
                                </>
                            )}
                        </Button>
                    </form>

                    <div className="text-center mt-6">
                        <p className="text-gray-600">
                            Déjà un compte ?{' '}
                            <Link href="/login" className="font-semibold text-blue-600 hover:text-blue-500">
                                Se connecter
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
