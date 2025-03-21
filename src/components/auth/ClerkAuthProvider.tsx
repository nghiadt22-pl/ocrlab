import { useAuth } from "@clerk/clerk-react";
import { useEffect } from "react";

export function ClerkAuthProvider({ children }: { children: React.ReactNode }) {
  const { getToken, userId, isLoaded } = useAuth();

  // Store the token and user ID in localStorage when they change
  useEffect(() => {
    const storeAuthData = async () => {
      if (isLoaded && userId) {
        try {
          // Get the token from Clerk
          const token = await getToken();
          
          // Store the token and user ID in localStorage
          if (token) {
            localStorage.setItem('clerk-token', token);
          }
          
          localStorage.setItem('userId', userId);
        } catch (error) {
          console.error('Error storing auth data:', error);
        }
      }
    };

    storeAuthData();
  }, [getToken, userId, isLoaded]);

  // Clear the token and user ID when the component unmounts
  useEffect(() => {
    return () => {
      if (!userId) {
        localStorage.removeItem('clerk-token');
        localStorage.removeItem('userId');
      }
    };
  }, [userId]);

  return <>{children}</>;
} 