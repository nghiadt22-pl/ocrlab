import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PublicRoute } from "@/components/auth/PublicRoute";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import SignInPage from "./pages/SignIn";
import SignUpPage from "./pages/SignUp";
import Dashboard from "./pages/Dashboard";
import Folders from "./pages/Folders";
import FolderFiles from "./pages/FolderFiles";
import Search from "./pages/Search";

const App = () => (
  <TooltipProvider>
    <Toaster />
    <Sonner />
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Index />} />
      <Route 
        path="/sign-in/*" 
        element={
          <PublicRoute>
            <SignInPage />
          </PublicRoute>
        } 
      />
      <Route 
        path="/sign-up/*" 
        element={
          <PublicRoute>
            <SignUpPage />
          </PublicRoute>
        } 
      />
      
      {/* Protected routes */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/folders" 
        element={
          <ProtectedRoute>
            <Folders />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/folders/:folderId" 
        element={
          <ProtectedRoute>
            <FolderFiles />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/search" 
        element={
          <ProtectedRoute>
            <Search />
          </ProtectedRoute>
        } 
      />
      
      {/* Catch-all route */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  </TooltipProvider>
);

export default App;
