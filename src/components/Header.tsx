
import React from 'react';
import { FileTextIcon } from 'lucide-react';
import { Button } from './ui/button';
import { useAuth, useUser } from '@clerk/clerk-react';
import { Link, useNavigate } from 'react-router-dom';

const Header: React.FC = () => {
  const { isSignedIn, signOut } = useAuth();
  const { user } = useUser();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    await signOut();
    navigate('/');
  };

  return (
    <header className="w-full py-4 px-6 border-b border-border/40 backdrop-blur-sm bg-background/80 fixed top-0 z-10">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="bg-primary/10 p-2 rounded-lg">
            <FileTextIcon className="h-6 w-6 text-primary" />
          </div>
          <h1 className="text-xl font-medium">
            Document Intelligence
          </h1>
        </div>
        <div className="flex items-center space-x-4">
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
