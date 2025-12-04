import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000/api/v1';

export async function POST(request: Request) {
    const cookieStore = await cookies();
    const refreshToken = cookieStore.get('refresh_token')?.value;

    if (refreshToken) {
        // Optional: Call backend to blacklist token
        try {
            // We need the access token to call logout on backend, but we might not have it here easily 
            // unless passed in headers. For now, we just clear the cookie.
            // If we want to be strict, we should pass the access token in Authorization header to this route too.
        } catch (e) {
            // Ignore error
        }
    }

    cookieStore.delete('refresh_token');

    return NextResponse.json({ message: 'Logged out successfully' });
}
