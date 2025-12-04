'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Bus, LayoutDashboard, Settings, Ticket, Users } from 'lucide-react';

const sidebarItems = [
    { href: '/company', label: 'Tableau de bord', icon: LayoutDashboard },
    { href: '/company/fleet', label: 'Ma Flotte', icon: Bus },
    { href: '/company/trips', label: 'Voyages', icon: Ticket },
    { href: '/company/staff', label: 'Personnel', icon: Users },
    { href: '/company/settings', label: 'Paramètres', icon: Settings },
];

export default function CompanyLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();

    return (
        <div className="flex min-h-screen bg-gray-100 dark:bg-gray-900">
            {/* Sidebar */}
            <aside className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 hidden md:block">
                <div className="p-6">
                    <h2 className="text-2xl font-bold text-primary">Ticket Zen</h2>
                    <p className="text-sm text-gray-500">Espace Compagnie</p>
                </div>
                <nav className="mt-6 px-4 space-y-2">
                    {sidebarItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors",
                                    isActive
                                        ? "bg-primary/10 text-primary"
                                        : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                                )}
                            >
                                <Icon className="w-5 h-5 mr-3" />
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto">
                {children}
            </main>
        </div>
    );
}
