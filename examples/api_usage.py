"""
Example script demonstrating Payment Service API usage
"""
import asyncio
import httpx
from app.core.security import jwt_handler


async def main():
    """Example API interactions with the Payment Service."""
    
    # Base URL
    BASE_URL = "http://localhost:8000/api/v1"
    
    # Generate a JWT token for testing (user_id=1)
    token = jwt_handler.create_access_token({"user_id": 1, "sub": "1"})
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        
        print("=" * 60)
        print("Payment Service API Examples")
        print("=" * 60)
        
        # 1. Create a payment
        print("\n1. Creating a new payment...")
        payment_data = {
            "payment_id": "pi_example_123456789",
            "amount_total": 149.99,
            "currency": "USD",
            "payment_status": "pending",
            "provider": "stripe",
            "customer_email": "customer@example.com",
            "customer_id": "cus_123456",
            "booking_id": 1001,
            "property_id": 5001,
            "payment_method_types": "card",
            "description": "Payment for luxury apartment booking"
        }
        
        response = await client.post(
            f"{BASE_URL}/payments/",
            json=payment_data,
            headers=headers
        )
        
        if response.status_code == 201:
            payment = response.json()
            payment_id = payment["id"]
            print(f"✅ Payment created successfully!")
            print(f"   Payment ID: {payment_id}")
            print(f"   Amount: ${payment['amount_total']}")
            print(f"   Status: {payment['payment_status']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.json()}")
            return
        
        # 2. Get payment by ID
        print(f"\n2. Fetching payment by ID ({payment_id})...")
        response = await client.get(
            f"{BASE_URL}/payments/{payment_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            payment = response.json()
            print(f"✅ Payment retrieved successfully!")
            print(f"   Payment ID: {payment['payment_id']}")
            print(f"   Customer Email: {payment['customer_email']}")
        else:
            print(f"❌ Error: {response.status_code}")
        
        # 3. Update payment status
        print(f"\n3. Updating payment status to 'succeeded'...")
        response = await client.patch(
            f"{BASE_URL}/payments/{payment_id}/status",
            json={"payment_status": "succeeded"},
            headers=headers
        )
        
        if response.status_code == 200:
            payment = response.json()
            print(f"✅ Payment status updated!")
            print(f"   New Status: {payment['payment_status']}")
        else:
            print(f"❌ Error: {response.status_code}")
        
        # 4. Create more payments for pagination example
        print("\n4. Creating additional payments for pagination example...")
        for i in range(3):
            await client.post(
                f"{BASE_URL}/payments/",
                json={
                    "payment_id": f"pi_example_extra_{i}",
                    "amount_total": 50.00 + (i * 10),
                    "currency": "USD",
                    "payment_status": "succeeded",
                    "provider": "stripe",
                    "booking_id": 1002 + i
                },
                headers=headers
            )
        print("✅ Additional payments created!")
        
        # 5. Get user payments with pagination
        print("\n5. Fetching user payments (paginated)...")
        response = await client.get(
            f"{BASE_URL}/payments/?page=1&page_size=5",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total']} total payments")
            print(f"   Page: {data['page']}")
            print(f"   Page Size: {data['page_size']}")
            print(f"   Payments on this page: {len(data['payments'])}")
        else:
            print(f"❌ Error: {response.status_code}")
        
        # 6. Filter payments by status
        print("\n6. Filtering payments by status (succeeded)...")
        response = await client.get(
            f"{BASE_URL}/payments/?status=succeeded",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total']} succeeded payments")
            for payment in data['payments'][:3]:  # Show first 3
                print(f"   - {payment['payment_id']}: ${payment['amount_total']}")
        else:
            print(f"❌ Error: {response.status_code}")
        
        # 7. Get payments by booking ID
        print("\n7. Fetching payments for booking #1001...")
        response = await client.get(
            f"{BASE_URL}/payments/booking/1001",
            headers=headers
        )
        
        if response.status_code == 200:
            payments = response.json()
            print(f"✅ Found {len(payments)} payment(s) for booking #1001")
            for payment in payments:
                print(f"   - Payment: {payment['payment_id']}")
                print(f"     Amount: ${payment['amount_total']}")
                print(f"     Status: {payment['payment_status']}")
        else:
            print(f"❌ Error: {response.status_code}")
        
        # 8. Update payment details
        print(f"\n8. Updating payment description...")
        response = await client.put(
            f"{BASE_URL}/payments/{payment_id}",
            json={
                "description": "Updated: Payment completed successfully for luxury apartment",
                "customer_id": "cus_updated_123456"
            },
            headers=headers
        )
        
        if response.status_code == 200:
            payment = response.json()
            print(f"✅ Payment updated successfully!")
            print(f"   Description: {payment['description']}")
        else:
            print(f"❌ Error: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        print("\n📚 View full API documentation at: http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(main())
