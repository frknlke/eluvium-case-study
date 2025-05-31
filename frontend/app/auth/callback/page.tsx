"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { SyncMethod, Provider } from "@/lib/types";

// Backend API URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Utility function for exponential backoff retry
const fetchWithRetry = async (url: string, options: RequestInit, maxRetries = 5) => {
  let retries = 0;
  let lastError;

  while (retries < maxRetries) {
    try {
      const response = await fetch(url, options);
      if (response.ok) {
        return response;
      }
      
      // Get error details
      const errorData = await response.json();
      lastError = new Error(errorData.detail || "API request failed");
      
      // If there's a provider_enum error, try with 'gmail' instead of 'google'
      if (errorData.detail && errorData.detail.includes("provider_enum")) {
        const body = JSON.parse(options.body as string);
        body.provider = 'gmail'; // Match the PostgreSQL enum exactly
        options.body = JSON.stringify(body);
      }
    } catch (error: any) {
      lastError = error;
    }
    
    // Calculate delay with exponential backoff: 2^retries * 100ms
    const delay = Math.min(Math.pow(2, retries) * 100, 3000); // Cap at 3 seconds
    console.log(`Retry ${retries + 1}/${maxRetries} after ${delay}ms`);
    
    // Wait for the delay
    await new Promise(resolve => setTimeout(resolve, delay));
    
    // Increment retry counter
    retries++;
  }
  
  // All retries failed
  throw lastError;
};

export default function AuthCallback() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const processOAuthCallback = async () => {
      if (status === "authenticated" && session && !isProcessing) {
        setIsProcessing(true);
        
        try {
          // Get form data from session storage
          const formDataStr = sessionStorage.getItem('mailboxFormData');
          if (!formDataStr) {
            throw new Error("Form data not found. Please try again.");
          }
          
          const formData = JSON.parse(formDataStr);
          
          // Get OAuth tokens from session
          const accessToken = (session as any)?.accessToken;
          const refreshToken = (session as any)?.refreshToken;
          const expiresAt = (session as any)?.expiresAt;
          const email = session.user?.email;
          
          if (!accessToken || !refreshToken || !email) {
            throw new Error("OAuth data incomplete. Please try again.");
          }
          
          // Convert expiry timestamp to date if available
          const tokenExpiry = expiresAt ? new Date(expiresAt * 1000).toISOString() : null;
          
          // Save to backend database via API with retry logic
          const response = await fetchWithRetry(
            `${API_URL}/api/mailbox/`,
            {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                email_address: email,
                // Use 'gmail' to match the PostgreSQL provider_enum
                provider: 'gmail',
                access_token: accessToken,
                refresh_token: refreshToken,
                token_expiry: tokenExpiry,
                // Match a valid sync_method in PostgreSQL
                sync_method: 'polling'
              }),
            },
            5 // 5 max retries
          );
          
          // Clear session storage
          sessionStorage.removeItem('mailboxFormData');
          
          // Redirect to success page
          router.push('/dashboard');
        } catch (err: any) {
          console.error("Error in auth callback:", err);
          setError(err.message || "An error occurred while processing your request");
          setIsProcessing(false);
        }
      }
    };
    
    processOAuthCallback();
  }, [status, session, router, isProcessing]);

  if (status === "loading" || isProcessing) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-24">
        <div className="z-10 w-full max-w-5xl items-center justify-center font-mono text-sm flex flex-col">
          <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md text-center">
            <h2 className="text-2xl font-semibold mb-6">Processing...</h2>
            <p className="text-gray-600 mb-4">Please wait while we process your authentication.</p>
            <div className="flex justify-center">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-24">
        <div className="z-10 w-full max-w-5xl items-center justify-center font-mono text-sm flex flex-col">
          <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
            <h2 className="text-2xl font-semibold mb-6 text-center text-red-600">Error</h2>
            <p className="text-gray-800 mb-6">{error}</p>
            <button
              onClick={() => router.push('/')}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-4 rounded-lg transition duration-300"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
} 