from pathlib import Path
from scoutbot import sqlite_checkpointer

ROOT			= Path (__file__).parent
FORM_TICKETS	= ROOT / "tickets.json"
SAMPLE_TICKETS	= ROOT / "sample_tickets.json"

# Tickets from the submission form if there are any, otherwise the sample set.
TICKETS_PATH	= FORM_TICKETS if FORM_TICKETS.exists() else SAMPLE_TICKETS
STATUS_PATH		= ROOT / "ticket_status.json"
DB_PATH			= ROOT / "checkpoints.db"

# File-backed so escalated tickets survive the process and can be resumed later.
CHECKPOINTER	= sqlite_checkpointer (DB_PATH)
