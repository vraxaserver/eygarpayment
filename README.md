# Payment Microservice

A high-performance, production-ready payment microservice built with FastAPI, featuring JWT authentication, async operations, and clean architecture principles.

## 🚀 Features

- **Async/Await**: Full async support with asyncpg and SQLAlchemy
- **JWT Authentication**: Secure endpoint protection with Bearer token authentication
- **Clean Architecture**: Separation of concerns with Repository, Service, and API layers
- **Type Safety**: Comprehensive Pydantic models for request/response validation
- **Database Migrations**: Alembic integration for version-controlled schema changes
- **Pagination**: Efficient cursor-based pagination for large datasets
- **Filtering**: Advanced filtering by status, provider, booking, and property
- **Docker Support**: Multi-stage Dockerfile for optimized container images
- **Comprehensive Testing**: Pytest-based test suite with fixtures
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## 📋 Table of Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Service](#running-the-service)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [Project Structure](#project-structure)

## 🏗 Architecture

The service follows a clean, modular architecture:

```
├── app/
│   ├── api/          # API endpoints and routes
│   ├── core/         # Core configuration, database, security
│   ├── models/       # SQLAlchemy database models
│   ├── schemas/      # Pydantic request/response schemas
│   ├── repositories/ # Data access layer
│   ├── services/     # Business logic layer
│   └── dependencies/ # FastAPI dependencies (auth, etc.)
```

## 📦 Installation

### Prerequisites

- Python 3.12+
- PostgreSQL 15+ (external database required)
- Access to database: `eygar_property_listing`

### Local Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd payment-service
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

1. **Copy environment template**:
```bash
cp .env.example .env
```

2. **Update environment variables**:
```env
DATABASE_URL=postgresql+asyncpg://myuser:mypassword@localhost:5432/eygar_payment_db
SECRET_KEY=your-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:3000
```

## 🗄️ Database Setup

### Using Alembic Migrations

1. **Ensure database exists**:
```bash
# Database 'eygar_payment_db' should already exist
# If not, create it:
createdb eygar_payment_db
```

2. **Run migrations**:
```bash
alembic upgrade head
```

3. **Create new migration** (after model changes):
```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Manual Setup

Alternatively, the application will auto-create tables on startup if they don't exist.

## 🏃 Running the Service

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --workers 4
```

### Access the API

- **API Documentation**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc
- **Health Check**: http://localhost:8002/health

## 🔌 API Endpoints

### Payment Operations

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/payments/` | Create new payment | ✅ |
| GET | `/api/v1/payments/` | Get user payments (paginated) | ✅ |
| GET | `/api/v1/payments/{id}` | Get payment by ID | ✅ |
| GET | `/api/v1/payments/payment-gateway/{payment_id}` | Get by gateway payment ID | ✅ |
| GET | `/api/v1/payments/booking/{booking_id}` | Get payments by booking | ✅ |
| PUT | `/api/v1/payments/{id}` | Update payment | ✅ |
| PATCH | `/api/v1/payments/{id}/status` | Update payment status | ✅ |
| DELETE | `/api/v1/payments/{id}` | Cancel payment | ✅ |
| GET | `/api/v1/payments/admin/all` | Get all payments (admin) | ✅ |

### Request Examples

#### Create Payment

```bash
curl -X POST "http://localhost:8002/api/v1/payments/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "pi_1234567890",
    "amount_total": 99.99,
    "currency": "USD",
    "payment_status": "pending",
    "provider": "stripe",
    "customer_email": "customer@example.com",
    "booking_id": 1,
    "property_id": 1,
    "description": "Property booking payment"
  }'
```

#### Get User Payments (with pagination)

```bash
curl -X GET "http://localhost:8002/api/v1/payments/?page=1&page_size=10&status=succeeded" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Update Payment Status

```bash
curl -X PATCH "http://localhost:8002/api/v1/payments/1/status" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_status": "succeeded"
  }'
```

## 🔐 Authentication

The service uses JWT Bearer token authentication. All endpoints (except `/health` and `/`) require a valid JWT token.

### Token Format

Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Token Payload

The JWT token must contain:
```json
{
  "user_id": 123,
  "sub": "123",
  "exp": 1234567890
}
```

