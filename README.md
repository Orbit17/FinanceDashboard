# 🚀 Finance AI Platform

AI-Powered Personal Finance Insights Platform with Docker

## Quick Start

1. **Install Docker Desktop** from docker.com

2. **Build and start services:**
   ```bash
   make build
   make start
   ```

3. **Wait 10 seconds**, then seed demo data:
   ```bash
   make seed
   ```

4. **Access the app:**
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Commands

- `make start` - Start all services
- `make stop` - Stop services
- `make restart` - Restart services
- `make logs` - View logs
- `make seed` - Add demo data
- `make clean` - Remove everything

## API Endpoints

- `GET /api/transactions` - List all transactions
- `POST /api/transactions` - Create transaction
- `GET /api/insights` - Get AI insights
- `GET /api/forecast` - Get cash flow forecast
- `POST /api/demo/seed` - Seed demo data

## Next Steps

1. Connect to Plaid for real bank data
2. Train custom ML models
3. Build React frontend
4. Deploy to production

## Troubleshooting

**Port 5432 in use?**
```bash
docker-compose down
# Stop local PostgreSQL
```

**Database not ready?**
```bash
docker-compose logs db
# Wait for "database system is ready to accept connections"
```

**Start fresh:**
```bash
make clean
make build
make start
```
