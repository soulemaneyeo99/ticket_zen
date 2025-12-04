'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, Mail, Lock, User, Phone } from 'lucide-react';

const loginSchema = z.object({
    email: z.string().email('Email invalide'),
    password: z.string().min(1, 'Mot de passe requis'),
});

const registerSchema = z.object({
    email: z.string().email('Email invalide'),
    password: z.string().min(8, 'Minimum 8 caractères'),
    password_confirm: z.string(),
    first_name: z.string().min(2, 'Prénom requis'),
    last_name: z.string().min(2, 'Nom requis'),
    phone_number: z.string().regex(/^\+?[0-9]{10,15}$/, 'Numéro invalide'),
    role: z.literal('client'),
}).refine(data => data.password === data.password_confirm, {
    message: 'Les mots de passe ne correspondent pas',
    path: ['password_confirm'],
});

type LoginForm = z.infer<typeof loginSchema>;
type RegisterForm = z.infer<typeof registerSchema>;

export function AuthModal({ open, onClose }: { open: boolean; onClose: () => void }) {
    const { login, register: registerUser, isLoggingIn, isRegistering } = useAuth();
    const [activeTab, setActiveTab] = useState<'login' | 'register'>('login');

    const loginForm = useForm<LoginForm>({
        resolver: zodResolver(loginSchema),
    });

    const registerForm = useForm<RegisterForm>({
        resolver: zodResolver(registerSchema),
        defaultValues: { role: 'client' },
    });

    const onLoginSubmit = (data: LoginForm) => {
        login(data);
    };

    const onRegisterSubmit = (data: RegisterForm) => {
        const { password_confirm, ...payload } = data;
        registerUser(payload);
    };

    return (
        <Dialog open={open} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle className="text-2xl font-bold text-center">
                        Bienvenue sur Ticket Zen
                    </DialogTitle>
                </DialogHeader>

                <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="login">Connexion</TabsTrigger>
                        <TabsTrigger value="register">Inscription</TabsTrigger>
                    </TabsList>

                    {/* LOGIN TAB */}
                    <TabsContent value="login">
                        <form onSubmit={loginForm.handleSubmit(onLoginSubmit)} className="space-y-4">
                            <div>
                                <Label className="flex items-center gap-2 mb-2">
                                    <Mail className="w-4 h-4" /> Email
                                </Label>
                                <Input
                                    type="email"
                                    placeholder="jean@exemple.com"
                                    {...loginForm.register('email')}
                                    className="h-11"
                                />
                                {loginForm.formState.errors.email && (
                                    <p className="text-sm text-red-500 mt-1">{loginForm.formState.errors.email.message}</p>
                                )}
                            </div>

                            <div>
                                <Label className="flex items-center gap-2 mb-2">
                                    <Lock className="w-4 h-4" /> Mot de passe
                                </Label>
                                <Input
                                    type="password"
                                    placeholder="••••••••"
                                    {...loginForm.register('password')}
                                    className="h-11"
                                />
                                {loginForm.formState.errors.password && (
                                    <p className="text-sm text-red-500 mt-1">{loginForm.formState.errors.password.message}</p>
                                )}
                            </div>

                            <Button
                                type="submit"
                                className="w-full h-11 bg-blue-600 hover:bg-blue-700"
                                disabled={isLoggingIn}
                            >
                                {isLoggingIn ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Connexion...
                                    </>
                                ) : (
                                    'Se connecter'
                                )}
                            </Button>
                        </form>
                    </TabsContent>

                    {/* REGISTER TAB */}
                    <TabsContent value="register">
                        <form onSubmit={registerForm.handleSubmit(onRegisterSubmit)} className="space-y-4">
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <Label className="mb-2">Prénom</Label>
                                    <Input
                                        placeholder="Jean"
                                        {...registerForm.register('first_name')}
                                        className="h-11"
                                    />
                                    {registerForm.formState.errors.first_name && (
                                        <p className="text-sm text-red-500 mt-1">{registerForm.formState.errors.first_name.message}</p>
                                    )}
                                </div>
                                <div>
                                    <Label className="mb-2">Nom</Label>
                                    <Input
                                        placeholder="Kouassi"
                                        {...registerForm.register('last_name')}
                                        className="h-11"
                                    />
                                    {registerForm.formState.errors.last_name && (
                                        <p className="text-sm text-red-500 mt-1">{registerForm.formState.errors.last_name.message}</p>
                                    )}
                                </div>
                            </div>

                            <div>
                                <Label className="flex items-center gap-2 mb-2">
                                    <Mail className="w-4 h-4" /> Email
                                </Label>
                                <Input
                                    type="email"
                                    placeholder="jean@exemple.com"
                                    {...registerForm.register('email')}
                                    className="h-11"
                                />
                                {registerForm.formState.errors.email && (
                                    <p className="text-sm text-red-500 mt-1">{registerForm.formState.errors.email.message}</p>
                                )}
                            </div>

                            <div>
                                <Label className="flex items-center gap-2 mb-2">
                                    <Phone className="w-4 h-4" /> Téléphone
                                </Label>
                                <Input
                                    placeholder="+225 07 12 34 56 78"
                                    {...registerForm.register('phone_number')}
                                    className="h-11"
                                />
                                {registerForm.formState.errors.phone_number && (
                                    <p className="text-sm text-red-500 mt-1">{registerForm.formState.errors.phone_number.message}</p>
                                )}
                            </div>

                            <div>
                                <Label className="flex items-center gap-2 mb-2">
                                    <Lock className="w-4 h-4" /> Mot de passe
                                </Label>
                                <Input
                                    type="password"
                                    placeholder="Minimum 8 caractères"
                                    {...registerForm.register('password')}
                                    className="h-11"
                                />
                                {registerForm.formState.errors.password && (
                                    <p className="text-sm text-red-500 mt-1">{registerForm.formState.errors.password.message}</p>
                                )}
                            </div>

                            <div>
                                <Label className="mb-2">Confirmer le mot de passe</Label>
                                <Input
                                    type="password"
                                    placeholder="••••••••"
                                    {...registerForm.register('password_confirm')}
                                    className="h-11"
                                />
                                {registerForm.formState.errors.password_confirm && (
                                    <p className="text-sm text-red-500 mt-1">{registerForm.formState.errors.password_confirm.message}</p>
                                )}
                            </div>

                            <Button
                                type="submit"
                                className="w-full h-11 bg-amber-500 hover:bg-amber-600"
                                disabled={isRegistering}
                            >
                                {isRegistering ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Inscription...
                                    </>
                                ) : (
                                    "Créer mon compte"
                                )}
                            </Button>
                        </form>
                    </TabsContent>
                </Tabs>
            </DialogContent>
        </Dialog>
    );
}