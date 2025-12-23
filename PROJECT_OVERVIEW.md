# Payment Microservice - Complete Project Overview

## 🎯 Project Summary

A production-ready, high-performance payment microservice built with FastAPI following clean architecture principles. The service features JWT authentication, async operations, comprehensive testing, and Docker support.

## ✅ What's Included

### Core Features
- ✅ **JWT Authentication**: Secure Bearer token authentication on all endpoints
- ✅ **Async/Await**: Full async support with asyncpg and async SQLAlchemy
- ✅ **Clean Architecture**: Repository → Service → API layer separation
- ✅ **Type Safety**: Comprehensive Pydantic models for validation
- ✅ **Database Migrations**: Alembic for version-controlled schema changes
- ✅ **Pagination**: Efficient pagination with filtering
- ✅ **Docker Ready**: Multi-stage Dockerfile with docker-compose
- ✅ **Testing**: Complete test suite with pytest and fixtures
- ✅ **Documentation**: Auto-generated OpenAPI/Swagger docs

### Payment Data Fields (As Requested)
✅ checkout_session_id
✅ payment_id
✅ payment_method_id
✅ payment_method_types
✅ payment_status (enum: pending, processing, succeeded, failed, canceled, refunded)
✅ currency
✅ amount_total
✅ customer_id
✅ customer_email
✅ booking_id
✅ property_id
✅ user_id
✅ provider (enum: stripe, paypal, square, razorpay, other)
✅ created_at
✅ updated_at
✅ description

## 📁 Project Structure

```
payment-service/
├── app/                          # Main application code
│   ├── api/v1/                  # API endpoints
│   │   └── payment.py           # Payment routes with JWT auth
│   ├── core/                    # Core configuration
│   │   ├── config.py            # Settings management
│   │   ├── database.py          # Async SQLAlchemy setup
│   │   └── security.py          # JWT token handling
│   ├── dependencies/            # FastAPI dependencies
│   │   └── auth.py              # Authentication dependency
│   ├── models/                  # Database models
│   │   └── payment.py           # Payment SQLAlchemy model
│   ├── repositories/            # Data access layer
│   │   └── payment_repository.py # All database operations
│   ├── schemas/                 # Pydantic models
│   │   └── payment.py           # Request/response schemas
│   ├── services/                # Business logic
│   │   └── payment_service.py   # Payment service layer
│   └── main.py                  # FastAPI application
├── alembic/                     # Database migrations
│   ├── versions/
│   │   └── 001_initial.py       # Initial migration
│   └── env.py                   # Alembic configuration
├── tests/                       # Test suite
│   ├── conftest.py              # Test fixtures
│   └── test_payment_api.py      # API tests
├── examples/                    # Usage examples
│   └── api_usage.py             # Example API calls
├── docker-compose.yml           # Docker Compose setup
├── Dockerfile                   # Multi-stage Dockerfile
├── requirements.txt             # Python dependencies
├── Makefile                     # Common commands
├── README.md                    # Full documentation
└── QUICKSTART.md               # Quick start guide
```

## 🔌 API Endpoints

### Authentication Required (JWT Token)
All endpoints require: `Authorization: Bearer <token>`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/payments/` | Create new payment |
| GET | `/api/v1/payments/` | Get user payments (paginated) |
| GET | `/api/v1/payments/{id}` | Get payment by ID |
| GET | `/api/v1/payments/payment-gateway/{payment_id}` | Get by gateway ID |
| GET | `/api/v1/payments/booking/{booking_id}` | Get payments by booking |
| PUT | `/api/v1/payments/{id}` | Update payment |
| PATCH | `/api/v1/payments/{id}/status` | Update payment status |
| DELETE | `/api/v1/payments/{id}` | Cancel payment |
| GET | `/api/v1/payments/admin/all` | Get all payments (admin) |

### Public Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | Service info |
| GET | `/docs` | API documentation |

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
cd payment-service
cp .env.example .env
# Edit .env with your PostgreSQL credentials
docker-compose up -d
```

Access the service:
- API: http://localhost:8002
- Docs: http://localhost:8002/docs
- Health: http://localhost:8002/health

**Prerequisites**: PostgreSQL database `eygar_payment_db` must be running on localhost:5432

### Local Development
```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database (ensure eygar_property_listing exists)
alembic upgrade head

# Run
uvicorn app.main:app --reload
```

## 🔑 Authentication

The service uses JWT Bearer tokens. Every API request (except `/health` and `/`) requires a valid JWT token.

### Token Requirements
```json
{
  "user_id": 123,
  "sub": "123",
  "exp": 1234567890
}
```

### Example Request
```bash
curl -X POST "http://localhost:8002/api/v1/payments/" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "pi_1234567890",
    "amount_total": 99.99,
    "currency": "USD",
    "payment_status": "pending",
    "provider": "stripe"
  }'
```

## 🧪 Testing

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

Test coverage includes:
- ✅ Payment creation
- ✅ Payment retrieval (by ID, gateway ID, booking)
- ✅ Payment updates
- ✅ Status updates
- ✅ Pagination
- ✅ Filtering
- ✅ Authorization checks
- ✅ Error handling

## 🏗 Architecture Layers

### 1. API Layer (`app/api/v1/payment.py`)
- Defines REST endpoints
- Handles request/response
- Uses FastAPI dependencies for auth
- Returns Pydantic models

### 2. Service Layer (`app/services/payment_service.py`)
- Contains business logic
- Validates authorization (user owns payment)
- Handles errors and exceptions
- Orchestrates repository calls

