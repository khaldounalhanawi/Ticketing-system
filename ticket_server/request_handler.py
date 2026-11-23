"""Serves the front-end files and sends API requests to the matching function in routes.py."""

from http.server import SimpleHTTPRequestHandler
from os import PathLike
from urllib.parse import urlsplit

from ticket_server import settings
from ticket_server.http_helpers import send_json
from ticket_server.routes import handle_resolve_post, handle_status_get, handle_ticket_post


class TicketRequestHandler(SimpleHTTPRequestHandler):
	timeout = settings.REQUEST_TIMEOUT_SECONDS

	def end_headers(self) -> None:
		"""Add security headers; make browsers re-check page files so code changes show up without a hard refresh."""
		if not urlsplit(self.path).path.startswith("/api/"):  # API replies already send no-store
			self.send_header("Cache-Control", "no-cache")
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
			handle_status_get(self)
		except Exception as error:  # last line of defence: answer instead of dropping the request
			self.log_error("Unexpected error: %r", error)
			send_json(self, 500, {"error": "Unexpected server error."})

	def do_POST(self) -> None:
		"""Send new tickets and review decisions to their route; anything else is 404."""
		path = urlsplit(self.path).path
		resolve_match = settings.RESOLVE_PATH_PATTERN.match(path)
		try:
			if path == settings.TICKETS_ENDPOINT:
				handle_ticket_post(self)
			elif resolve_match:
				handle_resolve_post(self, resolve_match.group(1))
			else:
				send_json(self, 404, {"error": "Not found."})
		except Exception as error:  # last line of defence: answer instead of dropping the request
			self.log_error("Unexpected error: %r", error)
			send_json(self, 500, {"error": "Unexpected server error."})
