# Quick Start Guide - Payment Service

Get up and running with the Payment Service in 5 minutes!

## Prerequisites

- Docker installed (for Docker option)
- Python 3.12+ (for local development)
- PostgreSQL database: `eygar_property_listing` (must be running and accessible)

## Option 1: Docker Compose (Recommended)

1. **Clone and navigate to the project**:
```bash
cd payment-service
```

2. **Copy environment file**:
```bash
cp .env.example .env
```

3. **Update .env with your database credentials**:
```bash
# Edit .env file
DATABASE_URL=postgresql+asyncpg://myuser:mypassword@localhost:5432/eygar_payment_db
```

4. **Ensure PostgreSQL is running**:
Your external PostgreSQL database must be running and accessible on localhost:5432

5. **Start the payment service**:
```bash
docker-compose up -d
```

6. **Check service health**:
```bash
curl http://localhost:8002/health
```

7. **View API documentation**:
Open http://localhost:8002/docs in your browser

The service is now running at **http://localhost:8002** and connected to your PostgreSQL database.

## Option 2: Local Development

1. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Ensure PostgreSQL database exists**:
```bash
# Database 'eygar_payment_db' should already exist
# Check connection with:
psql -h localhost -U myuser -d eygar_payment_db
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your database credentials
DATABASE_URL=postgresql+asyncpg://myuser:mypassword@localhost:5432/eygar_payment_db
```

5. **Run migrations**:
```bash
alembic upgrade head
```

6. **Start the service**:
```bash
uvicorn app.main:app --reload
```

7. **Access the API**:
- Docs: http://localhost:8002/docs
- Health: http://localhost:8002/health

## Testing the API

### Generate a JWT Token

```python
python -c "from app.core.security import jwt_handler; print(jwt_handler.create_access_token({'user_id': 1, 'sub': '1'}))"
```

### Create a Payment

```bash
curl -X POST "http://localhost:8002/api/v1/payments/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "pi_test_12345",
    "amount_total": 99.99,
    "currency": "USD",
    "payment_status": "pending",
    "provider": "stripe",
    "customer_email": "test@example.com"
  }'
```

### Get User Payments

```bash
curl -X GET "http://localhost:8002/api/v1/payments/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Create test database
createdb test_payment_db

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## Common Commands

```bash
# Start payment service
docker-compose up -d

# View logs
docker-compose logs -f payment-service

# Stop service
docker-compose down

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

## Using Makefile

```bash
# View all commands
make help

# Install dependencies
make install

# Run tests
make test

# Start development server
make run

# Start Docker containers
make docker-up
```

## Next Steps

1. ✅ Service is running
2. 📖 Read the [full README](README.md)
3. 🔍 Explore the API at http://localhost:8002/docs
4. 🧪 Run the example script: `python examples/api_usage.py`
5. 🔐 Integrate with your authentication service

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running on localhost:5432
- Verify database `eygar_payment_db` exists
- Check credentials in .env match your PostgreSQL setup
- Test connection: `psql -h localhost -U myuser -d eygar_payment_db`

### Port Already in Use
- Change port in docker-compose.yml or use `--port` flag

### Authentication Error
- Ensure JWT token is valid and not expired
- Check SECRET_KEY matches in .env

### Migration Issues
```bash
# Reset database
alembic downgrade base
alembic upgrade head
```

## Support

- 📚 Full Documentation: [README.md](README.md)
- 🐛 Report Issues: GitHub Issues
- 💬 Questions: Open a discussion

Happy coding! 🚀
