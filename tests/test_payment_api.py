import pytest
from httpx import AsyncClient
from decimal import Decimal


class TestPaymentAPI:
    """Test suite for Payment API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_payment(self, client: AsyncClient, auth_headers: dict):
        """Test creating a new payment."""
        payment_data = {
            "payment_id": "pi_test_12345",
            "amount_total": 99.99,
            "currency": "USD",
            "payment_status": "pending",
            "provider": "stripe",
            "customer_email": "test@example.com",
            "booking_id": 1,
            "property_id": 1,
            "description": "Test payment"
        }
        
        response = await client.post(
            "/api/v1/payments/",
            json=payment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["payment_id"] == payment_data["payment_id"]
        assert float(data["amount_total"]) == payment_data["amount_total"]
        assert data["user_id"] == 1
    
    @pytest.mark.asyncio
    async def test_create_payment_duplicate(self, client: AsyncClient, auth_headers: dict):
        """Test creating a payment with duplicate payment_id."""
        payment_data = {
            "payment_id": "pi_test_duplicate",
            "amount_total": 50.00,
            "currency": "USD"
        }
        
        # Create first payment
        await client.post(
            "/api/v1/payments/",
            json=payment_data,
            headers=auth_headers
        )
        
        # Try to create duplicate
        response = await client.post(
            "/api/v1/payments/",
            json=payment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_create_payment_unauthorized(self, client: AsyncClient):
        """Test creating a payment without authentication."""
        payment_data = {
            "payment_id": "pi_test_unauth",
            "amount_total": 99.99
        }
        
        response = await client.post(
            "/api/v1/payments/",
            json=payment_data
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_payment_by_id(self, client: AsyncClient, auth_headers: dict):
        """Test retrieving a payment by ID."""
        # Create payment
        payment_data = {
            "payment_id": "pi_test_get",
            "amount_total": 75.50,
            "currency": "EUR"
        }
        
        create_response = await client.post(
            "/api/v1/payments/",
            json=payment_data,
            headers=auth_headers
        )
        payment_id = create_response.json()["id"]
        
        # Get payment
        response = await client.get(
            f"/api/v1/payments/{payment_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == payment_id
        assert data["payment_id"] == payment_data["payment_id"]
    
    @pytest.mark.asyncio
    async def test_get_payment_unauthorized(
        self,
        client: AsyncClient,
        auth_headers: dict,
        auth_headers_user2: dict
    ):
        """Test retrieving another user's payment."""
        # Create payment as user 1
        payment_data = {
            "payment_id": "pi_test_forbidden",
            "amount_total": 100.00
        }
        
        create_response = await client.post(
            "/api/v1/payments/",
            json=payment_data,
            headers=auth_headers
        )
        payment_id = create_response.json()["id"]
        
        # Try to get as user 2
        response = await client.get(
            f"/api/v1/payments/{payment_id}",
            headers=auth_headers_user2
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_user_payments(self, client: AsyncClient, auth_headers: dict):
        """Test retrieving user's payment list."""
        # Create multiple payments
        for i in range(3):
            await client.post(
                "/api/v1/payments/",
                json={
                    "payment_id": f"pi_test_list_{i}",
                    "amount_total": 50.00 * (i + 1)
                },
                headers=auth_headers
            )
        
        # Get user payments
        response = await client.get(
            "/api/v1/payments/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["payments"]) == 3
    
    @pytest.mark.asyncio
    async def test_get_user_payments_with_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test payment list pagination."""
        # Create 5 payments
        for i in range(5):
            await client.post(
                "/api/v1/payments/",
                json={
                    "payment_id": f"pi_test_page_{i}",
                    "amount_total": 25.00
                },
                headers=auth_headers
            )
        
        # Get page 1 with 2 items
        response = await client.get(
            "/api/v1/payments/?page=1&page_size=2",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["payments"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_user_payments_with_status_filter(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test filtering payments by status."""
        # Create payments with different statuses
        await client.post(
            "/api/v1/payments/",
            json={
                "payment_id": "pi_test_pending",
                "amount_total": 50.00,
                "payment_status": "pending"
            },
            headers=auth_headers
        )
        
        await client.post(
            "/api/v1/payments/",
            json={
                "payment_id": "pi_test_succeeded",
                "amount_total": 100.00,
                "payment_status": "succeeded"
            },
            headers=auth_headers
        )
        
        # Filter by status
        response = await client.get(
            "/api/v1/payments/?status=succeeded",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["payments"][0]["payment_status"] == "succeeded"
    
    @pytest.mark.asyncio
    async def test_get_payment_by_gateway_id(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test retrieving payment by gateway payment_id."""
        payment_data = {
            "payment_id": "pi_test_gateway",
            "amount_total": 150.00
        }
        
        await client.post(
            "/api/v1/payments/",
            json=payment_data,
            headers=auth_headers
        )
        
        response = await client.get(
            f"/api/v1/payments/payment-gateway/{payment_data['payment_id']}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["payment_id"] == payment_data["payment_id"]
    
    @pytest.mark.asyncio
    async def test_get_booking_payments(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test retrieving payments by booking ID."""
        booking_id = 123
        
        # Create payments for booking
        for i in range(2):
            await client.post(
                "/api/v1/payments/",
                json={
                    "payment_id": f"pi_test_booking_{i}",
                    "amount_total": 100.00,
                    "booking_id": booking_id
                },
                headers=auth_headers
            )
        
        response = await client.get(
            f"/api/v1/payments/booking/{booking_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        payments = response.json()
        assert len(payments) == 2
        assert all(p["booking_id"] == booking_id for p in payments)
    
    @pytest.mark.asyncio
    async def test_update_payment(self, client: AsyncClient, auth_headers: dict):
        """Test updating payment details."""
        # Create payment
        payment_data = {
            "payment_id": "pi_test_update",
            "amount_total": 100.00,
            "description": "Original description"
        }
        
        create_response = await client.post(
            "/api/v1/payments/",
            json=payment_data,
            headers=auth_headers
        )
        payment_id = create_response.json()["id"]
        
        # Update payment
        update_data = {
            "description": "Updated description",
            "customer_email": "updated@example.com"
        }
        
        response = await client.put(
            f"/api/v1/payments/{payment_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == update_data["description"]
        assert data["customer_email"] == update_data["customer_email"]
    
    @pytest.mark.asyncio
    async def test_update_payment_status(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test updating payment status."""
        # Create payment
        payment_data = {
            "payment_id": "pi_test_status_update",
            "amount_total": 75.00,
            "payment_status": "pending"
        }
        
        create_response = await client.post(
            "/api/v1/payments/",
            json=payment_data,
            headers=auth_headers
        )
        payment_id = create_response.json()["id"]
        
        # Update status
        response = await client.patch(
            f"/api/v1/payments/{payment_id}/status",
            json={"payment_status": "succeeded"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["payment_status"] == "succeeded"
    
    @pytest.mark.asyncio
    async def test_delete_payment(self, client: AsyncClient, auth_headers: dict):
        """Test canceling a payment."""
        # Create payment
        payment_data = {
            "payment_id": "pi_test_delete",
            "amount_total": 50.00
        }
        
        create_response = await client.post(
            "/api/v1/payments/",
            json=payment_data,
            headers=auth_headers
        )
        payment_id = create_response.json()["id"]
        
        # Delete payment
        response = await client.delete(
            f"/api/v1/payments/{payment_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "canceled" in response.json()["message"].lower()
        
        # Verify status changed
        get_response = await client.get(
            f"/api/v1/payments/{payment_id}",
            headers=auth_headers
        )
        assert get_response.json()["payment_status"] == "canceled"
