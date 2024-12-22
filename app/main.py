from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from fastapi import FastAPI, Request, HTTPException, Depends, UploadFile, Form
from db import get_db_connection
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address
import os
import subprocess
import uuid
from xss.xss import router as xss_router
from mitm.mitm import router as mitm_router

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

app.include_router(xss_router)
app.include_router(mitm_router)

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

@app.post("/upload-vulnerable")
async def upload_vulnerable(file: UploadFile, metadata: str = Form(...)):
    """
    Vulnerable file upload endpoint.
    Demonstrates shell injection using metadata or additional input fields.
    """
    try:
        # Save the uploaded file to a temporary directory
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # Vulnerable: Metadata is directly passed to the shell command
        os.system(f"file {file_location} && echo {metadata}")
        return {"message": f"File {file.filename} processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/upload-secure")
async def upload_file_secure(file: UploadFile, metadata: str = Form(...)):
    # Validate metadata
    if ";" in metadata or "&" in metadata or "|" in metadata:
        raise HTTPException(status_code=400, detail="Invalid metadata")

    # Save the file with a secure name
    import uuid
    safe_file_name = f"{uuid.uuid4()}.tmp"
    file_location = f"/tmp/{safe_file_name}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Secure: Use subprocess.run with shell=False
    result = subprocess.run(["echo", metadata], capture_output=True, text=True)
    return {"message": "File uploaded and processed securely", "output": result.stdout}