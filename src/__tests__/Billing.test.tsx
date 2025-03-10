import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Billing from '../pages/Billing';

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
}));

// Mock the Header component
vi.mock('../components/Header', () => ({
  default: () => <div data-testid="mock-header">Header</div>,
}));

// Wrapper component to provide router context
const BillingWithRouter = () => (
  <BrowserRouter>
    <Billing />
  </BrowserRouter>
);

describe('Billing Component', () => {
  it('renders the billing page title', () => {
    render(<BillingWithRouter />);
    expect(screen.getByText('Billing & Subscription')).toBeInTheDocument();
  });

  it('renders the tabs correctly', () => {
    render(<BillingWithRouter />);
    expect(screen.getByRole('tab', { name: /overview/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /invoices/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /plans/i })).toBeInTheDocument();
  });

  it('displays current plan information in the overview tab', () => {
    render(<BillingWithRouter />);
    expect(screen.getByText('Current Plan')).toBeInTheDocument();
    expect(screen.getByText('Professional')).toBeInTheDocument();
    expect(screen.getByText('Monthly')).toBeInTheDocument();
  });

  it('displays payment method information in the overview tab', () => {
    render(<BillingWithRouter />);
    expect(screen.getByText('Payment Method')).toBeInTheDocument();
    expect(screen.getByText('Visa ending in 4242')).toBeInTheDocument();
  });

  it('displays usage and limits information in the overview tab', () => {
    render(<BillingWithRouter />);
    expect(screen.getByText('Usage & Limits')).toBeInTheDocument();
    expect(screen.getByText('Pages Processed')).toBeInTheDocument();
    expect(screen.getByText('Storage Used (GB)')).toBeInTheDocument();
    expect(screen.getByText('API Calls')).toBeInTheDocument();
  });

  it('switches to invoices tab when clicked', async () => {
    render(<BillingWithRouter />);
    const user = userEvent.setup();
    
    // Click on the Invoices tab
    await user.click(screen.getByRole('tab', { name: /invoices/i }));
    
    // Check that the invoices content is displayed
    expect(screen.getByText('Billing History')).toBeInTheDocument();
    expect(screen.getByText('View and download your past invoices')).toBeInTheDocument();
    
    // Check for table headers
    expect(screen.getByRole('columnheader', { name: /invoice/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /date/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /amount/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /status/i })).toBeInTheDocument();
  });

  it('switches to plans tab when clicked', async () => {
    render(<BillingWithRouter />);
    const user = userEvent.setup();
    
    // Click on the Plans tab
    await user.click(screen.getByRole('tab', { name: /plans/i }));
    
    // Check that the plans content is displayed
    expect(screen.getByText('Basic')).toBeInTheDocument();
    expect(screen.getByText('Professional')).toBeInTheDocument();
    expect(screen.getByText('Enterprise')).toBeInTheDocument();
    
    // Check for plan prices
    expect(screen.getByText('$9.99/month')).toBeInTheDocument();
    expect(screen.getByText('$29.99/month')).toBeInTheDocument();
    expect(screen.getByText('$99.99/month')).toBeInTheDocument();
  });

  it('toggles auto-renew switch when clicked', async () => {
    render(<BillingWithRouter />);
    const user = userEvent.setup();
    
    // Find the switch by its label text instead of role
    const switchLabel = screen.getByText('Auto-renew');
    expect(switchLabel).toBeInTheDocument();
    
    // Find the switch element near the label
    const switchContainer = switchLabel.closest('div')?.parentElement;
    const switchElement = switchContainer?.querySelector('button[role="switch"]');
    
    expect(switchElement).not.toBeNull();
    
    // Click the switch to toggle it
    if (switchElement) {
      await user.click(switchElement);
      
      // Check that the text changed to Off
      expect(screen.getByText('Off')).toBeInTheDocument();
    }
  });
}); 