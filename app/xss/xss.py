from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from html import escape
from fastapi.templating import Jinja2Templates
router = APIRouter()
templates = Jinja2Templates(directory="xss/templates/")

# Mock database to store comments
comments = []

@router.get("/vulnerable", response_class=HTMLResponse)
def read_vulnerable(request: Request):
    """Vulnerable endpoint that renders user inputs directly."""
    return templates.TemplateResponse("vulnerable.html", {"request": request, "comments": comments})

@router.post("/vulnerable", response_class=HTMLResponse)
def submit_vulnerable_comment(comment: str = Form(...)):
    """Accepts user input and stores it without sanitization."""
    comments.append(comment)  
    return HTMLResponse(content="<p>Comment submitted!</p><a href='/vulnerable'>Back</a>", status_code=200)

@router.get("/secure", response_class=HTMLResponse)
def read_secure(request: Request):
    """Secure endpoint that sanitizes user inputs before rendering."""
    sanitized_comments = [escape(c) for c in comments]
    return templates.TemplateResponse("secure.html", {"request": request, "comments": sanitized_comments})

@router.post("/secure", response_class=HTMLResponse)
def submit_secure_comment(comment: str = Form(...)):
    """Accepts user input and sanitizes it before storing."""
    sanitized_comment = escape(comment)
    comments.append(sanitized_comment)
    return HTMLResponse(content="<p>Comment submitted securely!</p><a href='/secure'>Back</a>", status_code=200)
