"""Reads and writes data/tickets.json safely.

- A lock makes sure two requests never write at the same time.
- Writes go to a temporary file first and then replace the real file,
  so a crash mid-write can never leave tickets.json half-written.
- If tickets.json is damaged, nothing is written, so no tickets are lost.
"""

import json
import os
import threading
from pathlib import Path
from typing import Any

from scoutbot.tickets import settings

_write_lock = threading.Lock()


def load_tickets(path: Path) -> tuple[list[Any], None] | tuple[None, str]:
	"""Return (tickets, None), or (None, error_message) if the file is unusable."""
	if not path.exists():
		return [], None
	try:
		data = json.loads(path.read_text(encoding="utf-8"))
	except (OSError, ValueError):
		return None, f"{path.name} could not be read as JSON."
	if not isinstance(data, list):
		return None, f"{path.name} must contain a JSON list."
	return data, None


def next_ticket_id(tickets: list[Any]) -> str:
	"""Return the ID after the highest existing T-<number> ID."""
	highest = settings.TICKET_ID_START - 1
	for ticket in tickets:
		ticket_id = ticket.get("id") if isinstance(ticket, dict) else None
		match = settings.TICKET_ID_PATTERN.match(ticket_id) if isinstance(ticket_id, str) else None
		if match:
			highest = max(highest, int(match.group(1)))
	return f"{settings.TICKET_ID_PREFIX}{highest + 1}"


def write_tickets(path: Path, tickets: list[Any] | dict[str, Any]) -> None:
	"""Write the full list to disk in one step."""
	path.parent.mkdir(parents=True, exist_ok=True)  # data/ is gitignored, so a fresh clone lacks it
	temporary_path = path.with_name(path.name + ".tmp")
	content = json.dumps(tickets, indent=2, ensure_ascii=False) + "\n"
	temporary_path.write_text(content, encoding="utf-8")
	os.replace(temporary_path, path)


def save_ticket(customer_id: str, text: str) -> tuple[dict[str, str], None] | tuple[None, str]:
	"""Append a new ticket. Return (ticket, None), or (None, error_message)."""
	with _write_lock:
		tickets, error = load_tickets(settings.TICKETS_FILE)
		if error:
			return None, error
		if len(tickets) >= settings.MAX_TICKETS_IN_FILE:
			return None, "The tickets file is full."

		ticket = {"id": next_ticket_id(tickets), "customer_id": customer_id, "text": text}
		try:
			write_tickets(settings.TICKETS_FILE, tickets + [ticket])
		except OSError:
			return None, "The ticket could not be written to disk."
		return ticket, None
