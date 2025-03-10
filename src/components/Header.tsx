import React from 'react';
import { FileTextIcon, LayoutDashboard, FolderIcon, SearchIcon, CreditCard } from 'lucide-react';
import { Button } from './ui/button';
import { useAuth, useUser } from '@clerk/clerk-react';
import { Link, useNavigate, useLocation } from 'react-router-dom';

const Header: React.FC = () => {
  const { isSignedIn, signOut } = useAuth();
  const { user } = useUser();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSignOut = async () => {
    await signOut();
    navigate('/');
  };

  return (
    <header className="w-full py-4 px-6 border-b border-border/40 backdrop-blur-sm bg-background/80 fixed top-0 z-10">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Link to="/" className="flex items-center space-x-2">
            <div className="bg-primary/10 p-2 rounded-lg">
              <FileTextIcon className="h-6 w-6 text-primary" />
            </div>
            <h1 className="text-xl font-medium">
              Document Intelligence
            </h1>
          </Link>
        </div>
        <div className="flex items-center space-x-4">
          {isSignedIn && (
            <nav className="hidden md:flex items-center mr-4">
              <Link 
                to="/" 
                className={`px-3 py-2 text-sm rounded-md transition-colors ${
                  location.pathname === '/' 
                    ? 'bg-primary/10 text-primary' 
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                Home
              </Link>
              <Link 
                to="/dashboard" 
                className={`px-3 py-2 text-sm rounded-md transition-colors flex items-center gap-1 ${
                  location.pathname === '/dashboard' 
                    ? 'bg-primary/10 text-primary' 
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <LayoutDashboard className="h-4 w-4" />
                Dashboard
              </Link>
              <Link 
                to="/folders" 
                className={`px-3 py-2 text-sm rounded-md transition-colors flex items-center gap-1 ${
                  location.pathname === '/folders' || location.pathname.startsWith('/folders/') 
                    ? 'bg-primary/10 text-primary' 
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <FolderIcon className="h-4 w-4" />
                Folders
              </Link>
              <Link 
                to="/search" 
                className={`px-3 py-2 text-sm rounded-md transition-colors flex items-center gap-1 ${
                  location.pathname === '/search' 
                    ? 'bg-primary/10 text-primary' 
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <SearchIcon className="h-4 w-4" />
                Search
              </Link>
              <Link 
                to="/billing" 
                className={`px-3 py-2 text-sm rounded-md transition-colors flex items-center gap-1 ${
                  location.pathname === '/billing' 
                    ? 'bg-primary/10 text-primary' 
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <CreditCard className="h-4 w-4" />
                Billing
              </Link>
            </nav>
          )}
          
          <a 
            href="https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Documentation
          </a>
          
          {isSignedIn ? (
            <div className="flex items-center gap-4">
              <span className="text-sm">Hello, {user?.firstName || 'User'}</span>
              <Button variant="outline" onClick={handleSignOut}>
                Sign Out
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Button variant="outline" asChild>
                <Link to="/sign-in">Sign In</Link>
              </Button>
              <Button asChild>
                <Link to="/sign-up">Sign Up</Link>
              </Button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
