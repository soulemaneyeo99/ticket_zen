# Ticket Zen - Frontend

Plateforme de réservation de tickets de transport en ligne pour la Côte d'Ivoire.

## 🚀 Technologies

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **UI Components**: Shadcn/UI + Radix UI
- **State Management**: Zustand
- **Data Fetching**: React Query (TanStack Query)
- **Form Handling**: React Hook Form + Zod
- **Authentication**: JWT with HttpOnly Cookies
- **Icons**: Lucide React
- **Date Handling**: date-fns

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── (auth)/            # Auth routes (login, register)
│   │   ├── admin/             # Admin dashboard
│   │   ├── agent/             # Boarding agent pages
│   │   ├── client/            # Client dashboard
│   │   ├── company/           # Company management
│   │   │   ├── fleet/         # Fleet management
│   │   │   └── trips/         # Trip management
│   │   ├── trips/             # Public trip search & booking
│   │   ├── api/               # Next.js API routes (proxy)
│   │   │   └── auth/          # Auth endpoints
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Landing page
│   ├── components/
│   │   └── ui/                # Reusable UI components
│   ├── lib/
│   │   ├── axios.ts           # Axios instance
│   │   └── utils.ts           # Utility functions
│   ├── providers/             # React context providers
│   ├── services/              # API service layer
│   ├── store/                 # Zustand stores
│   ├── types/                 # TypeScript type definitions
│   └── middleware.ts          # Next.js middleware (auth)
├── public/                    # Static assets
└── package.json
```

## 🔧 Setup & Installation

### Prerequisites

- Node.js 18+ and npm
- Backend API running (see backend README)

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment variables**:
   Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000/api/v1
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:3000`

4. **Build for production**:
   ```bash
   npm run build
   npm start
   ```

## 🏗️ Architecture

### Authentication Flow

- **JWT Tokens**: Access tokens stored in memory (Zustand), refresh tokens in HttpOnly cookies
- **API Proxy**: Next.js API routes (`/api/auth/*`) proxy requests to backend and manage cookies
- **Middleware**: Protects routes and redirects unauthenticated users
- **Role-based Routing**: Automatic redirection based on user role after login

### State Management

- **Zustand**: Global auth state (user, access token)
- **React Query**: Server state caching and synchronization
- **React Hook Form**: Form state management

### API Layer

All API calls go through service modules in `src/services/`:
- `auth.service.ts` - Authentication
- `company.service.ts` - Company management
- `fleet.service.ts` - Vehicle management
- `trip.service.ts` - Trip management
- `ticket.service.ts` - Ticket booking
- `payment.service.ts` - Payment processing
- `boarding.service.ts` - Boarding operations

## 👥 User Roles & Features

### Voyageur (Client)
- Search and book trips
- View booking history
- Manage profile
- Receive digital tickets via email/SMS

### Compagnie (Transport Company)
- Manage fleet (vehicles)
- Create and manage trips
- View statistics and revenue
- Manage staff

### Embarqueur (Boarding Agent)
- Scan QR codes
- Validate tickets
- View boarding history

### Admin
- Validate companies
- View platform statistics
- Manage users
- Configure platform settings

## 🎨 UI Components

Built with Shadcn/UI and Radix UI primitives:
- `Button`, `Input`, `Label` - Form elements
- `Card` - Content containers
- `Select` - Dropdowns
- `Toast` - Notifications
- All components are fully accessible and themeable

## 🔐 Security

- HttpOnly cookies for refresh tokens
- CSRF protection via Next.js middleware
- Role-based access control
- Secure API proxy pattern
- Input validation with Zod schemas

## 📱 Responsive Design

- Mobile-first approach
- Tailwind CSS responsive utilities
- Optimized for all screen sizes

## 🧪 Development

### Code Style
```bash
npm run lint
```

### Type Checking
TypeScript strict mode enabled for maximum type safety.

## 🚢 Deployment

1. Build the application:
   ```bash
   npm run build
   ```

2. Set production environment variables

3. Deploy to your hosting platform (Vercel, Netlify, etc.)

## 📝 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000/api/v1` |
| `NEXT_PUBLIC_BACKEND_URL` | Backend base URL for proxy | `http://localhost:8000/api/v1` |

## 🤝 Contributing

1. Follow the existing code structure
2. Use TypeScript for all new files
3. Follow the component naming conventions
4. Test your changes before committing

## 📄 License

Proprietary - Ticket Zen Platform

---

**Built with ❤️ for the Ivorian transport industry**
