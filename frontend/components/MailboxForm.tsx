"use client";

import { useState } from 'react';
import { Provider, SyncMethod, MailboxFormData } from '@/lib/types';
import { signIn } from 'next-auth/react';

export default function MailboxForm() {
  const [formData, setFormData] = useState<MailboxFormData>({
    syncMethod: SyncMethod.API,
    provider: Provider.GOOGLE
  });
  
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Store form data in session storage to retrieve after OAuth redirect
    sessionStorage.setItem('mailboxFormData', JSON.stringify(formData));
    
    // Use a fixed callback URL with port 3000
    const callbackUrl = 'http://localhost:3000/auth/callback';
    
    // Redirect to Google OAuth
    signIn('google', { callbackUrl });
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
      <h2 className="text-2xl font-semibold mb-6 text-center">Mailbox Configuration</h2>
      
      {validationError && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
          {validationError}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-6">
          <label htmlFor="syncMethod" className="block text-sm font-medium text-gray-700 mb-1">
            Sync Method
          </label>
          <select
            id="syncMethod"
            name="syncMethod"
            value={formData.syncMethod}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={SyncMethod.API}>API</option>
            <option value={SyncMethod.IMAP}>IMAP</option>
            <option value={SyncMethod.POP3}>POP3</option>
          </select>
        </div>
        
        <button
          type="submit"
          className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-4 rounded-lg transition duration-300"
        >
          Continue to Google Sign-in
        </button>
      </form>
    </div>
  );
} 