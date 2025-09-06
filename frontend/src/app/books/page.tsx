"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Header from "../../components/Header";

interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

export default function BooksPage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem("access_token");
      const tokenType = localStorage.getItem("token_type");

      if (!token) {
        router.push("/auth/login");
        return;
      }

      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/me`, {
          headers: {
            "Authorization": `${tokenType} ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Authentication failed");
        }

        const userData = await response.json();
        setUser(userData);
      } catch (error) {
        console.error("Auth check failed:", error);
        localStorage.removeItem("access_token");
        localStorage.removeItem("token_type");
        router.push("/auth/login");
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            📚 Library Dashboard
          </h2>
          <p className="text-xl text-gray-600">
            Welcome to your library management system
          </p>
        </div>

        {/* Success Message */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-8">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-medium text-green-800">
                🎉 Authentication Successful!
              </h3>
              <div className="mt-2 text-sm text-green-700">
                <p>You are successfully connected to the backend API!</p>
                <ul className="mt-2 list-disc list-inside">
                  <li>✅ Login working correctly</li>
                  <li>✅ Token authentication functional</li>
                  <li>✅ User data retrieved from API</li>
                  <li>✅ Frontend-Backend connection established</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* User Info Card */}
        <div className="bg-white shadow-lg rounded-lg p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Account Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span className="text-sm font-medium text-gray-500">Name:</span>
              <p className="mt-1 text-sm text-gray-900">{user?.full_name}</p>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-500">Email:</span>
              <p className="mt-1 text-sm text-gray-900">{user?.email}</p>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-500">Role:</span>
              <p className="mt-1 text-sm text-gray-900 capitalize">{user?.role}</p>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-500">Status:</span>
              <p className="mt-1 text-sm text-gray-900">
                {user?.is_active ? (
                  <span className="text-green-600">Active</span>
                ) : (
                  <span className="text-red-600">Inactive</span>
                )}
              </p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-blue-600 text-4xl mb-4">📖</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Browse Books</h3>
            <p className="text-gray-600 text-sm mb-4">Explore our collection of books</p>
            <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm">
              Coming Soon
            </button>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-blue-600 text-4xl mb-4">👤</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">My Account</h3>
            <p className="text-gray-600 text-sm mb-4">Manage your profile and settings</p>
            <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm">
              Coming Soon
            </button>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="text-blue-600 text-4xl mb-4">📊</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Dashboard</h3>
            <p className="text-gray-600 text-sm mb-4">View your activity and statistics</p>
            <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm">
              Coming Soon
            </button>
          </div>
        </div>

        {/* API Connection Status */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-900 mb-2">🔗 API Connection Status</h4>
          <div className="text-sm text-blue-700">
            <p>✅ Successfully connected to: <code className="bg-white px-2 py-1 rounded text-xs">{process.env.NEXT_PUBLIC_API_URL}</code></p>
            <p>✅ Authentication working correctly</p>
            <p>✅ Frontend deployed to Google Cloud Run</p>
            <p>✅ Backend API responding properly</p>
          </div>
        </div>
      </div>
    </div>
  );
}
