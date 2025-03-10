import { Loader2 } from "lucide-react";

interface LoadingProps {
  size?: number;
  className?: string;
}

export function Loading({ size = 24, className = "" }: LoadingProps) {
  return (
    <div className={`flex items-center justify-center ${className}`}>
      <Loader2 className="animate-spin" size={size} />
    </div>
  );
}

export function FullPageLoading() {
  return (
    <div className="flex items-center justify-center h-screen">
      <Loading size={32} />
      <span className="ml-2 text-lg font-medium">Loading...</span>
    </div>
  );
} 