import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
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
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h2 className="text-4xl font-bold text-gray-900 sm:text-6xl">
            Modern Library
            <span className="text-blue-600"> Management</span>
          </h2>
          <p className="mt-6 text-lg leading-8 text-gray-600 max-w-2xl mx-auto">
            A comprehensive digital library system with book management, user authentication, 
            loan tracking, holds, fines, and automated notifications. Built with FastAPI and React.
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <Link
              href="/books"
              className="rounded-md bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
            >
              Browse Books
            </Link>
            <Link href="http://localhost:8001/docs" className="text-sm font-semibold leading-6 text-gray-900">
              API Documentation <span aria-hidden="true">→</span>
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
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

        {/* Tech Stack */}
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

        {/* Demo Section */}
        <div className="mt-16 bg-blue-50 rounded-lg p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-4 text-center">Try the Demo</h3>
          <p className="text-gray-600 text-center mb-6">
            Experience the full functionality with sample data
          </p>
          <div className="text-center">
            <div className="inline-flex flex-col sm:flex-row gap-4">
              <div className="bg-white p-4 rounded-lg shadow-sm">
                <div className="font-semibold text-gray-900">Demo Users</div>
                <div className="text-sm text-gray-600 mt-1">
                  Admin: admin@library.com<br/>
                  Librarian: librarian@library.com<br/>
                  Member: member@library.com
                </div>
                <div className="text-xs text-gray-500 mt-2">Password: password123</div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p>&copy; 2025 Library Management System. Built with ❤️ for modern libraries.</p>
          <div className="mt-4 space-x-4">
            <Link href="https://github.com/asefatesfay/library-system" className="text-blue-400 hover:text-blue-300">
              View on GitHub
            </Link>
            <Link href="http://localhost:8001/docs" className="text-blue-400 hover:text-blue-300">
              API Docs
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
