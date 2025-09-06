# 🐳 Podman Development Setup

This guide will help you quickly set up the entire Library Management System using Podman and Podman Compose for local development.

## 🚀 Quick Start with Podman

### Prerequisites
- Podman and podman-compose installed
- Git (to clone the repository)

### One-Command Setup
```bash
# Clone and start everything
git clone https://github.com/asefatesfay/library-system.git
cd library-system
podman-compose up
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

### Using Make with Podman
```bash
# Start all services in background
make up-podman

# Start with logs visible
make up-logs-podman

# Stop all services
make down-podman

# Rebuild and restart
make rebuild-podman

# View logs
make logs-podman
```

### Using Podman Compose Directly
```bash
# Start all services
podman-compose up -d

# View logs
podman-compose logs -f

# Stop services
podman-compose down

# Rebuild services
podman-compose build

# Execute commands in containers
podman-compose exec backend bash
podman-compose exec frontend sh
podman-compose exec db psql -U library_user -d library_system
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
podman-compose exec db psql -U library_user -d library_system

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
podman-compose exec backend pytest

# Install new packages
podman-compose exec backend pip install package_name
# Then add to requirements.txt

# View backend logs
podman-compose logs -f backend
```

### Frontend Development
```bash
# The frontend automatically reloads on code changes
# Access at http://localhost:3000

# Install new packages
podman-compose exec frontend npm install package_name

# View frontend logs
podman-compose logs -f frontend
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
podman-compose exec backend pytest

# Run with coverage
podman-compose exec backend pytest --cov=.

# Run specific tests
podman-compose exec backend pytest tests/test_books.py
```

### Frontend Testing
```bash
# Run tests
podman-compose exec frontend npm test

# Run tests in watch mode
podman-compose exec frontend npm run test:watch
```

## 🔄 Data Reset

### Reset Database
```bash
# Complete reset (removes all data)
podman-compose down -v
podman-compose up

# Or using make
make down-podman-volumes
make up-podman
```

### Reset Specific Service
```bash
# Restart just the backend
podman-compose restart backend

# Rebuild just the frontend
podman-compose build frontend
podman-compose up -d frontend
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
podman-compose ps

# View database logs
podman-compose logs db

# Restart database
podman-compose restart db
```

#### Package Installation Issues
```bash
# Rebuild containers after package changes
podman-compose down
podman-compose build
podman-compose up -d
```

### View Container Status
```bash
# Check all containers
podman-compose ps

# Check individual container logs
podman-compose logs backend
podman-compose logs frontend
podman-compose logs db
```

### Container Health Checks
```bash
# Check backend health
curl http://localhost:8000/health

# Check database connection
podman-compose exec db pg_isready -U library_user
```

## 🚀 Podman vs Docker

This setup works identically with both Podman and Docker:
- All `docker-compose` commands work with `podman-compose`
- Container networking and volumes work the same way
- Environment variables and configurations are identical
- Hot reloading and development workflows are identical

### Podman Advantages
- **Rootless**: Runs without root privileges
- **Daemonless**: No background daemon required
- **Pod-based**: Better Kubernetes compatibility
- **Security**: Enhanced security features

## 🎉 Success!

You now have a complete development environment with Podman:
- ✅ Full-stack application running
- ✅ PostgreSQL database with sample data
- ✅ Hot reloading for development
- ✅ Database management tools
- ✅ Easy testing and debugging

Happy coding with Podman! 🚀
