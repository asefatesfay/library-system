# Library Management System

A comprehensive FastAPI-based library management system with full CRUD operations, user authentication, book lending, holds management, and member administration.

## 🚀 Features

### 📚 Book Management
- Complete catalog browsing with search and filtering
- Book availability tracking with multiple copies
- ISBN, genre, publisher, and publication year support
- Staff-only book creation, updates, and management
- Barcode generation for book copies

### 👥 User Management
- Role-based access control (Admin, Librarian, Member)
- User registration and profile management
- Membership statistics and activity tracking
- Password hashing with bcrypt

### 🔄 Loan System
- Book borrowing with automatic due dates
- Loan renewals (up to 2 times per book)
- Return processing with condition tracking
- Overdue fine calculation and management
- Loan history and statistics

### 📋 Hold/Reservation System
- Book hold placement with queue management
- Automatic notifications when books become available
- Hold expiration and cancellation
- Queue position tracking
- Staff hold fulfillment processing

### 💰 Fine Management
- Automatic overdue fine calculation
- Complete fine payment processing with multiple payment methods
- Fine history and comprehensive reporting
- Admin fine waiver capabilities
- Outstanding balance tracking and borrowing restrictions

### 🔔 Notification System
- Automatic book availability notifications
- Overdue loan and hold expiration reminders
- Fine payment and waiver notifications
- Staff broadcast messaging to user groups
- Read/unread status tracking with notification summaries

### 🔐 Authentication & Security
- JWT-based authentication
- Role-based authorization
- Secure password hashing
- Environment variable configuration

## 🛠 Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React/Next.js (Coming Soon)
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt via passlib
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Deployment**: Docker on Google Cloud Run
- **CI/CD**: GitHub Actions

## 📋 Requirements

- Python 3.11+
- PostgreSQL (for production)
- FastAPI and dependencies (see requirements.txt)

## 🚀 Installation & Setup

### Local Development

#### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/asefatesfay/library-system.git
   cd library-system/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the backend:**
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://127.0.0.1:8000`
API Documentation: `http://127.0.0.1:8000/docs`

#### Frontend Setup (Coming Soon)

```bash
cd frontend
npm install
npm run dev
```

### Production Deployment

The application is configured for deployment on Google Cloud Run with:
- Automatic CI/CD via GitHub Actions
- PostgreSQL database on Cloud SQL
- Environment-based configuration
- Docker containerization

## 📖 API Endpoints

### Authentication
- `POST /auth/login` — User login
- `POST /auth/register` — User registration

### Books
- `GET /books/` — Browse book catalog (with search/filters)
- `GET /books/{book_id}` — Get book details
- `GET /books/{book_id}/availability` — Check book availability
- `POST /books/` — Add new book (Staff only)
- `PUT /books/{book_id}` — Update book (Staff only)
- `DELETE /books/{book_id}` — Remove book (Staff only)

### Loans
- `POST /loans/` — Borrow a book
- `GET /loans/` — Get user's loans
- `GET /loans/{loan_id}` — Get loan details
- `PUT /loans/{loan_id}/renew` — Renew a loan
- `PUT /loans/{loan_id}/return` — Return a book
- `GET /loans/all` — Get all loans (Staff only)
- `GET /loans/stats` — Loan statistics (Staff only)

### Holds
- `POST /holds/` — Place a hold on a book
- `GET /holds/` — Get user's holds
- `GET /holds/{hold_id}` — Get hold details
- `PUT /holds/{hold_id}/cancel` — Cancel a hold
- `GET /holds/all` — Get all holds (Staff only)
- `PUT /holds/{hold_id}/fulfill` — Fulfill a hold (Staff only)

### Fines
- `GET /fines/` — Get user's fines
- `GET /fines/{fine_id}` — Get fine details
- `POST /fines/{fine_id}/pay` — Pay a fine
- `GET /fines/summary` — Get fine summary
- `GET /fines/all` — Get all fines (Staff only)
- `POST /fines/{fine_id}/waive` — Waive a fine (Staff only)
- `GET /fines/stats` — Fine statistics (Staff only)
- `GET /fines/report` — Generate fine report (Staff only)

