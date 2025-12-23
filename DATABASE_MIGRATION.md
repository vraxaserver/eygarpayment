# Database Configuration - Migration Guide

## Changes Made

The payment service has been configured to use your external PostgreSQL database:

### Database Connection
- **Database Name**: `eygar_payment_db`
- **Host**: `localhost:5432`
- **User**: `myuser`
- **Password**: `mypassword` (update in `.env` with your actual password)

### What Changed

1. **Removed from docker-compose.yml**:
   - PostgreSQL container (now using external database)
   - Redis container (removed dependency)

2. **Docker Networking**:
   - Changed to `network_mode: host` to access localhost PostgreSQL
   - Removed isolated Docker network

3. **Python Version**:
   - Updated from Python 3.11-slim to Python 3.12-slim

4. **Dependencies**:
   - Removed Redis from requirements.txt
   - Removed Redis configuration from settings

## Setup Instructions

### 1. Ensure Database Exists

```bash
# Check if database exists
psql -h localhost -U myuser -l | grep eygar_payment_db

# If not exists, create it:
createdb -h localhost -U myuser eygar_payment_db
```

### 2. Update Environment File

```bash
cp .env.example .env

# Edit .env with your actual credentials:
DATABASE_URL=postgresql+asyncpg://myuser:mypassword@localhost:5432/eygar_payment_db
SECRET_KEY=your-actual-secret-key-min-32-characters
```

### 3. Run Database Migrations

```bash
# Create payments table
alembic upgrade head
```

This will create the `payments` table in your `eygar_payment_db` database.

### 4. Verify Migration

```bash
# Connect to database
psql -h localhost -U myuser -d eygar_payment_db

# List tables
\dt

# Check payments table structure
\d payments

# Exit
\q
```

You should see the `payments` table with all the required columns.

## Table Created

The migration creates a `payments` table with:

```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    checkout_session_id VARCHAR(255) UNIQUE,
    payment_id VARCHAR(255) UNIQUE NOT NULL,
    payment_method_id VARCHAR(255),
    payment_method_types VARCHAR(100),
    payment_status VARCHAR(50) NOT NULL DEFAULT 'pending',
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    amount_total NUMERIC(10,2) NOT NULL,
    customer_id VARCHAR(255),
    customer_email VARCHAR(255),
    booking_id INTEGER,
    property_id INTEGER,
    user_id INTEGER NOT NULL,
    provider VARCHAR(50) NOT NULL DEFAULT 'stripe',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- With indexes on:
-- payment_id, checkout_session_id, payment_status, 
-- customer_id, customer_email, booking_id, property_id, user_id
```

## Starting the Service

### Using Docker Compose

```bash
# Make sure PostgreSQL is running first
docker-compose up -d

# Check logs
docker-compose logs -f eygar-payment-service
```

### Using Local Python

```bash
# Activate virtual environment
source venv/bin/activate

# Start server
uvicorn app.main:app --reload
```

## Testing the Connection

```bash
# Health check
curl http://localhost:8002/health

# Should return:
# {"status":"healthy","service":"payment-service","version":"1.0.0"}
```

## Common Issues

### Issue: "could not connect to server"
**Solution**: Ensure PostgreSQL is running on localhost:5432
```bash
sudo systemctl status postgresql
# or
brew services list | grep postgresql  # macOS
```

### Issue: "database does not exist"
**Solution**: Create the database
```bash
createdb -h localhost -U myuser eygar_payment_db
```

### Issue: "password authentication failed"
**Solution**: Update `.env` with correct credentials
```bash
# Check PostgreSQL user exists
psql -U myuser -d postgres -c "\du"
```

### Issue: "relation 'payments' does not exist"
**Solution**: Run migrations
```bash
alembic upgrade head
```

## Integration with Other Services

The `payments` table includes foreign key references:
- `booking_id` - Links to your bookings service
- `property_id` - Links to your property listings service
- `user_id` - Links to your authentication service

You can add foreign key constraints later if needed:

```sql
-- Example (run in psql if you want FK constraints)
ALTER TABLE payments 
ADD CONSTRAINT fk_booking 
FOREIGN KEY (booking_id) 
REFERENCES bookings(id);

ALTER TABLE payments 
ADD CONSTRAINT fk_property 
FOREIGN KEY (property_id) 
REFERENCES properties(id);
```

## Rollback (if needed)

To remove the payments table:

```bash
# Rollback one migration
alembic downgrade -1

# Or rollback all
alembic downgrade base
```

## Next Steps

1. ✅ Verify database connection
2. ✅ Run migrations
3. ✅ Start the service
4. ✅ Test with API documentation at http://localhost:8002/docs
5. ✅ Integrate with your authentication service for JWT tokens
