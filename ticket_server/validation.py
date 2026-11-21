"""Checks incoming tickets again on the server. Browser checks can be bypassed."""

import re
import unicodedata

from ticket_server import settings

HIDDEN_CHARS = re.compile(
    "[\x00-\x08\x0b\x0c\x0e-\x1f\x7f​-‏‪-‮⁠-⁩﻿]"
)


def clean_text(value):
    """Return the value as a clean single-line string, or "" if it is not a string."""
    if not isinstance(value, str):
        return ""
    value = unicodedata.normalize("NFC", value)
    value = HIDDEN_CHARS.sub("", value)
    return " ".join(value.split())


def validate_payload(payload):
    """Return (cleaned_fields, None) when valid, or (None, error_message)."""
    if not isinstance(payload, dict):
        return None, "Request body must be a JSON object."

    customer_id = clean_text(payload.get("customer_id")).replace(" ", "")
    text = clean_text(payload.get("text"))

    # The customer ID is optional: "" means the customer has no ID.
    if customer_id and not settings.CUSTOMER_ID_PATTERN.match(customer_id):
        return None, "Customer ID is invalid."
    if len(text) < settings.TEXT_MIN_LENGTH:
        return None, "Issue description is too short."
    if len(text) > settings.TEXT_MAX_LENGTH:
        return None, "Issue description is too long."
    return {"customer_id": customer_id, "text": text}, None
