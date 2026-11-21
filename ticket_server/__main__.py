"""Start the ticket server:  python -m ticket_server"""

from functools import partial
from http.server import ThreadingHTTPServer

from ticket_server import settings
from ticket_server.request_handler import TicketRequestHandler


def run():
	handler = partial(TicketRequestHandler, directory=str(settings.STATIC_DIR))
	try:
		server = ThreadingHTTPServer((settings.HOST, settings.PORT), handler)
	except OSError as error:
		print(f"Could not start on port {settings.PORT}: {error}")
		return

	print(f"Form:    http://{settings.HOST}:{settings.PORT}/submission_form.html")
	print(f"Tickets: {settings.TICKETS_FILE}")
	print("Press Ctrl+C to stop.")
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		print("\nStopped.")
	finally:
		server.server_close()


if __name__ == "__main__":
	run()
