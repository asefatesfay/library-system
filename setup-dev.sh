#!/bin/bash

# Test script for Docker development setup
echo "🧪 Testing Library Management System Docker Setup"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed"
    exit 1
fi

echo "✅ docker-compose is available"

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Test backend health
echo "🔍 Testing backend health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
fi

# Test frontend
echo "🔍 Testing frontend..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not accessible"
fi

# Test database
echo "🔍 Testing database..."
if docker-compose exec -T db pg_isready -U library_user > /dev/null 2>&1; then
    echo "✅ Database is ready"
else
    echo "❌ Database is not ready"
fi

echo ""
echo "🎉 Setup complete! Your services are running on:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   DB Admin:  http://localhost:8080"
echo ""
echo "📋 Demo credentials:"
echo "   Admin:     admin@library.com / password123"
echo "   Librarian: librarian@library.com / password123"
echo "   Member:    member@library.com / password123"
echo ""
echo "🛑 To stop services: docker-compose down"
