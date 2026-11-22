"""Serves the front-end files and accepts new tickets at POST /api/tickets."""

from http.server import SimpleHTTPRequestHandler
from os import PathLike
from urllib.parse import urlsplit

from ticket_server import settings
from ticket_server.http_helpers import origin_allowed, read_json_body, send_json
from ticket_server.storage import save_ticket
from ticket_server.status_view import merged_ticket_statuses
from ticket_server.validation import validate_payload


class TicketRequestHandler(SimpleHTTPRequestHandler):
	timeout = settings.REQUEST_TIMEOUT_SECONDS

	def end_headers(self) -> None:
		self.send_header("X-Content-Type-Options", "nosniff")
		self.send_header("X-Frame-Options", "DENY")
		self.send_header("Referrer-Policy", "no-referrer")
		super().end_headers()

	def list_directory(self, path: str | PathLike[str]) -> None:
		"""Never show folder listings."""
		self.send_error(404, "Not found")
		return None

	def do_GET(self) -> None:
		"""Answer the status endpoint with JSON; serve everything else as static files."""
		if urlsplit(self.path).path != settings.STATUS_ENDPOINT:
			return super().do_GET()
		try:
			tickets, error = merged_ticket_statuses()
		except Exception as error:  # same last line of defence as do_POST
			self.log_error("Unexpected error: %r", error)
			return send_json(self, 500, {"error": "Unexpected server error."})
		if error:
			self.log_error("Status read failed: %s", error)
			return send_json(self, 500, {"error": "Could not read ticket statuses."})
		return send_json(self, 200, {"tickets": tickets})

	def do_POST(self) -> None:
		try:
			self.handle_ticket_post()
		except Exception as error:  # last line of defence: answer instead of dropping the request
			self.log_error("Unexpected error: %r", error)
			send_json(self, 500, {"error": "Unexpected server error."})

	def handle_ticket_post(self) -> None:
		if urlsplit(self.path).path != settings.TICKETS_ENDPOINT:
			return send_json(self, 404, {"error": "Not found."})
		if not origin_allowed(self.headers.get("Origin")):
			return send_json(self, 403, {"error": "Origin not allowed."})

		payload, problem = read_json_body(self)
		if problem:
			return send_json(self, problem[0], {"error": problem[1]})
		fields, error = validate_payload(payload)
		if error:
			return send_json(self, 400, {"error": error})

		ticket, error = save_ticket(fields["customer_id"], fields["text"])
		if error:
			self.log_error("Saving failed: %s", error)
			return send_json(self, 500, {"error": "Could not save the ticket."})
		return send_json(self, 201, {"id": ticket["id"]})
