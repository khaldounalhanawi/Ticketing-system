"""Checks incoming tickets and review decisions again on the server. Browser checks can be bypassed."""

import re
import unicodedata
from typing import Any

from scoutbot.schema import Category, Priority
from ticket_server import settings

CATEGORIES = [category.value for category in Category]
PRIORITIES = [priority.value for priority in Priority]
DECISION_FIELDS = ("decision", "owner", "category", "priority")

HIDDEN_CHARS = re.compile(
    "[\x00-\x08\x0b\x0c\x0e-\x1f\x7f​-‏‪-‮⁠-⁩﻿]"
)


def clean_text(value: Any) -> str:
    """Return the value as a clean single-line string, or "" if it is not a string."""
    if not isinstance(value, str):
        return ""
    value = unicodedata.normalize("NFC", value)
    value = HIDDEN_CHARS.sub("", value)
    return " ".join(value.split())


def validate_payload(payload: Any) -> tuple[dict[str, str], None] | tuple[None, str]:
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


def validate_decision(payload: Any) -> tuple[dict[str, str], None] | tuple[None, str]:
    """Return (cleaned_decision, None) when valid, or (None, error_message); blank fields keep the AI's value."""
    if not isinstance(payload, dict):
        return None, "Request body must be a JSON object."
    decision = {field: clean_text(payload.get(field)) for field in DECISION_FIELDS}
    decision["category"] = decision["category"].lower()
    decision["priority"] = decision["priority"].lower()

    if not decision["decision"]:
        return None, "Please describe your decision."
    if len(decision["decision"]) > settings.DECISION_MAX_LENGTH:
        return None, "Decision is too long."
    if not settings.OWNER_PATTERN.match(decision["owner"]):
        return None, "Team may only contain letters, numbers, spaces, dashes and underscores."
    if decision["category"] and decision["category"] not in CATEGORIES:
        return None, "Category is invalid."
    if decision["priority"] and decision["priority"] not in PRIORITIES:
        return None, "Priority is invalid."
    return decision, None
