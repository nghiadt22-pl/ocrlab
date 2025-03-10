import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Header from '../components/Header';

// Mock signOut function
const mockSignOut = vi.fn();

// Mock the Clerk authentication
vi.mock('@clerk/clerk-react', () => ({
  useAuth: () => ({
    isSignedIn: true,
    signOut: mockSignOut,
  }),
  useUser: () => ({
    user: {
      firstName: 'Test',
    },
  }),
}));

// Mock useNavigate and useLocation
const mockNavigate = vi.fn();
let mockPathname = '/';

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ pathname: mockPathname }),
  };
});

// Wrapper component to provide router context
const HeaderWithRouter = () => (
  <BrowserRouter>
    <Header />
  </BrowserRouter>
);

describe('Header Component', () => {
  beforeEach(() => {
    // Reset mocks and pathname before each test
    vi.clearAllMocks();
    mockPathname = '/';
  });

  it('renders the application name', () => {
    render(<HeaderWithRouter />);
    expect(screen.getByText('Document Intelligence')).toBeInTheDocument();
  });

  it('renders navigation links when user is signed in', () => {
    render(<HeaderWithRouter />);
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Folders')).toBeInTheDocument();
    expect(screen.getByText('Search')).toBeInTheDocument();
    expect(screen.getByText('Billing')).toBeInTheDocument();
  });

  it('renders the user greeting when signed in', () => {
    render(<HeaderWithRouter />);
    expect(screen.getByText('Hello, Test')).toBeInTheDocument();
  });

  it('renders the sign out button when user is signed in', () => {
    render(<HeaderWithRouter />);
    expect(screen.getByRole('button', { name: /sign out/i })).toBeInTheDocument();
  });

  it('handles sign out when button is clicked', async () => {
    render(<HeaderWithRouter />);
    const user = userEvent.setup();
    
    const signOutButton = screen.getByRole('button', { name: /sign out/i });
    await user.click(signOutButton);
    
    expect(mockSignOut).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/');
  });

  it('renders documentation link', () => {
    render(<HeaderWithRouter />);
    const docLink = screen.getByText('Documentation');
    expect(docLink).toBeInTheDocument();
    expect(docLink.getAttribute('href')).toBe('https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview');
  });

  it('highlights the active navigation link based on current path', async () => {
    // Set the mock pathname to /billing for this test
    mockPathname = '/billing';
    
    render(<HeaderWithRouter />);
    
    // The Billing link should have the active class
    const billingLink = screen.getByText('Billing').closest('a');
    expect(billingLink).toHaveClass('bg-primary/10');
    expect(billingLink).toHaveClass('text-primary');
  });
}); 