import httpx
import asyncio

BASE_URL = "http://localhost:8001"

async def test_flow():
    async with httpx.AsyncClient() as client:
        # Register user
        register_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        }
        response = await client.post(f"{BASE_URL}/auth/", json=register_data)
        print("Register:", response.status_code, response.json() if response.status_code == 201 else response.text)

        # Login
        login_data = {
            "username": "test@example.com",
            "password": "password123"
        }
        response = await client.post(f"{BASE_URL}/auth/token", data=login_data)
        print("Login:", response.status_code)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(response.text)
            return

        # Update location
        location_data = {
            "latitude": 12.9716,
            "longitude": 77.5946
        }
        response = await client.post(f"{BASE_URL}/api/location/update", json=location_data, headers=headers)
        print("Update Location:", response.status_code, response.json())

        # Add contact
        contact_data = {
            "name": "Emergency Contact",
            "email": "contact@example.com",
            "phone_number": "1234567890",
            "relation": "Friend",
            "message": "Help me!"
        }
        response = await client.post(f"{BASE_URL}/api/contacts", json=contact_data, headers=headers)
        print("Add Contact:", response.status_code, response.json())

        # Trigger SOS
        response = await client.post(f"{BASE_URL}/api/sos/trigger", headers=headers)
        print("Trigger SOS:", response.status_code, response.json())

if __name__ == "__main__":
    asyncio.run(test_flow())