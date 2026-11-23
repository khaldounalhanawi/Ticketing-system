"""Web settings for the ticket server. Data paths come from scoutbot.tickets.settings."""

import re

# Re-exported so server code reads every setting from this one module.
from scoutbot.tickets.settings import CHECKPOINTS_FILE, PROJECT_ROOT, STATUS_FILE, TICKETS_FILE  # noqa: F401

# Where the server listens. 127.0.0.1 means only this computer can reach it.
HOST = "127.0.0.1"
PORT = 8000

# What the server shows in the browser. Never put data files in here: it is public.
STATIC_DIR = PROJECT_ROOT / "front-end"

TICKETS_ENDPOINT = "/api/tickets"
STATUS_ENDPOINT = "/api/tickets/status"
# POST /api/tickets/<ticket id>/resolve applies a human's review decision.
RESOLVE_PATH_PATTERN = re.compile(r"^/api/tickets/([A-Za-z0-9-]{1,20})/resolve$", re.ASCII)

# Rules for a human review decision (dashboard.html review form).
DECISION_MAX_LENGTH = 500
OWNER_PATTERN = re.compile(r"^[A-Za-z0-9 _-]{0,60}$", re.ASCII)

# Rules that must match front-end/js/config/settings.js
CUSTOMER_ID_PATTERN = re.compile(r"^[A-Za-z0-9-]{1,20}$", re.ASCII)
TEXT_MIN_LENGTH = 10
TEXT_MAX_LENGTH = 2000

# Limits that protect the server from oversized or slow requests.
MAX_BODY_BYTES = 10_000
REQUEST_TIMEOUT_SECONDS = 10
ALLOWED_ORIGINS = {f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}"}
