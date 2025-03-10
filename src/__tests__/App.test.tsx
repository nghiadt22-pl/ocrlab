import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';

// Mock the Clerk authentication
vi.mock('@clerk/clerk-react', () => ({
  useAuth: () => ({
    isSignedIn: true,
    signOut: vi.fn(),
  }),
  useUser: () => ({
    user: {
      firstName: 'Test',
    },
  }),
  ClerkProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  SignedIn: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  SignedOut: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock the UI components that use matchMedia
vi.mock('@/components/ui/toaster', () => ({
  Toaster: () => <div data-testid="mock-toaster">Toaster</div>,
}));

vi.mock('@/components/ui/sonner', () => ({
  Toaster: () => <div data-testid="mock-sonner">Sonner</div>,
}));

// Mock the components
vi.mock('../pages/Index', () => ({
  default: () => <div data-testid="index-page">Index Page</div>,
}));

vi.mock('../pages/Dashboard', () => ({
  default: () => <div data-testid="dashboard-page">Dashboard Page</div>,
}));

vi.mock('../pages/Folders', () => ({
  default: () => <div data-testid="folders-page">Folders Page</div>,
}));

vi.mock('../pages/FolderFiles', () => ({
  default: () => <div data-testid="folder-files-page">Folder Files Page</div>,
}));

vi.mock('../pages/Search', () => ({
  default: () => <div data-testid="search-page">Search Page</div>,
}));

vi.mock('../pages/Billing', () => ({
  default: () => <div data-testid="billing-page">Billing Page</div>,
}));

vi.mock('../pages/NotFound', () => ({
  default: () => <div data-testid="not-found-page">Not Found Page</div>,
}));

vi.mock('../pages/SignIn', () => ({
  default: () => <div data-testid="sign-in-page">Sign In Page</div>,
}));

vi.mock('../pages/SignUp', () => ({
  default: () => <div data-testid="sign-up-page">Sign Up Page</div>,
}));

// Mock the ProtectedRoute component
vi.mock('../components/auth/ProtectedRoute', () => ({
  ProtectedRoute: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock the PublicRoute component
vi.mock('../components/auth/PublicRoute', () => ({
  PublicRoute: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

describe('App Component Routing', () => {
  it('renders the index page at the root route', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByTestId('index-page')).toBeInTheDocument();
  });

  it('renders the dashboard page at /dashboard route', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
  });

  it('renders the folders page at /folders route', () => {
    render(
      <MemoryRouter initialEntries={['/folders']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByTestId('folders-page')).toBeInTheDocument();
  });

  it('renders the folder files page at /folders/:folderId route', () => {
    render(
      <MemoryRouter initialEntries={['/folders/123']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByTestId('folder-files-page')).toBeInTheDocument();
  });

  it('renders the search page at /search route', () => {
    render(
      <MemoryRouter initialEntries={['/search']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByTestId('search-page')).toBeInTheDocument();
  });

  it('renders the billing page at /billing route', () => {
    render(
      <MemoryRouter initialEntries={['/billing']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByTestId('billing-page')).toBeInTheDocument();
  });

  it('renders the sign-in page at /sign-in route', () => {
    render(
      <MemoryRouter initialEntries={['/sign-in']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByTestId('sign-in-page')).toBeInTheDocument();
  });

  it('renders the sign-up page at /sign-up route', () => {
    render(
      <MemoryRouter initialEntries={['/sign-up']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByTestId('sign-up-page')).toBeInTheDocument();
  });

  it('renders the not-found page for unknown routes', () => {
    render(
      <MemoryRouter initialEntries={['/unknown-route']}>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByTestId('not-found-page')).toBeInTheDocument();
  });
}); 