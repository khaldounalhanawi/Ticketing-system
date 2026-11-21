from pathlib import Path
from scoutbot import sqlite_checkpointer
from langgraph.checkpoint.memory import InMemorySaver

TICKETS_PATH	= Path (__file__).parent / "sample_tickets.json"
DB_PATH			= Path (__file__).parent / "checkpoints.db"

# CHECKPOINTER	= sqlite_checkpointer (DB_PATH)
CHECKPOINTER	= InMemorySaver()