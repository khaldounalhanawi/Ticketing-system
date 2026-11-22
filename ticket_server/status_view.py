"""Builds the list the dashboard shows: every known ticket with its current status."""

from pathlib import Path
from typing import Any

from ticket_server import settings
from ticket_server.status_store import load_statuses
from ticket_server.storage import load_tickets

NEW = "new"


def _new_record(ticket: dict[str, Any]) -> dict[str, Any]:
	"""Record for a submitted ticket that has not been triaged yet."""
	return {
		"status": NEW,
		"customer_id": ticket.get("customer_id", ""),
		"text": ticket.get("text", ""),
		"triage": {},
		"notes": [],
		"resolution": {},
	}


def merged_ticket_statuses(
	tickets_file: Path | None = None,
	status_file: Path | None = None,
) -> tuple[list[dict[str, Any]], None] | tuple[None, str]:
	"""Return (list_of_tickets, None), or (None, error_message).

	Tickets without a status record count as "new". Records whose ticket is not in
	tickets.json (e.g. sample tickets) are still included.
	"""
	tickets, error = load_tickets(tickets_file or settings.TICKETS_FILE)
	if error:
		return None, error
	statuses, error = load_statuses(status_file or settings.STATUS_FILE)
	if error:
		return None, error

	merged = {}
	for ticket in tickets:
		if isinstance(ticket, dict) and isinstance(ticket.get("id"), str):
			merged[ticket["id"]] = _new_record(ticket)
	for ticket_id, record in statuses.items():
		if isinstance(record, dict):
			merged[ticket_id] = record
	return [{"id": ticket_id, **record} for ticket_id, record in merged.items()], None
