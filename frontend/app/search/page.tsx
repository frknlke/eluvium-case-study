"use client";

import { useState } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

// Backend API URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Entity types we support filtering on
const ENTITY_TYPES = [
  { key: 'PERSON', label: 'People' },
  { key: 'ORG', label: 'Organizations' },
  { key: 'LOC', label: 'Locations' },
  { key: 'DATE', label: 'Dates' },
  { key: 'MONEY', label: 'Money' },
];

export default function SearchPage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  // Search form state
  const [query, setQuery] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [selectedEntities, setSelectedEntities] = useState<{[key: string]: string[]}>({});
  const [entityInput, setEntityInput] = useState<{[key: string]: string}>({});
  
  // Results state
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Add entity value to filter
  const addEntityValue = (type: string, value: string) => {
    if (!value.trim()) return;
    
    setSelectedEntities(prev => ({
      ...prev,
      [type]: [...(prev[type] || []), value.trim()]
    }));
    
    setEntityInput(prev => ({
      ...prev,
      [type]: ''
    }));
  };

  // Remove entity value from filter
  const removeEntityValue = (type: string, value: string) => {
    setSelectedEntities(prev => ({
      ...prev,
      [type]: prev[type]?.filter(v => v !== value) || []
    }));
  };

  // Handle search submission
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // Prepare search payload
      const searchPayload = {
        query: query,
        entities: Object.entries(selectedEntities)
          .filter(([_, values]) => values.length > 0)
          .reduce((acc, [key, values]) => ({...acc, [key]: values}), {}),
        date_from: dateFrom ? new Date(dateFrom).toISOString() : null,
        date_to: dateTo ? new Date(dateTo).toISOString() : null,
        limit: 10
      };
      
      const response = await fetch(`${API_URL}/api/search/advanced`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchPayload),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Search failed");
      }
      
      const data = await response.json();
      setResults(data);
    } catch (err: any) {
      console.error("Search error:", err);
      setError(err.message || "Failed to search");
    } finally {
      setLoading(false);
    }
  };

  // Parse metadata to a more usable format
  const parseMetadata = (metadata: any) => {
    const parsed: any = {};
    
    for (const [key, value] of Object.entries(metadata)) {
      if (typeof value === 'string' && (value.startsWith('[') || value.startsWith('{'))) {
        try {
          parsed[key] = JSON.parse(value as string);
        } catch (e) {
          parsed[key] = value;
        }
      } else {
        parsed[key] = value;
      }
    }
    
    return parsed;
  };

  // Redirect if not authenticated
  if (status === "unauthenticated") {
    router.push("/");
    return null;
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-6 md:p-24">
      <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-4xl">
        <h1 className="text-3xl font-bold mb-6">Advanced Email Search</h1>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSearch} className="mb-8">
          {/* Main search query */}
          <div className="mb-6">
            <label htmlFor="query" className="block text-gray-700 font-medium mb-2">
              Search Query
            </label>
            <input
              type="text"
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter search terms..."
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>
          
          {/* Date range filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label htmlFor="dateFrom" className="block text-gray-700 font-medium mb-2">
                From Date
              </label>
              <input
                type="date"
                id="dateFrom"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label htmlFor="dateTo" className="block text-gray-700 font-medium mb-2">
                To Date
              </label>
              <input
                type="date"
                id="dateTo"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          
          {/* Entity filters */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-3">Filter by Entities</h2>
            
            <div className="space-y-4">
              {ENTITY_TYPES.map(entity => (
                <div key={entity.key} className="border rounded-lg p-4 bg-gray-50">
                  <h3 className="font-medium mb-2">{entity.label}</h3>
                  
                  {/* Selected entity values */}
                  <div className="flex flex-wrap gap-2 mb-3">
                    {selectedEntities[entity.key]?.map(value => (
                      <span 
                        key={value} 
                        className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm flex items-center"
                      >
                        {value}
                        <button 
                          type="button"
                          onClick={() => removeEntityValue(entity.key, value)}
                          className="ml-1 text-blue-600 hover:text-blue-800"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  
                  {/* Add new entity value */}
                  <div className="flex">
                    <input
                      type="text"
                      value={entityInput[entity.key] || ''}
                      onChange={(e) => setEntityInput(prev => ({
                        ...prev,
                        [entity.key]: e.target.value
                      }))}
                      placeholder={`Add ${entity.label.slice(0, -1)}...`}
                      className="flex-grow p-2 border border-gray-300 rounded-l-lg focus:ring-blue-500 focus:border-blue-500"
                    />
                    <button
                      type="button"
                      onClick={() => addEntityValue(entity.key, entityInput[entity.key] || '')}
                      className="bg-blue-500 text-white px-4 py-2 rounded-r-lg hover:bg-blue-600"
                    >
                      Add
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Submit button */}
          <div className="flex justify-center">
            <button
              type="submit"
              disabled={loading}
              className={`${
                loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600'
              } text-white font-bold py-3 px-6 rounded-lg transition duration-300 w-full md:w-auto`}
            >
              {loading ? 'Searching...' : 'Search Emails'}
            </button>
          </div>
        </form>
        
        {/* Search results */}
        <div className="mt-8">
          <h2 className="text-2xl font-semibold mb-4">
            Results {results.length > 0 ? `(${results.length})` : ''}
          </h2>
          
          {results.length === 0 ? (
            <p className="text-gray-500">
              {loading ? 'Searching...' : 'No results found. Try a different search query.'}
            </p>
          ) : (
            <div className="space-y-6">
              {results.map((result, index) => {
                const metadata = parseMetadata(result.metadata);
                return (
                  <div key={index} className="border rounded-lg p-4 bg-gray-50">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-medium">
                        {metadata.subject || `Email ${index + 1}`}
                      </h3>
                      <span className="text-sm text-gray-500">
                        {metadata.date ? new Date(metadata.date as string).toLocaleDateString() : 'Unknown date'}
                      </span>
                    </div>
                    
                    {/* Email snippet */}
                    <p className="text-gray-700 mb-3">
                      {result.document?.substring(0, 150)}...
                    </p>
                    
                    {/* Entity tags */}
                    <div className="mt-3">
                      {Object.entries(metadata).map(([key, value]) => {
                        if (ENTITY_TYPES.some(e => e.key === key) && Array.isArray(value)) {
                          return (
                            <div key={key} className="mt-1">
                              <span className="text-sm font-medium text-gray-700">{key}: </span>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {value.map((entity: string, i: number) => (
                                  <span 
                                    key={i}
                                    className="bg-gray-200 text-gray-800 px-2 py-1 rounded-full text-xs"
                                  >
                                    {entity}
                                  </span>
                                ))}
                              </div>
                            </div>
                          );
                        }
                        return null;
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
        
        {/* Navigation */}
        <div className="flex justify-center mt-8">
          <Link 
            href="/dashboard" 
            className="inline-block bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-6 rounded-lg transition duration-300"
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    </main>
  );
} 