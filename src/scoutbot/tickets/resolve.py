"""Applies a human's review decision: resumes the ticket's paused graph run and saves its new status.

Used by the dashboard (through ticket_server) and by run_answer.py. Knows nothing about HTTP:
problems come back as a ResolveProblem, and each front end decides how to show them.
"""

import threading
from enum import Enum
from pathlib import Path
from typing import Any

from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command

from scoutbot.graph import thread_config
from scoutbot.tickets.status_store import save_status, status_from_snapshot

_resolve_lock = threading.Lock()    # two threads can never resume the same run at the same time


class ResolveProblem(Enum):
	"""Why a decision could not be applied; the value is a message a person can read."""

	UNKNOWN_TICKET = "Unknown ticket."
	ALREADY_ANSWERED = "This ticket was already answered."
	SAVE_FAILED = "Decision applied, but the status file could not be saved."


def resolve_ticket(
	graph: CompiledStateGraph, ticket_id: str, decision: dict[str, Any], status_file: Path
) -> tuple[dict[str, Any], None] | tuple[None, ResolveProblem]:
	"""Resume a paused ticket with the decision; return (record, None) or (None, problem)."""
	config = thread_config(ticket_id)
	with _resolve_lock:
		snapshot = graph.get_state(config)
		if not snapshot.values:
			return None, ResolveProblem.UNKNOWN_TICKET
		if not snapshot.next:
			# Already answered elsewhere: repair a stale status record instead of resuming twice.
			save_status(status_file, ticket_id, status_from_snapshot(snapshot))
			return None, ResolveProblem.ALREADY_ANSWERED
		graph.invoke(Command(resume=decision), config)
		record = status_from_snapshot(graph.get_state(config))
		error = save_status(status_file, ticket_id, record)
	if error:
		return None, ResolveProblem.SAVE_FAILED
	return record, None
