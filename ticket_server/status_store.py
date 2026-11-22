"""Reads and writes ticket_status.json: one status record per ticket, keyed by ticket ID.

run_graph.py writes a record after each ticket; the server reads them for the dashboard.
No langgraph import here, so the server stays light.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ticket_server.storage import write_tickets

if TYPE_CHECKING:  # type-only import, so the server never loads langgraph
	from langgraph.types import StateSnapshot

PENDING_HUMAN = "pending_human"
RESOLVED = "resolved"
FAILED = "failed"


def load_statuses(path: Path) -> tuple[dict[str, Any], None] | tuple[None, str]:
	"""Return (statuses_dict, None), or (None, error_message) if the file is unusable."""
	if not path.exists():
		return {}, None
	try:
		data = json.loads(path.read_text(encoding="utf-8"))
	except (OSError, ValueError):
		return None, f"{path.name} could not be read as JSON."
	if not isinstance(data, dict):
		return None, f"{path.name} must contain a JSON object."
	return data, None


def save_status(path: Path, ticket_id: str, record: dict[str, Any]) -> str | None:
	"""Add or replace one ticket's record. Return None, or an error message."""
	statuses, error = load_statuses(path)
	if error:
		return error
	statuses[ticket_id] = {**record, "updated_at": datetime.now(timezone.utc).isoformat()}
	try:
		write_tickets(path, statuses)
	except OSError:
		return f"{path.name} could not be written."
	return None


def status_from_snapshot(snapshot: StateSnapshot) -> dict[str, Any]:
	"""Turn a LangGraph state snapshot into a status record for the dashboard."""
	values = snapshot.values
	status = PENDING_HUMAN if snapshot.next else RESOLVED
	return {
		"status": status,
		"customer_id": values.get("customer_id", ""),
		"text": values.get("ticket_text", ""),
		"triage": values.get("triage", {}),
		"notes": values.get("notes", []),
		"resolution": values.get("resolution", {}),
	}


def failed_record(ticket: dict[str, Any], reason: str) -> dict[str, Any]:
	"""Status record for a ticket whose triage could not complete."""
	return {
		"status": FAILED,
		"customer_id": ticket.get("customer_id", ""),
		"text": ticket.get("text", ""),
		"triage": {},
		"notes": [reason],
		"resolution": {},
	}
