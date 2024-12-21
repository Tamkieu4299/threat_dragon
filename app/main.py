from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from fastapi import FastAPI, Request, HTTPException, Depends
from db import get_db_connection
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address


# Create the FastAPI app with custom metadata
app = FastAPI(
    title="SQL Injection PoC API",
    description="""
This API demonstrates SQL Injection vulnerabilities and mitigations. 

### Endpoints:
1. **/vulnerable-login**: An intentionally vulnerable endpoint demonstrating raw SQL queries.
2. **/secure-login**: A secure implementation using parameterized queries.

Use these endpoints to test SQL Injection scenarios.
""",
    version="1.0.0"
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/vulnerable-login")
def login(username: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Example vulnerable query for testing SQL Injection
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(query)
        user = cursor.fetchall()

        if user:
            return {"message": "Login successful", "user": user}
        else:
            return {"message": "Invalid credentials"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/secure-login")
def secure_login(username: str, password: str):
    """
    Secure Login using password hashing and parameterized queries.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Parameterized query to prevent SQL injection
        query = "SELECT username, password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user and pwd_context.verify(password, user["password"]):
            return {"message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during login")
    finally:
        cursor.close()
        conn.close()


@app.post("/vulnerable-delete")
def vulnerable_delete(username: str):
    """
    Vulnerable Delete Endpoint
    Example input: username = admin'; DELETE FROM users WHERE id=1; --
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = f"DELETE FROM users WHERE username = '{username}'"
        cursor.execute(query)
        conn.commit()
        return {"message": "Tampering successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred")
    finally:
        cursor.close()
        conn.close()


@app.post("/secure-delete")
def secure_delete(username: str):
    """
    Secure endpoint to prevent tampering via SQL injection.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Parameterized query to prevent SQL injection
        query = "DELETE FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        conn.commit()
        return {"message": f"User {username} deleted successfully, if they existed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred during deletion")
    finally:
        cursor.close()
        conn.close()


@app.post("/vulnerable-dos")
def vulnerable_dos(username: str):
    """
    Vulnerable Endpoint with Potentially Long Query
    Example input: username = '; WAITFOR DELAY '00:00:20'; --
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = f"SELECT * FROM users WHERE username = '{username}'"
        cursor.execute(query)
        return {"message": "Query executed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred")
    finally:
        cursor.close()
        conn.close()

@app.post("/secure-dos")
@limiter.limit("5/minute")  # Limit to 5 requests per minute
def secure_dos(username: str, request: Request):
    """
    Secure endpoint to prevent DoS via rate limiting and input validation.
    """
    if len(username) > 50:
        raise HTTPException(status_code=400, detail="Input too long")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT id, username FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        return {"message": "Query executed securely"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred")
    finally:
        cursor.close()
        conn.close()