"use client";

import { signIn, signOut, useSession } from "next-auth/react";
import Link from "next/link";
import MailboxForm from "@/components/MailboxForm";

export default function Home() {
  const { data: session, status } = useSession();
  const isAuthenticated = status === "authenticated";

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-center font-mono text-sm flex flex-col">
        <h1 className="text-4xl font-bold mb-8">Eluvium Gmail OAuth</h1>
        
        {!isAuthenticated ? (
          <MailboxForm />
        ) : (
          <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
            <h2 className="text-2xl font-semibold mb-6 text-center">Successfully Authenticated</h2>
            <div className="mb-6">
              <div className="mb-4">
                <p className="font-semibold">Email:</p>
                <p className="text-gray-700">{session?.user?.email}</p>
              </div>
              <div className="mb-4">
                <p className="font-semibold">Name:</p>
                <p className="text-gray-700">{session?.user?.name}</p>
              </div>
              <div className="mb-4">
                <p className="font-semibold">Access Token:</p>
                <p className="text-gray-700 break-all text-xs">
                  {(session as any)?.accessToken ? `${(session as any).accessToken.substring(0, 40)}...` : "No access token"}
                </p>
              </div>
            </div>
            <div className="flex flex-col space-y-3">
              <Link href="/dashboard" className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-lg transition duration-300 text-center">
                Go to Dashboard
              </Link>
              <button
                onClick={() => signOut()}
                className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg transition duration-300"
              >
                Sign Out
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
