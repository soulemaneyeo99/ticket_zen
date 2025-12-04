export interface User {
  id: string;
  email: string;
  role: 'client' | 'compagnie' | 'admin' | 'embarqueur';
  first_name: string;
  last_name: string;
  phone_number: string;
}

export interface AuthResponse {
  user: User;
  tokens: {
    access: string;
    refresh: string;
  };
}

export interface City {
  id: number;
  name: string;
  slug: string;
}

export interface Company {
  name: string;
  logo: string;
}

export interface Vehicle {
  type: string;
  has_ac: boolean;
  has_wifi: boolean;
}

export interface Trip {
  id: string;
  departure_city: City;
  arrival_city: City;
  departure_datetime: string; // ISO 8601
  arrival_datetime: string;
  price: string; // Decimal string
  company: Company;
  vehicle: Vehicle;
  available_seats: number;
  status?: 'scheduled' | 'completed' | 'cancelled'; // Added for company view
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  role: 'client' | 'compagnie';
}

export interface PassengerDetails {
  first_name: string;
  last_name: string;
  phone_number: string;
  email?: string;
}

export interface CreateTicketPayload {
  trip: string; // Trip ID
  passenger_details: PassengerDetails;
}

export interface Ticket {
  id: string;
  trip: Trip;
  passenger_details: PassengerDetails;
  status: 'pending' | 'confirmed' | 'cancelled';
  qr_code: string;
  created_at: string;
  ticket_number?: string; // Added for display
}

export interface PaymentInitiatePayload {
  ticket_id: string;
  method: 'mobile_money' | 'card';
  phone_number?: string; // For mobile money
}

export interface PaymentResponse {
  payment_url?: string;
  status: string;
  transaction_id: string;
}