'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { tripsService } from '@/services/trips';
import { ticketsService } from '@/services/tickets';
import { paymentsService } from '@/services/payments';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, CreditCard, Smartphone, User, Mail, Phone, ArrowLeft, CheckCircle, ShieldCheck } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { fr } from 'date-fns/locale';
import Link from 'next/link';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import dynamic from 'next/dynamic';

// Dynamically import RouteMap
const RouteMap = dynamic(() => import('@/components/features/RouteMap'), {
    ssr: false,
    loading: () => (
        <div className="w-full h-48 bg-slate-100 rounded-lg flex items-center justify-center">
            <div className="text-slate-500">Chargement de la carte...</div>
        </div>
    ),
});

const passengerSchema = z.object({
    first_name: z.string().min(2, 'Prénom requis'),
    last_name: z.string().min(2, 'Nom requis'),
    email: z.string().email('Email invalide').optional().or(z.literal('')),
    phone_number: z.string().regex(/^\+?[0-9]{10,15}$/, 'Numéro invalide (ex: +225...)'),
});

type PassengerForm = z.infer<typeof passengerSchema>;

export default function BookingPage() {
    const params = useParams();
    const tripId = params.id as string;
    const [paymentMethod, setPaymentMethod] = useState<'mobile_money' | 'card'>('mobile_money');

    const { register, handleSubmit, formState: { errors } } = useForm<PassengerForm>({
        resolver: zodResolver(passengerSchema),
    });

    // Fetch trip details
    const { data: trip, isLoading } = useQuery({
        queryKey: ['trip', tripId],
        queryFn: () => tripsService.getById(tripId),
    });

    // Create ticket mutation
    const createTicketMutation = useMutation({
        mutationFn: ticketsService.create,
    });

    // Initiate payment mutation
    const initiatePaymentMutation = useMutation({
        mutationFn: paymentsService.initiate,
        onSuccess: (data) => {
            if (data.payment_url) {
                window.location.href = data.payment_url;
            } else {
                toast.success('Paiement initié. Vérifiez votre téléphone.');
                // Redirect to a success/pending page or handle accordingly
            }
        },
        onError: () => {
            toast.error('Erreur lors du paiement');
        },
    });

    const onSubmit = async (data: PassengerForm) => {
        if (!trip) return;

        try {
            // 1. Create ticket
            const ticket = await createTicketMutation.mutateAsync({
                trip: tripId,
                passenger_details: {
                    first_name: data.first_name,
                    last_name: data.last_name,
                    phone_number: data.phone_number,
                    email: data.email || undefined,
                }
            });

            // 2. Initiate payment
            await initiatePaymentMutation.mutateAsync({
                ticket_id: ticket.id,
                method: paymentMethod,
                phone_number: paymentMethod === 'mobile_money' ? data.phone_number : undefined,
            });
        } catch (error: unknown) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const msg = (error as any).response?.data?.detail || 'Erreur lors de la réservation';
            toast.error(msg);
        }
    };

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50">
                <Loader2 className="w-12 h-12 animate-spin text-blue-600" />
            </div>
        );
    }

    if (!trip) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <p className="text-slate-500">Voyage introuvable</p>
            </div>
        );
    }

    const price = parseFloat(trip.price);
    const isProcessing = createTicketMutation.isPending || initiatePaymentMutation.isPending;

    return (
        <div className="min-h-screen bg-slate-50">
            {/* Header */}
            <div className="bg-white border-b sticky top-0 z-10 p-4">
                <div className="container mx-auto max-w-6xl flex items-center gap-4">
                    <Link href={`/trips/search`} className="p-2 hover:bg-slate-100 rounded-full">
                        <ArrowLeft className="w-6 h-6" />
                    </Link>
                    <h1 className="font-bold text-lg">Finaliser la réservation</h1>
                </div>
            </div>

            <div className="container mx-auto max-w-6xl px-4 py-8">
                <div className="grid lg:grid-cols-3 gap-8">
                    {/* LEFT: Form */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Step 1: Passenger Info */}
                        <Card className="border-0 shadow-md overflow-hidden">
                            <div className="bg-blue-600 p-4 text-white flex items-center gap-3">
                                <div className="w-8 h-8 bg-white text-blue-600 rounded-full flex items-center justify-center font-bold">1</div>
                                <h2 className="font-bold text-lg">Informations du passager</h2>
                            </div>
                            <CardContent className="p-6">
                                <form id="booking-form" onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                                    <div className="grid md:grid-cols-2 gap-5">
                                        <div>
                                            <Label className="flex items-center text-slate-700 font-semibold mb-2">
                                                <User className="w-4 h-4 mr-2" /> Prénom
                                            </Label>
                                            <Input
                                                placeholder="Jean"
                                                {...register('first_name')}
                                                className="h-12 bg-slate-50"
                                            />
                                            {errors.first_name && <p className="text-sm text-red-500 mt-1">{errors.first_name.message}</p>}
                                        </div>
                                        <div>
                                            <Label className="flex items-center text-slate-700 font-semibold mb-2">
                                                <User className="w-4 h-4 mr-2" /> Nom
                                            </Label>
                                            <Input
                                                placeholder="Kouassi"
                                                {...register('last_name')}
                                                className="h-12 bg-slate-50"
                                            />
                                            {errors.last_name && <p className="text-sm text-red-500 mt-1">{errors.last_name.message}</p>}
                                        </div>
                                    </div>

                                    <div className="grid md:grid-cols-2 gap-5">
                                        <div>
                                            <Label className="flex items-center text-slate-700 font-semibold mb-2">
                                                <Mail className="w-4 h-4 mr-2" /> Email (Optionnel)
                                            </Label>
                                            <Input
                                                type="email"
                                                placeholder="jean@exemple.com"
                                                {...register('email')}
                                                className="h-12 bg-slate-50"
                                            />
                                            {errors.email && <p className="text-sm text-red-500 mt-1">{errors.email.message}</p>}
                                        </div>
                                        <div>
                                            <Label className="flex items-center text-slate-700 font-semibold mb-2">
                                                <Phone className="w-4 h-4 mr-2" /> Téléphone
                                            </Label>
                                            <Input
                                                placeholder="+225 07 12 34 56 78"
                                                {...register('phone_number')}
                                                className="h-12 bg-slate-50"
                                            />
                                            {errors.phone_number && <p className="text-sm text-red-500 mt-1">{errors.phone_number.message}</p>}
                                        </div>
                                    </div>
                                </form>
                            </CardContent>
                        </Card>

                        {/* Step 2: Payment Method */}
                        <Card className="border-0 shadow-md overflow-hidden">
                            <div className="bg-slate-800 p-4 text-white flex items-center gap-3">
                                <div className="w-8 h-8 bg-white text-slate-800 rounded-full flex items-center justify-center font-bold">2</div>
                                <h2 className="font-bold text-lg">Moyen de paiement</h2>
                            </div>
                            <CardContent className="p-6">
                                <div className="grid md:grid-cols-2 gap-4 mb-6">
                                    <PaymentMethodCard
                                        icon={<Smartphone className="w-6 h-6" />}
                                        title="Mobile Money"
                                        subtitle="Orange, MTN, Moov, Wave"
                                        active={paymentMethod === 'mobile_money'}
                                        onClick={() => setPaymentMethod('mobile_money')}
                                    />
                                    <PaymentMethodCard
                                        icon={<CreditCard className="w-6 h-6" />}
                                        title="Carte Bancaire"
                                        subtitle="Visa, Mastercard"
                                        active={paymentMethod === 'card'}
                                        onClick={() => setPaymentMethod('card')}
                                    />
                                </div>

                                <div className="flex items-center gap-2 text-sm text-slate-600 bg-green-50 p-3 rounded-lg">
                                    <ShieldCheck className="w-5 h-5 text-green-600 shrink-0" />
                                    <span>Paiement 100% sécurisé via CinetPay. Vos données sont chiffrées.</span>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Submit Button */}
                        <Button
                            type="submit"
                            form="booking-form"
                            className="w-full h-14 bg-green-600 hover:bg-green-700 text-white font-bold text-lg shadow-lg"
                            disabled={isProcessing}
                        >
                            {isProcessing ? (
                                <>
                                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                                    Traitement en cours...
                                </>
                            ) : (
                                `Payer ${price.toLocaleString()} FCFA`
                            )}
                        </Button>
                    </div>

                    {/* RIGHT: Summary */}
                    <div className="lg:col-span-1">
                        <div className="sticky top-24 space-y-6">
                            <Card className="border-0 shadow-lg">
                                <CardHeader className="bg-slate-50 border-b">
                                    <CardTitle className="text-lg">Récapitulatif</CardTitle>
                                </CardHeader>
                                <CardContent className="p-6 space-y-6">
                                    {/* Company */}
                                    <div className="flex items-center gap-3">
                                        {trip.company.logo ? (
                                            /* eslint-disable-next-line @next/next/no-img-element */
                                            <img src={trip.company.logo} alt={trip.company.name} className="w-10 h-10 rounded-full object-cover" />
                                        ) : (
                                            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center font-bold text-blue-600">
                                                {trip.company.name.substring(0, 2).toUpperCase()}
                                            </div>
                                        )}
                                        <span className="font-bold text-slate-900">{trip.company.name}</span>
                                    </div>

                                    {/* Map Preview */}
                                    <div className="rounded-lg overflow-hidden border border-slate-200">
                                        <RouteMap
                                            departureCity={trip.departure_city}
                                            arrivalCity={trip.arrival_city}
                                            distance={trip.distance_km}
                                            height="200px"
                                        />
                                    </div>

                                    {/* Route */}
                                    <div className="relative pl-4 border-l-2 border-slate-200 space-y-6">
                                        <div className="relative">
                                            <div className="absolute -left-[21px] top-1 w-3 h-3 bg-blue-600 rounded-full border-2 border-white" />
                                            <div className="font-bold text-slate-900">
                                                {format(parseISO(trip.departure_datetime), 'HH:mm')}
                                            </div>
                                            <div className="text-sm text-slate-600">{trip.departure_city.name}</div>
                                            <div className="text-xs text-slate-400">
                                                {format(parseISO(trip.departure_datetime), 'dd MMM yyyy', { locale: fr })}
                                            </div>
                                        </div>
                                        <div className="relative">
                                            <div className="absolute -left-[21px] top-1 w-3 h-3 bg-amber-500 rounded-full border-2 border-white" />
                                            <div className="font-bold text-slate-900">Arrivée estimée</div>
                                            <div className="text-sm text-slate-600">{trip.arrival_city.name}</div>
                                        </div>
                                    </div>

                                    {/* Price Breakdown */}
                                    <div className="border-t border-slate-100 pt-4 space-y-3">
                                        <div className="flex justify-between items-center text-slate-600">
                                            <span>Prix du ticket</span>
                                            <span className="font-semibold">{price.toLocaleString()} FCFA</span>
                                        </div>
                                        <div className="flex justify-between items-center text-slate-600">
                                            <span>Frais de service</span>
                                            <span className="font-semibold">0 FCFA</span>
                                        </div>
                                        <div className="flex justify-between items-center text-xl font-bold text-blue-600 pt-3 border-t border-slate-100">
                                            <span>Total</span>
                                            <span>{price.toLocaleString()} FCFA</span>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Payment Method Card Component
function PaymentMethodCard({
    icon,
    title,
    subtitle,
    active,
    onClick,
}: {
    icon: React.ReactNode;
    title: string;
    subtitle: string;
    active: boolean;
    onClick: () => void;
}) {
    return (
        <button
            type="button"
            onClick={onClick}
            className={cn(
                'relative p-4 rounded-xl border-2 transition-all text-left hover:scale-105',
                active
                    ? 'border-blue-600 bg-blue-50 shadow-lg'
                    : 'border-slate-200 hover:border-blue-200'
            )}
        >
            <div className="flex items-center gap-3">
                <div className={cn(
                    'w-12 h-12 rounded-full flex items-center justify-center',
                    active ? 'bg-blue-100 text-blue-600' : 'bg-slate-100 text-slate-500'
                )}>
                    {icon}
                </div>
                <div>
                    <h3 className="font-bold text-slate-900">{title}</h3>
                    <p className="text-sm text-slate-500">{subtitle}</p>
                </div>
            </div>
            {active && (
                <CheckCircle className="absolute top-3 right-3 w-6 h-6 text-blue-600" />
            )}
        </button>
    );
}