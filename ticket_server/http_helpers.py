"""Small helpers for reading and answering HTTP requests."""

import json

from ticket_server import settings


def origin_allowed(origin):
    """Block other websites from posting to this server. A missing Origin is allowed (e.g. curl)."""
    return origin is None or origin in settings.ALLOWED_ORIGINS


def read_json_body(handler):
    """Return (payload, None), or (None, (status_code, error_message))."""
    content_type = handler.headers.get("Content-Type", "").split(";")[0].strip().lower()
    if content_type != "application/json":
        return None, (415, "Content-Type must be application/json.")
    try:
        length = int(handler.headers.get("Content-Length", ""))
    except ValueError:
        return None, (411, "Content-Length header is required.")
    if length <= 0 or length > settings.MAX_BODY_BYTES:
        return None, (413, "Request body is empty or too large.")
    try:
        return json.loads(handler.rfile.read(length).decode("utf-8")), None
    except (UnicodeDecodeError, ValueError):
        return None, (400, "Request body is not valid JSON.")


def send_json(handler, status, payload):
    """Send a JSON response with the given status code."""
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)
