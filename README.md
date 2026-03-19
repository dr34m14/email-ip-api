# Email & IP Extractor API

A FastAPI application for extracting emails and IP addresses from text, validating emails, and extracting emails from websites.

## Features

- Extract emails from text using regex
- Extract IPv4/IPv6 addresses from text (with validation)
- Validate email addresses (format + domain)
- Extract emails from website URLs (using BeautifulSoup)

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Start the development server:
```bash
uvicorn email_ip_api:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs for interactive API documentation.

### Endpoints

- `POST /extract` - Extract emails from text
- `POST /validate` - Validate email address  
- `POST /extract-ip` - Extract IP addresses from text
- `POST /extract-from-url` - Extract emails from URL

## Example Requests

```bash
# Extract emails
curl -X POST "http://localhost:8000/extract" -H "Content-Type: application/json" -d '{"text": "Contact: user@example.com"}'

# Validate email
curl -X POST "http://localhost:8000/validate" -H "Content-Type: application/json" -d '{"email": "user@example.com"}'

# Extract IPs
curl -X POST "http://localhost:8000/extract-ip" -H "Content-Type: application/json" -d '{"text": "Server: 192.168.1.1 and ::1"}'
```

# email-ip-api
