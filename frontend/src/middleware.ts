import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Routes that don't require authentication
const publicRoutes = [
    '/',
    '/login',
    '/register',
    '/forgot-password',
    '/trips/search',
    '/trips',
    '/api/auth/login',
    '/api/auth/register',
    '/api/auth/logout',
    '/api/auth/refresh',
];

export function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;

    // Check if the route is public
    if (publicRoutes.some(route => pathname.startsWith(route))) {
        return NextResponse.next();
    }

    // Check for refresh token cookie (HttpOnly)
    const refreshToken = request.cookies.get('refresh_token');

    if (!refreshToken) {
        // Redirect to login if no token
        const url = new URL('/login', request.url);
        url.searchParams.set('from', pathname);
        return NextResponse.redirect(url);
    }

    // Role-based protection (Basic check based on URL structure)
    // Ideally, we would decode the token here, but we don't have the access token in cookie (it's in memory)
    // So we rely on the refresh token presence for initial check, and client-side checks for specific roles.
    // However, for better security, we could store role in a non-HttpOnly cookie or decode the refresh token if it contains role.

    // For now, we allow access if refresh token exists, and let the client-side AuthGuard handle specific role redirects.
    // Or we could add a 'user_role' cookie set on login for middleware checks.

    return NextResponse.next();
}

export const config = {
    matcher: [
        /*
         * Match all request paths except for the ones starting with:
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico (favicon file)
         * - public (public folder)
         */
        '/((?!_next/static|_next/image|favicon.ico|public).*)',
    ],
};
