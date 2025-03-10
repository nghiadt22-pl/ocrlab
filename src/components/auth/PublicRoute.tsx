import { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/hooks/use-auth";
import { FullPageLoading } from "@/components/ui/loading";

interface PublicRouteProps {
  children: ReactNode;
  redirectAuthenticated?: boolean;
}

export function PublicRoute({ 
  children, 
  redirectAuthenticated = true 
}: PublicRouteProps) {
  const { isLoaded, isAuthenticated } = useAuth();
  const location = useLocation();
  
  // Get the redirect path from location state or default to dashboard
  const from = location.state?.from?.pathname || "/dashboard";

  // Show loading state while Clerk is initializing
  if (!isLoaded) {
    return <FullPageLoading />;
  }

  // Redirect to dashboard if already authenticated (for login/signup pages)
  if (redirectAuthenticated && isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  // Render children for public routes
  return <>{children}</>;
} 