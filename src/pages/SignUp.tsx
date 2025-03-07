
import { SignUp } from "@clerk/clerk-react";
import React from "react";

const SignUpPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md p-8 space-y-8 bg-card rounded-xl shadow-lg">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold">Sign Up</h1>
          <p className="text-muted-foreground mt-2">Create your Document Intelligence account</p>
        </div>
        <SignUp routing="path" path="/sign-up" signInUrl="/sign-in" />
      </div>
    </div>
  );
};

export default SignUpPage;
