#!/usr/bin/env bash
uvicorn email_ip_api:app --host 0.0.0.0 --port $PORT