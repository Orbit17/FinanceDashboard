.PHONY: help build start stop restart logs clean seed

help:
	@echo "Finance AI Platform - Docker Commands"
	@echo "======================================"
	@echo "make build   - Build Docker images"
	@echo "make start   - Start all services"
	@echo "make stop    - Stop all services"
	@echo "make restart - Restart all services"
	@echo "make logs    - View logs"
	@echo "make seed    - Seed demo data"
	@echo "make clean   - Remove containers and volumes"

build:
	@echo "🔨 Building Docker images..."
	docker-compose build

start:
	@echo "🚀 Starting services..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "Wait 10 seconds for DB to initialize, then run: make seed"

stop:
	@echo "🛑 Stopping services..."
	docker-compose down

restart:
	@echo "🔄 Restarting services..."
	docker-compose restart

logs:
	docker-compose logs -f

seed:
	@echo "🌱 Seeding demo data..."
	curl -X POST http://localhost:8000/api/demo/seed
	@echo ""
	@echo "✅ Demo data seeded! Check http://localhost:8000/api/transactions"

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	rm -rf backend/__pycache__ backend/app/__pycache__