### 3. Repository Layer (`app/repositories/payment_repository.py`)
- Direct database operations
- Uses async SQLAlchemy
- Efficient queries with indexes
- Pagination and filtering

### 4. Model Layer (`app/models/payment.py`)
- SQLAlchemy ORM models
- Database schema definition
- Relationships and constraints

### 5. Schema Layer (`app/schemas/payment.py`)
- Pydantic models for validation
- Request/response serialization
- Type checking

## 🔒 Security Features

1. **JWT Authentication**: Every endpoint protected with Bearer tokens
2. **Authorization**: Users can only access their own payments
3. **Input Validation**: Pydantic models validate all inputs
4. **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries
5. **CORS Configuration**: Configurable allowed origins
6. **Password Hashing**: Ready for user service integration

## 🚢 Deployment

### Docker Compose (Development)
```bash
docker-compose up -d
```

Includes:
- Payment service
- PostgreSQL database
- Redis (optional caching)

### Docker (Production)
```bash
docker build -t payment-service:latest .
docker run -d -p 8000:8000 payment-service:latest
```

### Environment Variables
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
SECRET_KEY=your-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:3000
```

## 📊 Database Schema

### Payments Table
- **Primary Key**: `id` (auto-increment)
- **Unique Constraints**: `payment_id`, `checkout_session_id`
- **Indexes**: On all frequently queried fields
- **Foreign Keys**: Ready for integration with booking/property services

### Enums
- **PaymentStatus**: pending, processing, succeeded, failed, canceled, refunded
- **PaymentProvider**: stripe, paypal, square, razorpay, other

## ⚡ Performance Optimizations

1. **Async Operations**: All I/O is async (database, API calls)
2. **Connection Pooling**: Optimized database connection pool (size: 10, max_overflow: 20)
3. **Database Indexes**: Strategic indexes on frequently queried columns
4. **Pagination**: Efficient offset-based pagination
5. **Query Optimization**: Selective loading with filters
6. **Caching Ready**: Redis integration prepared

## 🛠 Development Tools

### Makefile Commands
```bash
make help        # Show all commands
make install     # Install dependencies
make test        # Run tests
make run         # Start development server
make docker-up   # Start Docker containers
make migrate     # Run migrations
```

### Alembic Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📈 Monitoring & Health

### Health Check Endpoint
```bash
curl http://localhost:8002/health
```

Response:
```json
{
  "status": "healthy",
  "service": "payment-service",
  "version": "1.0.0"
}
```

### Docker Health Check
Built-in health check in Docker container (30s interval)

## 🔧 Customization

### Adding New Payment Providers
1. Add provider to `PaymentProvider` enum in `models/payment.py`
2. Update validation in schemas if needed
3. Add provider-specific logic in service layer

### Adding New Endpoints
1. Define route in `app/api/v1/payment.py`
2. Add business logic in `app/services/payment_service.py`
3. Add database operations in `app/repositories/payment_repository.py`
4. Write tests in `tests/test_payment_api.py`

### Integrating with Other Services
The service is designed to integrate easily with:
- **Auth Service**: Validates JWT tokens from your auth service
- **Booking Service**: Links payments to bookings via `booking_id`
- **Property Service**: Links payments to properties via `property_id`
- **Notification Service**: Can trigger events on payment status changes

## 📝 Example Usage

See `examples/api_usage.py` for a complete example showing:
- Creating payments
- Retrieving payments
- Updating status
- Pagination
- Filtering
- Error handling

Run it:
```bash
python examples/api_usage.py
```

## 🐛 Troubleshooting

### Database Connection
```bash
# Check PostgreSQL is running
docker-compose ps
# View logs
docker-compose logs postgres
```

### Authentication Issues
- Ensure SECRET_KEY matches across services
- Verify JWT token is not expired
- Check token includes `user_id` or `sub`

### Migration Issues
```bash
# Reset database
alembic downgrade base
alembic upgrade head
```

## 📚 Documentation

- **README.md**: Complete documentation
- **QUICKSTART.md**: 5-minute quick start guide
- **API Docs**: http://localhost:8002/docs (interactive)
- **ReDoc**: http://localhost:8002/redoc (alternative docs)

## 🎓 Key Takeaways

✅ **Modular Architecture**: Easy to maintain and extend
✅ **Production Ready**: Docker, migrations, tests, docs
✅ **Secure**: JWT auth, validation, authorization
✅ **Performant**: Async operations, pooling, indexes
✅ **Well Tested**: Comprehensive test suite
✅ **Well Documented**: README, quick start, API docs

## 📦 What You Get

✅ Complete FastAPI payment microservice
✅ Async database operations (PostgreSQL + asyncpg)
✅ JWT authentication on all endpoints
✅ Clean architecture (Repository/Service/API layers)
✅ Pydantic models for validation
✅ SQLAlchemy models with migrations
✅ Comprehensive test suite
✅ Docker & Docker Compose setup
✅ Full documentation
✅ Example usage scripts
✅ Makefile for common tasks

## 🚀 Next Steps

1. ✅ Review the code structure
2. ✅ Start the service: `docker-compose up -d`
3. ✅ Explore API: http://localhost:8002/docs
4. ✅ Run tests: `pytest`
5. ✅ Integrate with your auth service
6. ✅ Customize for your needs

---

**Built with ❤️ using FastAPI, SQLAlchemy, and modern Python best practices**
