from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import re
import ipaddress
from email_validator import validate_email, EmailNotValidError
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta

app = FastAPI(title="Email & IP Extractor API with API Key")

# -------------------------------
# Request Models
# -------------------------------
class TextRequest(BaseModel):
    text: str

class EmailRequest(BaseModel):
    email: str

# -------------------------------
# API Key Config
# -------------------------------
# Example API keys with tier, usage counter, and reset timestamp
API_KEYS = {
    "FREE-12345": {"tier": "free", "requests": 0, "reset_time": datetime.utcnow()},
    "PAID-ABCDE": {"tier": "paid", "requests": 0, "reset_time": datetime.utcnow()},
}

FREE_LIMIT = 50   # requests/day
PAID_LIMIT = 1000 # requests/day

# -------------------------------
# Utility Functions
# -------------------------------
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

def extract_emails_from_text(text: str):
    return re.findall(EMAIL_REGEX, text)

def extract_ips_from_text(text: str):
    words = text.split()
    ips = []
    for word in words:
        try:
            ip = ipaddress.ip_address(word)
            ips.append({"ip": str(ip), "type": "IPv4" if ip.version == 4 else "IPv6"})
        except ValueError:
            continue
    return ips

def extract_emails_from_url(url: str):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text()
        return extract_emails_from_text(text)
    except:
        return []

# -------------------------------
# Middleware: API Key + Rate Limit
# -------------------------------
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    path = request.url.path
    if path.startswith("/docs") or path.startswith("/openapi.json"):
        return await call_next(request)  # allow swagger UI
    
    api_key = request.headers.get("X-API-KEY")
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API Key")
    
    key_data = API_KEYS.get(api_key)
    if not key_data:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    # Reset daily limit if 24h passed
    if datetime.utcnow() - key_data["reset_time"] > timedelta(days=1):
        key_data["requests"] = 0
        key_data["reset_time"] = datetime.utcnow()
    
    # Check rate limit
    limit = FREE_LIMIT if key_data["tier"] == "free" else PAID_LIMIT
    if key_data["requests"] >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Increment usage
    key_data["requests"] += 1
    
    response = await call_next(request)
    return response

# -------------------------------
# API Endpoints
# -------------------------------

@app.post("/extract")
def extract_emails(req: TextRequest):
    emails = extract_emails_from_text(req.text)
    return {"emails": emails}

@app.post("/validate")
def validate_email_address(req: EmailRequest):
    try:
        v = validate_email(req.email, check_deliverability=False)  # skip MX check if desired
        return {"valid": True, "format_ok": True, "domain_ok": True, "email": v.email}
    except EmailNotValidError as e:
        return {"valid": False, "format_ok": False, "domain_ok": False, "error": str(e)}

@app.post("/extract-ip")
def extract_ips(req: TextRequest):
    ips = extract_ips_from_text(req.text)
    return {"ips": ips}

@app.post("/extract-from-url")
def extract_emails_url(req: TextRequest):
    emails = extract_emails_from_url(req.text)
    return {"emails": emails}