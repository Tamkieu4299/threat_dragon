from fastapi import APIRouter
import requests

# Create a router for MITM demo endpoints
router = APIRouter()

@router.get("/send-data")
async def send_data():
    # Example of sensitive data (this should NEVER be sent without encryption)
    sensitive_data = {
        "username": "victim_user",
        "password": "password123"
    }
    # Simulating an HTTP connection (plain text, susceptible to MITM)
    response = requests.post("http://example.com/receive-data", json=sensitive_data)
    return {"status": "Data sent", "response_code": response.status_code}

@router.get("/send-secure-data")
async def send_secure_data():
    sensitive_data = {
        "username": "secure_user",
        "password": "securePassword123"
    }
    # Simulating a secure HTTPS connection
    response = requests.post("https://secure.example.com/receive-data", json=sensitive_data)
    return {"status": "Secure data sent", "response_code": response.status_code}

@router.post("/spoofed-data")
async def spoofed_data(payload: dict):
    """
    Simulates an attacker modifying data during transit.
    """
    # Simulate an intercepted payload modification
    if "username" in payload and "password" in payload:
        spoofed_payload = payload.copy()
        spoofed_payload["username"] = "hacker_user"
        spoofed_payload["password"] = "hackedPassword123"

        # Simulate sending the spoofed data to the target
        response = requests.post("http://example.com/receive-data", json=spoofed_payload)

        return {
            "original_payload": payload,
            "spoofed_payload": spoofed_payload,
            "response_code": response.status_code,
            "response_text": response.text
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid payload format. Must include 'username' and 'password'.")
