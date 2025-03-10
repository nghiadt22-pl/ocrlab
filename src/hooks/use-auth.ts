import { useAuth as useClerkAuth, useUser } from "@clerk/clerk-react";

export function useAuth() {
  const { isLoaded, userId, sessionId } = useClerkAuth();
  const { user } = useUser();
  
  return {
    isLoaded,
    isAuthenticated: isLoaded && !!userId && !!sessionId,
    userId,
    sessionId,
    user
  };
} 