### Generating Test Token

For testing, you can generate a token using the JWT handler:

```python
from app.core.security import jwt_handler

token = jwt_handler.create_access_token({"user_id": 1, "sub": "1"})
print(token)
```

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/test_payment_api.py
```

### Test Database Setup

Tests use a separate test database (`test_eygar_property_listing`). Make sure to create it:

```bash
createdb test_eygar_property_listing
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Ensure your PostgreSQL database is running**:
- Database: `eygar_property_listing`
- Host: `localhost:5432`
- User/Password configured in `.env`

2. **Start the payment service**:
```bash
docker-compose up -d
```

This starts:
- Payment service (port 8000)

**Note**: The service uses `network_mode: host` to connect to your external PostgreSQL database.

2. **View logs**:
```bash
docker-compose logs -f payment-service
```

3. **Stop services**:
```bash
docker-compose down
```

### Using Docker Only

1. **Build image**:
```bash
docker build -t payment-service:latest .
```

2. **Run container**:
```bash
docker run -d \
  --name payment-service \
  --network host \
  -e DATABASE_URL=postgresql+asyncpg://myuser:mypassword@localhost:5432/eygar_payment_db \
  -e SECRET_KEY=your-secret-key \
  payment-service:latest
```

**Note**: Uses `--network host` to connect to PostgreSQL on localhost.

## 📁 Project Structure

```
payment-service/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── payment.py          # Payment endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py               # Configuration
│   │   ├── database.py             # Database setup
│   │   └── security.py             # JWT handling
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── auth.py                 # Auth dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   └── payment.py              # Payment model
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── payment_repository.py  # Data access layer
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── payment.py              # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── payment_service.py     # Business logic
│   ├── __init__.py
│   └── main.py                     # FastAPI app
├── alembic/
│   ├── versions/
│   │   └── 001_initial.py         # Initial migration
│   ├── env.py
│   └── script.py.mako
├── tests/
│   ├── conftest.py                # Test fixtures
│   └── test_payment_api.py        # API tests
├── .env.example
├── .gitignore
├── .dockerignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 📊 Database Schema

### Payments Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| checkout_session_id | String(255) | Checkout session ID (nullable, unique) |
| payment_id | String(255) | Payment gateway ID (unique, required) |
| payment_method_id | String(255) | Payment method ID |
| payment_method_types | String(100) | Payment method types |
| payment_status | Enum | Payment status (pending, processing, succeeded, failed, canceled, refunded) |
| currency | String(3) | ISO 4217 currency code |
| amount_total | Numeric(10,2) | Payment amount |
| customer_id | String(255) | Customer ID |
| customer_email | String(255) | Customer email |
| booking_id | Integer | Associated booking ID |
| property_id | Integer | Associated property ID |
| user_id | Integer | User who made payment (required) |
| provider | Enum | Payment provider (stripe, paypal, square, razorpay, other) |
| description | Text | Payment description |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |

### Indexes

- Primary key on `id`
- Unique index on `checkout_session_id`
- Unique index on `payment_id`
- Index on `payment_status`
- Index on `customer_id`
- Index on `customer_email`
- Index on `booking_id`
- Index on `property_id`
- Index on `user_id`

## 🔧 Performance Optimizations

1. **Async Operations**: All database operations use async/await
2. **Connection Pooling**: Configured with pre-ping and optimal pool size
3. **Database Indexes**: Strategic indexes on frequently queried columns
4. **Pagination**: Efficient offset-based pagination
5. **Query Optimization**: Selective loading with proper filters

## 🛡️ Security Features

- JWT Bearer token authentication
- Password hashing (when integrated with user service)
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic)
- Authorization checks (user ownership verification)

## 📝 Development Notes

### Adding New Endpoints

1. Add route handler in `app/api/v1/payment.py`
2. Add service method in `app/services/payment_service.py`
3. Add repository method in `app/repositories/payment_repository.py`
4. Add tests in `tests/test_payment_api.py`

### Database Migrations

After modifying models:
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For issues and questions, please open an issue in the repository.

## 🔄 Version History

- **v1.0.0** - Initial release with core payment functionality
