"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Mailbox } from "@/lib/types";

// Backend API URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Dashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [mailboxes, setMailboxes] = useState<Mailbox[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showingEmbeddings, setShowingEmbeddings] = useState(false);
  const [embeddingsCount, setEmbeddingsCount] = useState<number | null>(null);

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/");
    }
    
    if (status === "authenticated") {
      fetchMailboxes();
    }
  }, [status, router]);

  const fetchMailboxes = async () => {
    try {
      const response = await fetch(`${API_URL}/api/mailbox/`);
      if (!response.ok) {
        throw new Error("Failed to fetch mailboxes");
      }
      const data = await response.json();
      
      // Convert snake_case from API to camelCase for frontend
      const formattedMailboxes = data.map((mailbox: any) => ({
        id: mailbox.id,
        companyId: mailbox.company_id,
        emailAddress: mailbox.email_address,
        provider: mailbox.provider,
        syncMethod: mailbox.sync_method,
        syncStatus: mailbox.sync_status,
        lastSyncedAt: mailbox.last_synced_at,
        createdAt: mailbox.created_at,
        updatedAt: mailbox.updated_at
      }));
      
      setMailboxes(formattedMailboxes);
    } catch (err) {
      console.error("Error fetching mailboxes:", err);
      setError("Failed to load mailboxes");
    } finally {
      setLoading(false);
    }
  };

  const handleProcessEmails = async (mailboxId: string) => {
    setProcessing(mailboxId);
    try {
      const response = await fetch(`${API_URL}/api/mailbox/trigger-email-processing/${mailboxId}`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to process emails");
      }
      
      // Success notification could be added here
      alert("Email processing triggered successfully");
    } catch (err: any) {
      console.error("Error processing emails:", err);
      setError(err.message || "Failed to process emails");
    } finally {
      setProcessing(null);
    }
  };

  const handleShowEmbeddings = async () => {
    setShowingEmbeddings(true);
    try {
      const response = await fetch(`${API_URL}/api/search/print-embeddings`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to print embeddings");
      }
      
      const data = await response.json();
      setEmbeddingsCount(data.count);
      
      // Show success message
      alert(`Successfully printed ${data.count} embeddings to the backend console`);
    } catch (err: any) {
      console.error("Error showing embeddings:", err);
      setError(err.message || "Failed to print embeddings");
    } finally {
      setShowingEmbeddings(false);
    }
  };

  if (status === "loading" || loading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center">
        <p>Loading...</p>
      </div>
    );
  }

  if (status === "unauthenticated") {
    return null; // Will redirect in useEffect
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-2xl">
        <h1 className="text-4xl font-bold mb-6 text-center">Welcome to Dashboard</h1>
        <p className="text-xl mb-8 text-center">
          Your Google account has been successfully connected!
        </p>
        <p className="mb-6 text-center">
          Email: <span className="font-semibold">{session?.user?.email}</span>
        </p>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <div className="my-6">
          <h2 className="text-2xl font-semibold mb-4">Your Mailboxes</h2>
          {mailboxes.length === 0 ? (
            <p className="text-gray-500">No mailboxes found.</p>
          ) : (
            <div className="space-y-4">
              {mailboxes.map((mailbox) => (
                <div key={mailbox.id} className="border rounded-lg p-4 bg-gray-50">
                  <p className="font-medium">{mailbox.emailAddress}</p>
                  <div className="flex justify-between items-center mt-2">
                    <div>
                      <span className="text-sm text-gray-500">Provider: {mailbox.provider}</span>
                      <span className="text-sm text-gray-500 ml-4">Status: {mailbox.syncStatus}</span>
                    </div>
                    <button
                      onClick={() => handleProcessEmails(mailbox.id)}
                      disabled={processing === mailbox.id}
                      className={`${
                        processing === mailbox.id 
                          ? 'bg-gray-400 cursor-not-allowed' 
                          : 'bg-blue-500 hover:bg-blue-600'
                      } text-white font-bold py-2 px-4 rounded-lg transition duration-300`}
                    >
                      {processing === mailbox.id ? 'Processing...' : 'Process my emails'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Advanced Email Search Button */}
        <div className="my-6 flex justify-center">
          <Link 
            href="/search" 
            className="inline-block bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-lg transition duration-300"
          >
            Advanced Email Search
          </Link>
        </div>
        
        {/* Embeddings section */}
        <div className="my-8 border-t pt-6">
          <h2 className="text-2xl font-semibold mb-4">Vector Database</h2>
          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-700">
                Print all embeddings to the backend console
                {embeddingsCount !== null && (
                  <span className="ml-2 text-sm text-gray-500">
                    Last count: {embeddingsCount} embeddings
                  </span>
                )}
              </p>
            </div>
            <button
              onClick={handleShowEmbeddings}
              disabled={showingEmbeddings}
              className={`${
                showingEmbeddings
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-green-500 hover:bg-green-600'
              } text-white font-bold py-2 px-4 rounded-lg transition duration-300`}
            >
              {showingEmbeddings ? 'Processing...' : 'Show Embeddings'}
            </button>
          </div>
        </div>
        
        <div className="flex justify-center mt-8">
          <Link 
            href="/" 
            className="inline-block bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-6 rounded-lg transition duration-300"
          >
            Back to Home
          </Link>
        </div>
      </div>
    </main>
  );
} 