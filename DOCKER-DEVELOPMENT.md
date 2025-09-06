# 🐳 Docker Development Setup

This guide will help you quickly set up the entire Library Management System using Docker Compose for local development.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git (to clone the repository)

### One-Command Setup
```bash
# Clone and start everything
git clone https://github.com/asefatesfay/library-system.git
cd library-system
docker-compose up
```

That's it! Your full-stack application will be running on:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database Admin**: http://localhost:8080 (Adminer)

## 📋 Services

### Core Services
| Service | Port | URL | Description |
|---------|------|-----|-------------|
| Frontend | 3000 | http://localhost:3000 | Next.js React application |
| Backend | 8000 | http://localhost:8000 | FastAPI Python application |
| Database | 5432 | localhost:5432 | PostgreSQL database |

### Development Tools
| Service | Port | URL | Description |
|---------|------|-----|-------------|
| Adminer | 8080 | http://localhost:8080 | Database management interface |
| Redis | 6379 | localhost:6379 | Caching (optional) |

## 🛠 Development Commands

### Using Make (Recommended)
```bash
# Start all services in background
make up

# Start with logs visible
make up-logs

# Stop all services
make down

# Rebuild and restart
make rebuild

# View logs
make logs
make logs-backend    # Backend only
make logs-frontend   # Frontend only

# Database operations
make db-shell        # Connect to PostgreSQL

# Development shells
make shell-backend   # Bash in backend container
make shell-frontend  # Shell in frontend container
```

### Using Docker Compose Directly
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild services
docker-compose build

# Execute commands in containers
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec db psql -U library_user -d library_system
```

## 🗄 Database Setup

### Automatic Setup
The PostgreSQL database is automatically created with:
- **Database**: `library_system`
- **User**: `library_user`
- **Password**: `library_password`
- **Seed Data**: Sample books, users, and test data

### Manual Database Access
```bash
# Connect to database
make db-shell

# Or using docker-compose
docker-compose exec db psql -U library_user -d library_system

# View tables
\dt

# Sample query
SELECT * FROM books LIMIT 5;
```

### Database Management UI
Access Adminer at http://localhost:8080
- **System**: PostgreSQL
- **Server**: db
- **Username**: library_user
- **Password**: library_password
- **Database**: library_system

## 🔧 Development Workflow

### Backend Development
```bash
# The backend automatically reloads on code changes
# Access API docs at http://localhost:8000/docs

# Run tests
docker-compose exec backend pytest

# Install new packages
docker-compose exec backend pip install package_name
# Then add to requirements.txt

# View backend logs
make logs-backend
```

### Frontend Development
```bash
# The frontend automatically reloads on code changes
# Access at http://localhost:3000

# Install new packages
docker-compose exec frontend npm install package_name

# View frontend logs
make logs-frontend
```

## 🎯 Demo Credentials

Test the application with these pre-configured users:

| Role | Email | Password | Capabilities |
|------|-------|----------|-------------|
| Admin | admin@library.com | password123 | Full system access |
| Librarian | librarian@library.com | password123 | Manage books, loans, users |
| Member | member@library.com | password123 | Browse, borrow, returns |

## 🧪 Testing

### Backend API Testing
```bash
# Run all tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=.

# Run specific tests
docker-compose exec backend pytest tests/test_books.py
```

### Frontend Testing
```bash
# Run tests
docker-compose exec frontend npm test

# Run tests in watch mode
docker-compose exec frontend npm run test:watch
```

## 🔄 Data Reset

### Reset Database
```bash
# Complete reset (removes all data)
make down-volumes
make up

# Or manually
docker-compose down -v
docker-compose up
```

### Reset Specific Service
```bash
# Restart just the backend
docker-compose restart backend

# Rebuild just the frontend
docker-compose build frontend
docker-compose up -d frontend
```

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the ports
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # Database

# Kill processes or change ports in docker-compose.yml
```

#### Database Connection Issues
```bash
# Check database is healthy
docker-compose ps

# View database logs
make logs-db

# Restart database
docker-compose restart db
```

#### Package Installation Issues
```bash
# Rebuild containers after package changes
make rebuild
```

### View Container Status
```bash
# Check all containers
make status

# Or
docker-compose ps
```

### Container Health Checks
```bash
# Check backend health
curl http://localhost:8000/health

# Check database connection
docker-compose exec db pg_isready -U library_user
```

## 🚀 Production Notes

This Docker setup is optimized for development with:
- Hot reloading for both frontend and backend
- Volume mounts for code changes
- Development-friendly environment variables
- Debug tools (Adminer, detailed logging)

For production deployment, refer to:
- `backend/Dockerfile` for production backend build
- `.github/workflows/deploy.yml` for CI/CD pipeline
- Google Cloud Run deployment configuration

## 📝 Environment Variables

Development environment variables are configured in `docker-compose.yml`. For custom configurations:

1. Copy `.env.docker` to `.env.local`
2. Modify variables as needed
3. Reference in docker-compose.yml:
   ```yaml
   env_file:
     - .env.local
   ```

## 🎉 Success!

You now have a complete development environment with:
- ✅ Full-stack application running
- ✅ PostgreSQL database with sample data
- ✅ Hot reloading for development
- ✅ Database management tools
- ✅ Easy testing and debugging

Happy coding! 🚀
