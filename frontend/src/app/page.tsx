import Link from "next/link";
import Header from "../components/Header";

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <Header />

      {/* Hero Section - Water background effect */}
      <section 
        className="relative py-24 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.6)), url('/library-hero.jpg')`
        }}
      >
        {/* Background overlay for better text readability */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-900/80 to-indigo-900/80"></div>
        
        {/* Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl font-bold text-white sm:text-7xl drop-shadow-lg">
              Modern Library
              <span className="text-blue-300"> Management</span>
            </h1>
            <p className="mt-8 text-xl text-gray-100 max-w-3xl mx-auto drop-shadow-md">
              A comprehensive digital library system with book management, user authentication, 
              loan tracking, holds, fines, and automated notifications.
            </p>
            <div className="mt-12 flex items-center justify-center gap-x-6">
              <Link
                href="/books"
                className="bg-blue-500/90 backdrop-blur-sm px-8 py-4 text-lg font-semibold text-white rounded-lg hover:bg-blue-600/90 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                Browse Books
              </Link>
              <Link 
                href={`${process.env.NEXT_PUBLIC_API_URL}/docs`}
                className="text-lg text-white hover:text-blue-300 transition-colors drop-shadow-md border border-white/30 px-6 py-3 rounded-lg backdrop-blur-sm hover:border-blue-300/50"
              >
                API Documentation →
              </Link>
            </div>
          </div>
        </div>
        
        {/* Subtle watermark effect */}
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-gray-900 to-transparent"></div>
      </section>

      {/* Features Section */}
      <main className="bg-gradient-to-br from-blue-50 to-indigo-100 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl">
              Comprehensive Library Features
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Everything you need to manage a modern library efficiently
            </p>
          </div>

          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 text-2xl mb-4">📖</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Book Management</h3>
              <p className="text-gray-600">Complete catalog with search, filtering, and availability tracking</p>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 text-2xl mb-4">👥</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">User Management</h3>
              <p className="text-gray-600">Role-based access control for Members, Librarians, and Admins</p>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 text-2xl mb-4">🔄</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Loan System</h3>
              <p className="text-gray-600">Book borrowing, renewals, returns, and automated tracking</p>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 text-2xl mb-4">📋</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Holds & Reservations</h3>
              <p className="text-gray-600">Queue management with automatic notifications</p>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 text-2xl mb-4">💰</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Fine Management</h3>
              <p className="text-gray-600">Automatic calculation and payment processing</p>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 text-2xl mb-4">🔔</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Notifications</h3>
              <p className="text-gray-600">Automated alerts for due dates and availability</p>
            </div>
          </div>
        </div>
      </main>

      {/* Demo Section */}
      <section className="bg-blue-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">🚀 Try the Demo</h3>
          <p className="text-gray-600 mb-6">Experience the full functionality with sample data</p>
          
          <div className="bg-white rounded-lg shadow-sm p-6 max-w-md mx-auto">
            <div className="space-y-2 text-sm text-gray-700">
              <div><span className="font-medium">Admin:</span> admin@library.com</div>
              <div><span className="font-medium">Librarian:</span> librarian@library.com</div>
              <div><span className="font-medium">Member:</span> member@library.com</div>
              <div className="text-xs text-gray-500 mt-3">Password: password123</div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-lg">&copy; 2025 Library Management System. Built with ❤️ for modern libraries.</p>
          <div className="mt-6 space-x-6">
            <Link href="https://github.com/asefatesfay/library-system" className="text-blue-400 hover:text-blue-300 transition-colors">
              View on GitHub
            </Link>
            <Link href={`${process.env.NEXT_PUBLIC_API_URL}/docs`} className="text-blue-400 hover:text-blue-300 transition-colors">
              API Documentation
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
