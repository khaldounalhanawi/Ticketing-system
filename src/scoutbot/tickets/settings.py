"""Settings for ticket data: where the files live and how ticket IDs look. No web settings here."""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]   # src/scoutbot/tickets/settings.py -> project root

# data/ holds files the app writes (gitignored). seed/ holds committed template data.
# This is the one place these paths are defined; the server and the scripts import them from here.
DATA_DIR = PROJECT_ROOT / "data"
SEED_DIR = PROJECT_ROOT / "seed"

TICKETS_FILE = DATA_DIR / "tickets.json"            # form submissions
STATUS_FILE = DATA_DIR / "ticket_status.json"       # one status record per ticket
CHECKPOINTS_FILE = DATA_DIR / "checkpoints.db"      # paused graph runs
SAMPLE_TICKETS_FILE = SEED_DIR / "sample_tickets.json"

# Ticket IDs are handed out in order: T-1001, T-1002, ...
TICKET_ID_PREFIX = "T-"
TICKET_ID_START = 1001
TICKET_ID_PATTERN = re.compile(r"^T-(\d{1,9})$", re.ASCII)

MAX_TICKETS_IN_FILE = 10_000
