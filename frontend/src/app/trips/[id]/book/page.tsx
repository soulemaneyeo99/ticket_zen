'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { tripService, Trip } from '@/services/trip.service';
import { paymentService, PaymentRequest } from '@/services/payment.service';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Loader2, CreditCard, Smartphone, User, Mail, Phone, MapPin, Calendar, Clock, Bus, CheckCircle, ShieldCheck } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { z } from 'zod';

const passengerSchema = z.object({
    first_name: z.string().min(2, 'Prénom requis'),
    last_name: z.string().min(2, 'Nom requis'),
    email: z.string().email('Email invalide'),
    phone_number: z.string().min(10, 'Numéro invalide'),
});

type PassengerData = z.infer<typeof passengerSchema>;

export default function BookingPage() {
    const params = useParams();
    const router = useRouter();
    const { toast } = useToast();
    const [trip, setTrip] = useState<Trip | null>(null);
    const [loading, setLoading] = useState(true);
    const [processing, setProcessing] = useState(false);
    const [paymentMethod, setPaymentMethod] = useState<'MOBILE_MONEY' | 'CREDIT_CARD'>('MOBILE_MONEY');

    const { register, handleSubmit, formState: { errors } } = useForm<PassengerData>({
        resolver: zodResolver(passengerSchema),
    });

    useEffect(() => {
        const fetchTrip = async () => {
            try {
                const data = await tripService.getTrip(params.id as string);
                setTrip(data);
            } catch (error) {
                toast({
                    variant: "destructive",
                    title: "Erreur",
                    description: "Impossible de charger les détails du voyage.",
                });
            } finally {
                setLoading(false);
            }
        };

        fetchTrip();
    }, [params.id, toast]);

    const onSubmit = async (data: PassengerData) => {
        if (!trip) return;

        setProcessing(true);
        try {
            // 1. Create Ticket first
            const ticketData = {
                trip: trip.id,
                passenger_first_name: data.first_name,
                passenger_last_name: data.last_name,
                passenger_phone: data.phone_number,
                passenger_email: data.email,
                seat_number: `A${Math.floor(Math.random() * 20) + 1}`, // Auto-assign seat for now
                price: typeof trip.price === 'string' ? parseFloat(trip.price) : trip.price
            };

            const ticket = await ticketService.create(ticketData);

            // 2. Initiate Payment
            const price = typeof trip.price === 'string' ? parseFloat(trip.price) : trip.price;

            const paymentRequest: PaymentRequest = {
                amount: price,
                currency: 'XOF',
                description: `Ticket de bus ${typeof trip.departure_city === 'object' ? trip.departure_city.name : ''} - ${typeof trip.arrival_city === 'object' ? trip.arrival_city.name : ''}`,
                customer_name: `${data.first_name} ${data.last_name}`,
                customer_surname: data.last_name,
                customer_phone_number: data.phone_number,
                customer_email: data.email,
                customer_address: 'Abidjan', // Default
                customer_city: 'Abidjan', // Default
                customer_country: 'CI',
                customer_state: 'Lagunes',
                customer_zip_code: '00225',
                payment_method: paymentMethod,
                ticket_id: ticket.id, // Use the created ticket ID
            };

            const response = await paymentService.initiatePayment(paymentRequest);

            // Redirect to payment gateway
            window.location.href = response.payment_url;

        } catch (error: any) {
            console.error('Booking error:', error);
            toast({
                variant: "destructive",
                title: "Erreur de réservation",
                description: error?.response?.data?.detail || "Impossible d'initialiser la réservation. Veuillez réessayer.",
            });
            setProcessing(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <Loader2 className="w-12 h-12 animate-spin text-blue-600" />
            </div>
        );
    }

    if (!trip) return null;

    const price = typeof trip.price === 'string' ? parseFloat(trip.price) : trip.price;
    const companyName = trip.company_name || (typeof trip.company === 'object' ? trip.company.name : 'Compagnie');

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4">
            <div className="container mx-auto max-w-6xl">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">Finaliser votre réservation</h1>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left Column: Form */}
                    <div className="lg:col-span-2 space-y-6">

                        {/* Step 1: Passenger Info */}
                        <Card className="border-0 shadow-md overflow-hidden">
                            <div className="bg-blue-600 p-4 text-white flex items-center">
                                <div className="w-8 h-8 bg-white text-blue-600 rounded-full flex items-center justify-center font-bold mr-3">1</div>
                                <h2 className="font-bold text-lg">Informations du passager</h2>
                            </div>
                            <CardContent className="p-6">
                                <form id="booking-form" onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="space-y-2">
                                            <Label htmlFor="first_name" className="flex items-center text-gray-700">
                                                <User className="w-4 h-4 mr-2" /> Prénom
                                            </Label>
                                            <Input id="first_name" placeholder="Jean" {...register('first_name')} className="h-11 bg-gray-50" />
                                            {errors.first_name && <p className="text-sm text-red-500">{errors.first_name.message}</p>}
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="last_name" className="flex items-center text-gray-700">
                                                <User className="w-4 h-4 mr-2" /> Nom
                                            </Label>
                                            <Input id="last_name" placeholder="Kouassi" {...register('last_name')} className="h-11 bg-gray-50" />
                                            {errors.last_name && <p className="text-sm text-red-500">{errors.last_name.message}</p>}
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="space-y-2">
                                            <Label htmlFor="email" className="flex items-center text-gray-700">
                                                <Mail className="w-4 h-4 mr-2" /> Email
                                            </Label>
                                            <Input id="email" type="email" placeholder="jean@exemple.com" {...register('email')} className="h-11 bg-gray-50" />
                                            {errors.email && <p className="text-sm text-red-500">{errors.email.message}</p>}
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="phone" className="flex items-center text-gray-700">
                                                <Phone className="w-4 h-4 mr-2" /> Téléphone
                                            </Label>
                                            <Input id="phone" placeholder="+225 07..." {...register('phone_number')} className="h-11 bg-gray-50" />
                                            {errors.phone_number && <p className="text-sm text-red-500">{errors.phone_number.message}</p>}
                                        </div>
                                    </div>
                                </form>
                            </CardContent>
                        </Card>

                        {/* Step 2: Payment Method */}
                        <Card className="border-0 shadow-md overflow-hidden">
                            <div className="bg-gray-800 p-4 text-white flex items-center">
                                <div className="w-8 h-8 bg-white text-gray-800 rounded-full flex items-center justify-center font-bold mr-3">2</div>
                                <h2 className="font-bold text-lg">Moyen de paiement</h2>
                            </div>
                            <CardContent className="p-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div
                                        onClick={() => setPaymentMethod('MOBILE_MONEY')}
                                        className={`cursor-pointer p-4 rounded-xl border-2 transition-all flex items-center space-x-4 ${paymentMethod === 'MOBILE_MONEY' ? 'border-orange-500 bg-orange-50' : 'border-gray-200 hover:border-orange-200'}`}
                                    >
                                        <div className={`w-12 h-12 rounded-full flex items-center justify-center ${paymentMethod === 'MOBILE_MONEY' ? 'bg-orange-100 text-orange-600' : 'bg-gray-100 text-gray-500'}`}>
                                            <Smartphone className="w-6 h-6" />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-gray-900">Mobile Money</h3>
                                            <p className="text-sm text-gray-500">Orange, MTN, Moov, Wave</p>
                                        </div>
                                        {paymentMethod === 'MOBILE_MONEY' && <CheckCircle className="w-6 h-6 text-orange-500 ml-auto" />}
                                    </div>

                                    <div
                                        onClick={() => setPaymentMethod('CREDIT_CARD')}
                                        className={`cursor-pointer p-4 rounded-xl border-2 transition-all flex items-center space-x-4 ${paymentMethod === 'CREDIT_CARD' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-200'}`}
                                    >
                                        <div className={`w-12 h-12 rounded-full flex items-center justify-center ${paymentMethod === 'CREDIT_CARD' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-500'}`}>
                                            <CreditCard className="w-6 h-6" />
                                        </div>
                                        <div>
                                            <h3 className="font-bold text-gray-900">Carte Bancaire</h3>
                                            <p className="text-sm text-gray-500">Visa, Mastercard</p>
                                        </div>
                                        {paymentMethod === 'CREDIT_CARD' && <CheckCircle className="w-6 h-6 text-blue-600 ml-auto" />}
                                    </div>
                                </div>

                                <div className="mt-6 flex items-center text-sm text-gray-500 bg-gray-50 p-3 rounded-lg">
                                    <ShieldCheck className="w-5 h-5 text-green-600 mr-2" />
                                    Paiement 100% sécurisé via CinetPay. Vos données sont chiffrées.
                                </div>
                            </CardContent>
                        </Card>

                        <Button
                            type="submit"
                            form="booking-form"
                            className="w-full h-14 bg-green-600 hover:bg-green-700 text-white font-bold text-lg shadow-lg hover:shadow-green-600/30 transition-all rounded-xl"
                            disabled={processing}
                        >
                            {processing ? (
                                <>
                                    <Loader2 className="mr-2 h-5 w-5 animate-spin" /> Traitement en cours...
                                </>
                            ) : (
                                <>
                                    Payer {price.toLocaleString()} FCFA
                                </>
                            )}
                        </Button>
                    </div>

                    {/* Right Column: Summary */}
                    <div className="lg:col-span-1">
                        <div className="sticky top-8">
                            <Card className="border-0 shadow-lg bg-white">
                                <CardHeader className="bg-gray-50 border-b border-gray-100 pb-4">
                                    <CardTitle className="text-lg text-gray-900">Récapitulatif du voyage</CardTitle>
                                </CardHeader>
                                <CardContent className="p-6 space-y-6">
                                    {/* Company */}
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center font-bold text-blue-600">
                                            {companyName.substring(0, 2).toUpperCase()}
                                        </div>
                                        <span className="font-bold text-gray-900">{companyName}</span>
                                    </div>

                                    {/* Route */}
                                    <div className="relative pl-4 border-l-2 border-gray-200 space-y-6">
                                        <div className="relative">
                                            <div className="absolute -left-[21px] top-1 w-3 h-3 bg-blue-600 rounded-full border-2 border-white"></div>
                                            <div className="font-bold text-gray-900">{format(new Date(trip.departure_time), 'HH:mm')}</div>
                                            <div className="text-sm text-gray-600">{typeof trip.departure_city === 'object' ? trip.departure_city.name : ''}</div>
                                            <div className="text-xs text-gray-400">{format(new Date(trip.departure_time), 'dd MMM yyyy', { locale: fr })}</div>
                                        </div>
                                        <div className="relative">
                                            <div className="absolute -left-[21px] top-1 w-3 h-3 bg-orange-500 rounded-full border-2 border-white"></div>
                                            <div className="font-bold text-gray-900">{format(new Date(trip.arrival_time), 'HH:mm')}</div>
                                            <div className="text-sm text-gray-600">{typeof trip.arrival_city === 'object' ? trip.arrival_city.name : ''}</div>
                                            <div className="text-xs text-gray-400">{format(new Date(trip.arrival_time), 'dd MMM yyyy', { locale: fr })}</div>
                                        </div>
                                    </div>

                                    <div className="border-t border-gray-100 pt-4">
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-gray-600">Prix du ticket</span>
                                            <span className="font-bold text-gray-900">{price.toLocaleString()} FCFA</span>
                                        </div>
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-gray-600">Frais de service</span>
                                            <span className="font-bold text-gray-900">0 FCFA</span>
                                        </div>
                                        <div className="flex justify-between items-center text-lg font-bold text-blue-600 mt-4 pt-4 border-t border-gray-100">
                                            <span>Total à payer</span>
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
