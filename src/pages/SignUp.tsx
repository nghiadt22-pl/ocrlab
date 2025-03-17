import { SignUp } from "@clerk/clerk-react";
import React from "react";
import { FileTextIcon } from "lucide-react";
import { Link } from "react-router-dom";

const SignUpPage: React.FC = () => {
  return (
    <div className="min-h-screen flex">
      {/* Left side - Brand */}
      <div className="hidden lg:flex lg:w-1/2 bg-sidebar items-center justify-center p-12">
        <div className="max-w-md text-center">
          <div className="flex justify-center mb-6">
            <div className="bg-sidebar-accent/20 p-4 rounded-xl">
              <FileTextIcon className="h-12 w-12 text-sidebar-accent" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-white mb-4">OCR LAB</h1>
          <p className="text-sidebar-foreground/80 text-lg mb-8">
            Advanced OCR extraction with semantic search capabilities for all your document needs
          </p>
          <div className="grid grid-cols-2 gap-4 mt-12">
            <div className="bg-sidebar-accent/10 p-6 rounded-lg">
              <h3 className="text-xl font-medium text-white mb-2">Table Extraction</h3>
              <p className="text-sidebar-foreground/70">Extract structured data from tables in your documents</p>
            </div>
            <div className="bg-sidebar-accent/10 p-6 rounded-lg">
              <h3 className="text-xl font-medium text-white mb-2">Semantic Search</h3>
              <p className="text-sidebar-foreground/70">Find information using natural language queries</p>
            </div>
            <div className="bg-sidebar-accent/10 p-6 rounded-lg">
              <h3 className="text-xl font-medium text-white mb-2">Handwriting OCR</h3>
              <p className="text-sidebar-foreground/70">Convert handwritten text to digital format</p>
            </div>
            <div className="bg-sidebar-accent/10 p-6 rounded-lg">
              <h3 className="text-xl font-medium text-white mb-2">Image Analysis</h3>
              <p className="text-sidebar-foreground/70">Extract and describe content from images</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Right side - Sign Up */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-background">
        <div className="w-full max-w-md">
          <div className="flex lg:hidden justify-center mb-8">
            <div className="flex items-center space-x-2">
              <div className="bg-primary/10 p-2 rounded-lg">
                <FileTextIcon className="h-6 w-6 text-primary" />
              </div>
              <h1 className="text-2xl font-bold">OCR LAB</h1>
            </div>
          </div>
          
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold">Create an account</h2>
            <p className="text-muted-foreground mt-2">Sign up to get started with OCR LAB</p>
          </div>
          
          <div className="bg-card rounded-xl shadow-sm border border-border p-8">
            <SignUp routing="path" path="/sign-up" signInUrl="/sign-in" />
            
            <div className="mt-6 text-center text-sm">
              <p className="text-muted-foreground">
                Already have an account?{" "}
                <Link to="/sign-in" className="text-primary font-medium hover:underline">
                  Sign in
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignUpPage;
