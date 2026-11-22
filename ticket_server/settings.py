"""All settings for the ticket server live in this one file."""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Where the server listens. 127.0.0.1 means only this computer can reach it.
HOST = "127.0.0.1"
PORT = 8000

# What the server shows in the browser, and where it stores tickets.
STATIC_DIR = PROJECT_ROOT / "front-end"
TICKETS_FILE = PROJECT_ROOT / "tickets.json"
TICKETS_ENDPOINT = "/api/tickets"

# Written by run_graph.py, read by the dashboard (dashboard.html).
STATUS_FILE = PROJECT_ROOT / "ticket_status.json"
STATUS_ENDPOINT = "/api/tickets/status"

# Ticket IDs are handed out in order: T-1001, T-1002, ...
TICKET_ID_PREFIX = "T-"
TICKET_ID_START = 1001
TICKET_ID_PATTERN = re.compile(r"^T-(\d{1,9})$", re.ASCII)

# Rules that must match front-end/js/config/settings.js
CUSTOMER_ID_PATTERN = re.compile(r"^[A-Za-z0-9-]{1,20}$", re.ASCII)
TEXT_MIN_LENGTH = 10
TEXT_MAX_LENGTH = 2000

# Limits that protect the server from oversized or slow requests.
MAX_BODY_BYTES = 10_000
MAX_TICKETS_IN_FILE = 10_000
REQUEST_TIMEOUT_SECONDS = 10
ALLOWED_ORIGINS = {f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}"}
