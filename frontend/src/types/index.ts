export interface User {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    full_name: string;
    phone_number: string;
    role: 'voyageur' | 'compagnie' | 'embarqueur' | 'admin';
    role_display: string;
    is_active: boolean;
    is_verified: boolean;
    company?: string | null; // ID of the company
    company_name?: string | null;
    avatar?: string | null;
    created_at: string;
    last_login?: string;
}

export interface AuthResponse {
    message: string;
    user: User;
    tokens: {
        access: string;
        refresh: string;
    };
}

export interface ApiError {
    message: string;
    errors?: Record<string, string[]>;
}

export interface City {
    id: number;
    name: string;
    slug: string;
    country: string;
}

export interface Trip {
    id: number;
    company_name: string;
    departure_city: number;
    departure_city_name: string;
    arrival_city: number;
    arrival_city_name: string;
    departure_datetime: string;
    base_price: string;
    available_seats: number;
    total_seats: number;
    status: string;
    status_display: string;
    occupancy_rate: number;
    // Optional fields for details view
    vehicle?: any;
    estimated_duration?: number;
    distance_km?: string;
    amenities?: string[]; // To be added later

    // Detail view specific fields
    departure_city_details?: City;
    arrival_city_details?: City;
    estimated_arrival_datetime?: string;
    company?: any; // Full company object in detail view
}

export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}
