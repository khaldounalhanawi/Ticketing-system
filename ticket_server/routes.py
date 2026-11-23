"""What each API endpoint does. request_handler.py decides which of these runs."""

from http.server import BaseHTTPRequestHandler
from typing import Any

from scoutbot.tickets.resolve import ResolveProblem, resolve_ticket
from scoutbot.tickets.status_view import merged_ticket_statuses
from scoutbot.tickets.storage import save_ticket
from ticket_server import settings
from ticket_server.http_helpers import origin_allowed, read_json_body, send_json
from ticket_server.shared_graph import shared_graph
from ticket_server.validation import CATEGORIES, PRIORITIES, validate_decision, validate_payload

# How each core resolve problem is reported over HTTP.
RESOLVE_STATUS_CODES = {
	ResolveProblem.UNKNOWN_TICKET: 404,
	ResolveProblem.ALREADY_ANSWERED: 409,
	ResolveProblem.SAVE_FAILED: 500,
}


def _read_body(handler: BaseHTTPRequestHandler) -> tuple[Any, bool]:
	"""Check the origin and parse the JSON body; on a problem, answer the request and return (None, False)."""
	if not origin_allowed(handler.headers.get("Origin")):
		send_json(handler, 403, {"error": "Origin not allowed."})
		return None, False
	payload, problem = read_json_body(handler)
	if problem:
		send_json(handler, problem[0], {"error": problem[1]})
		return None, False
	return payload, True


def handle_status_get(handler: BaseHTTPRequestHandler) -> None:
	"""GET /api/tickets/status: every ticket with its status, plus the options the review form offers."""
	tickets, error = merged_ticket_statuses()
	if error:
		handler.log_error("Status read failed: %s", error)
		return send_json(handler, 500, {"error": "Could not read ticket statuses."})
	options = {"categories": CATEGORIES, "priorities": PRIORITIES}
	return send_json(handler, 200, {"tickets": tickets, "options": options})


def handle_ticket_post(handler: BaseHTTPRequestHandler) -> None:
	"""POST /api/tickets: validate a new ticket from the form and append it to data/tickets.json."""
	payload, ok = _read_body(handler)
	if not ok:
		return None
	fields, error = validate_payload(payload)
	if error:
		return send_json(handler, 400, {"error": error})
	ticket, error = save_ticket(fields["customer_id"], fields["text"])
	if error:
		handler.log_error("Saving failed: %s", error)
		return send_json(handler, 500, {"error": "Could not save the ticket."})
	return send_json(handler, 201, {"id": ticket["id"]})


def handle_resolve_post(handler: BaseHTTPRequestHandler, ticket_id: str) -> None:
	"""POST /api/tickets/<id>/resolve: apply a human's review decision to a paused ticket."""
	payload, ok = _read_body(handler)
	if not ok:
		return None
	decision, error = validate_decision(payload)
	if error:
		return send_json(handler, 400, {"error": error})
	record, problem = resolve_ticket(shared_graph(), ticket_id, decision, settings.STATUS_FILE)
	if problem:
		return send_json(handler, RESOLVE_STATUS_CODES[problem], {"error": problem.value})
	return send_json(handler, 200, {"ticket": {"id": ticket_id, **record}})
