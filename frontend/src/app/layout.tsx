// src/app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import QueryProvider from "@/providers/query-provider";
import AuthProvider from "@/providers/auth-provider";
import { Toaster } from "sonner"; // ← ADD THIS

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "Ticket Zen - Billetterie Digitale",
    description: "Réservez vos tickets de bus en Côte d'Ivoire",
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
                        <Toaster position="top-center" richColors /> {/* ← ADD THIS */}
                    </AuthProvider>
                </QueryProvider>
            </body>
        </html>
    );
}