### Notifications
- `GET /notifications/` — Get user's notifications
- `PUT /notifications/{notification_id}/read` — Mark notification as read
- `PUT /notifications/mark-all-read` — Mark all notifications as read
- `GET /notifications/summary` — Get notification summary
- `POST /notifications/broadcast` — Broadcast notification (Staff only)

### Members
- `GET /members/` — List all members (Staff only)
- `POST /members/` — Create new member (Admin only)
- `GET /members/{member_id}` — Get member details
- `PUT /members/{member_id}` — Update member (Staff only)
- `GET /members/{member_id}/stats` — Member statistics
- `PUT /members/{member_id}/deactivate` — Deactivate member (Admin only)

### Users
- `GET /users/me` — Get current user profile
- `PUT /users/me` — Update user profile

## 🏗 Project Structure

```
library-system/
├── README.md                  # Project overview and documentation
├── .gitignore                 # Git ignore rules
├── .github/
│   └── workflows/
│       └── deploy.yml         # CI/CD pipeline configuration
├── backend/                   # FastAPI Backend Application
│   ├── main.py               # FastAPI application entry point
│   ├── database.py           # Database models and configuration
│   ├── models.py             # Pydantic schemas
│   ├── auth.py               # Authentication and authorization
│   ├── seed_data.py          # Database seeding with sample data
│   ├── notification_service.py # Notification automation service
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile           # Container configuration
│   ├── .env.example         # Environment variables template
│   └── routes/
│       ├── auth.py          # Authentication endpoints
│       ├── books.py         # Book management endpoints
│       ├── loans.py         # Loan management endpoints
│       ├── holds.py         # Hold/reservation endpoints
│       ├── fines.py         # Fine management endpoints
│       ├── notifications.py # Notification endpoints
│       ├── members.py       # Member management endpoints
│       └── users.py         # User profile endpoints
└── frontend/                  # React Frontend Application (Coming Soon)
    ├── src/
    ├── public/
    ├── package.json
    └── ...
```

## 🎯 User Roles & Permissions

### Member (Default)
- Browse book catalog
- Borrow and return books
- Place and cancel holds
- View personal loan/hold history
- Update own profile

### Librarian
- All Member permissions
- View all loans and holds
- Process returns and fulfill holds
- View member statistics
- Manage book copies

### Admin
- All Librarian permissions
- Create and manage books
- Create and deactivate members
- Access system-wide statistics
- Waive fines

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
ENVIRONMENT=production|development
```

### Database Configuration

The application supports both SQLite (development) and PostgreSQL (production):

- **Development**: Uses `sqlite:///./library.db`
- **Production**: Uses PostgreSQL via `DATABASE_URL` environment variable

## 📊 Sample Data

The application includes a seeding system that creates:
- 10 classic books with multiple copies
- 5 users with different roles
- Sample loan and hold data
- Realistic library catalog

Run with: The application will automatically seed data on startup if tables are empty.

## 🚢 Deployment

### Google Cloud Run

1. Set up Cloud SQL PostgreSQL instance
2. Configure GitHub secrets for deployment
3. Push to main branch triggers automatic deployment

### Environment Variables for Production

Set these in your deployment environment:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Strong secret for JWT signing
- Other configuration as needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🎓 Learning Objectives

This project demonstrates:
- RESTful API design principles
- Database relationships and ORM usage
- Authentication and authorization
- Role-based access control
- File organization and project structure
- Environment-based configuration
- Modern Python web development practices
- Cloud deployment and CI/CD

## 🔗 Links

- **Live API**: [Deployed on Google Cloud Run]
- **API Documentation**: Visit `/docs` endpoint for interactive Swagger UI
- **Repository**: [GitHub Repository](https://github.com/asefatesfay/library-system)
