// src/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import QueryProvider from "@/providers/query-provider";
import AuthProvider from "@/providers/auth-provider";
import { Toaster } from "sonner";
import Chatbot from "@/components/features/Chatbot";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "Ticket Zen - Billetterie Digitale",
    description: "Réservez vos tickets de bus en Côte d'Ivoire. Simple, rapide et sécurisé.",
    viewport: "width=device-width, initial-scale=1, maximum-scale=1",
    themeColor: "#2563eb",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="fr" suppressHydrationWarning>
            <body className={inter.className}>
                <QueryProvider>
                    <AuthProvider>
                        {children}
                        <Chatbot />
                        <Toaster position="top-center" richColors />
                    </AuthProvider>
                </QueryProvider>
            </body>
        </html>
    );
}