import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextResponse } from "next/server";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || "");

const SYSTEM_PROMPT = `
Tu es l'assistant virtuel de Ticket Zen, la plateforme de référence pour la réservation de tickets de bus en Côte d'Ivoire.
Ton rôle est d'aider les utilisateurs à rechercher des trajets, comprendre le fonctionnement de la plateforme, et résoudre leurs problèmes courants.

Contexte Ticket Zen :
- **Services** : Réservation de billets de bus interurbains, gestion de flotte pour les compagnies.
- **Paiements** : Mobile Money (Wave, Orange Money, MTN Moov) et Cartes Bancaires.
- **Fonctionnalités** : E-ticket par SMS/QR Code, suivi de trajet en temps réel, tableau de bord pour les compagnies.
- **Politique** : Remboursement possible jusqu'à 24h avant le départ. Bagage soute (23kg) + main inclus.

Tes directives :
1. **Ton** : Professionnel, chaleureux, serviable et concis.
2. **Langue** : Français (Ivoirien courant accepté si l'utilisateur l'utilise, mais reste professionnel).
3. **Limitations** : Tu ne peux pas effectuer d'actions réelles (rembourser, réserver) mais tu guides l'utilisateur vers les bonnes pages.
4. **Sécurité** : Ne demande jamais de mot de passe ou de code PIN Mobile Money.

Si on te demande des horaires ou des prix spécifiques, explique que tu n'as pas accès aux données en temps réel et invite l'utilisateur à utiliser la recherche sur la page d'accueil.
`;


interface Message {
    sender: 'user' | 'bot';
    text: string;
}

export async function POST(req: Request) {
    try {
        const { message, history } = await req.json();

        if (!process.env.GEMINI_API_KEY) {
            return NextResponse.json(
                { error: "Clé API non configurée" },
                { status: 500 }
            );
        }

        const model = genAI.getGenerativeModel({ model: "gemini-pro" });

        const chat = model.startChat({
            history: [
                {
                    role: "user",
                    parts: [{ text: SYSTEM_PROMPT }],
                },
                {
                    role: "model",
                    parts: [{ text: "Compris. Je suis prêt à aider les utilisateurs de Ticket Zen." }],
                },
                ...(history || []).map((msg: Message) => ({
                    role: msg.sender === 'user' ? 'user' : 'model',
                    parts: [{ text: msg.text }],
                })),
            ],
        });

        const result = await chat.sendMessage(message);
        const response = await result.response;
        const text = response.text();

        return NextResponse.json({ text });
    } catch (error) {
        console.error("Gemini API Error:", error);
        return NextResponse.json(
            { error: "Une erreur est survenue lors du traitement de votre demande." },
            { status: 500 }
        );
    }
}
