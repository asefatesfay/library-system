import Link from "next/link";
import Image from "next/image";

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">📚 Library System</h1>
            </div>
            <nav className="flex space-x-4">
              <Link href="/auth/login" className="text-gray-600 hover:text-gray-900">
                Login
              </Link>
              <Link href="/auth/register" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                Register
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative bg-gray-900 min-h-[80vh] flex items-center">
        {/* Background Image */}
        <div className="absolute inset-0">
          <Image
            src="/images/library-hero.jpg"
            alt="Beautiful library interior"
            fill
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-gray-900 bg-opacity-60"></div>
        </div>
        
        {/* Hero Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white sm:text-6xl lg:text-7xl">
              Modern Library
              <span className="text-blue-400"> Management</span>
            </h1>
            <p className="mt-6 text-xl leading-8 text-gray-200 max-w-3xl mx-auto">
              A comprehensive digital library system with book management, user authentication, 
              loan tracking, holds, fines, and automated notifications. Built with FastAPI and React.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                href="/books"
                className="rounded-md bg-blue-600 px-8 py-4 text-lg font-semibold text-white shadow-lg hover:bg-blue-500 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
              >
                Browse Books
              </Link>
              <Link 
                href="http://localhost:8001/docs" 
                className="text-lg font-semibold leading-6 text-white hover:text-blue-400 transition-colors"
              >
                API Documentation <span aria-hidden="true">→</span>
              </Link>
            </div>
            
            {/* Demo Credentials */}
            <div className="mt-12 bg-black bg-opacity-30 rounded-lg p-6 max-w-md mx-auto backdrop-blur-sm">
              <h3 className="text-lg font-semibold text-white mb-3">🚀 Try the Demo</h3>
              <div className="text-sm text-gray-200 space-y-1">
                <div><span className="font-medium">Admin:</span> admin@library.com</div>
                <div><span className="font-medium">Librarian:</span> librarian@library.com</div>
                <div><span className="font-medium">Member:</span> member@library.com</div>
                <div className="text-xs text-gray-300 mt-2">Password: password123</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="bg-gradient-to-br from-blue-50 to-indigo-100 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Features Section */}
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl">
              Comprehensive Library Features
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Everything you need to manage a modern library efficiently and effectively
            </p>
          </div>

          {/* Features Grid */}
          {/* Features Grid */}
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 text-2xl mb-4">📖</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Book Management</h3>
              <p className="text-gray-600">Complete catalog with search, filtering, and availability tracking</p>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 text-2xl mb-4">👥</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">User Roles</h3>
              <p className="text-gray-600">Role-based access control for Members, Librarians, and Admins</p>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 text-2xl mb-4">🔄</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Loan System</h3>
              <p className="text-gray-600">Book borrowing, renewals, returns, and automated due date tracking</p>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 text-2xl mb-4">📋</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Holds & Reservations</h3>
              <p className="text-gray-600">Queue management with automatic availability notifications</p>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 text-2xl mb-4">💰</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Fine Management</h3>
              <p className="text-gray-600">Automatic calculation, payment processing, and comprehensive reporting</p>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-600 text-2xl mb-4">🔔</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Notifications</h3>
              <p className="text-gray-600">Automated alerts for book availability, overdue items, and fines</p>
            </div>
          </div>
        </div>        {/* Tech Stack */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mt-16 bg-white rounded-lg shadow-md p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">Technology Stack</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
              <div>
                <div className="text-3xl mb-2">⚡</div>
                <div className="font-semibold">FastAPI</div>
                <div className="text-sm text-gray-600">Backend API</div>
              </div>
              <div>
                <div className="text-3xl mb-2">⚛️</div>
                <div className="font-semibold">Next.js</div>
                <div className="text-sm text-gray-600">Frontend</div>
              </div>
              <div>
                <div className="text-3xl mb-2">🐘</div>
                <div className="font-semibold">PostgreSQL</div>
                <div className="text-sm text-gray-600">Database</div>
              </div>
              <div>
                <div className="text-3xl mb-2">☁️</div>
                <div className="font-semibold">Google Cloud</div>
                <div className="text-sm text-gray-600">Deployment</div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-lg">&copy; 2025 Library Management System. Built with ❤️ for modern libraries.</p>
          <div className="mt-6 space-x-6">
            <Link href="https://github.com/asefatesfay/library-system" className="text-blue-400 hover:text-blue-300 transition-colors">
              View on GitHub
            </Link>
            <Link href="http://localhost:8001/docs" className="text-blue-400 hover:text-blue-300 transition-colors">
              API Documentation
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
