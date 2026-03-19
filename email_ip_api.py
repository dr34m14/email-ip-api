from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import ipaddress
from email_validator import validate_email, EmailNotValidError
from bs4 import BeautifulSoup
import requests

app = FastAPI(title="Email & IP Extractor API")

# -------------------------------
# Request Models
# -------------------------------
class TextRequest(BaseModel):
    text: str

class EmailRequest(BaseModel):
    email: str

# -------------------------------
# Utility functions
# -------------------------------
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
IPV4_REGEX = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
IPV6_REGEX = r"\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b"

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
# API Endpoints
# -------------------------------

# 1. Extract emails from text
@app.post("/extract")
def extract_emails(req: TextRequest):
    emails = extract_emails_from_text(req.text)
    return {"emails": emails}

# 2. Validate email
@app.post("/validate")
def validate_email_address(req: EmailRequest):
    try:
        v = validate_email(req.email)
        return {
            "valid": True,
            "format_ok": True,
            "domain_ok": True,
            "email": v.email
        }
    except EmailNotValidError as e:
        return {
            "valid": False,
            "format_ok": False,
            "domain_ok": False,
            "error": str(e)
        }

# 3. Extract IP addresses
@app.post("/extract-ip")
def extract_ips(req: TextRequest):
    ips = extract_ips_from_text(req.text)
    return {"ips": ips}

# 4. Optional: Extract emails from a website URL
@app.post("/extract-from-url")
def extract_emails_url(req: TextRequest):
    emails = extract_emails_from_url(req.text)
    return {"emails": emails}

