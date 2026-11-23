from scoutbot import sqlite_checkpointer
from scoutbot.tickets.settings import TICKETS_FILE, SAMPLE_TICKETS_FILE, STATUS_FILE, CHECKPOINTS_FILE

# Tickets from the submission form if there are any, otherwise the sample set.
TICKETS_PATH	= TICKETS_FILE if TICKETS_FILE.exists() else SAMPLE_TICKETS_FILE
STATUS_PATH		= STATUS_FILE
DB_PATH			= CHECKPOINTS_FILE

# File-backed so escalated tickets survive the process and can be resumed later.
CHECKPOINTER	= sqlite_checkpointer (DB_PATH)
