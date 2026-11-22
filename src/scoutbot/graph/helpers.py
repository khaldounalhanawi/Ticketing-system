import json
import sqlite3
from pathlib import Path
from typing import Union
from langgraph.checkpoint.sqlite import SqliteSaver
from .state import TicketState
from scoutbot.schema import Priority


def ticket_with_customer(state: TicketState) -> str:
	''' Combine the ticket text and the customer record into one prompt string. '''
	return (
		f"{state['ticket_text']}\n\n"
		f"Customer record: {json.dumps(state['customer'], sort_keys=True)}"
	)


def route_after_triage(state: TicketState) -> str:
	''' Route to escalation for high-priority tickets, otherwise to auto-resolve. '''
	if state["triage"]["priority"] == Priority.high.value:
		return "escalate"
	return "auto_resolve"


def sqlite_checkpointer(db_path: Union[str, Path]) -> SqliteSaver:
	''' Create a SQLite-backed checkpointer that saves graph state to the given file. '''
	Path(db_path).parent.mkdir(parents=True, exist_ok=True)
	return SqliteSaver(sqlite3.connect(str(db_path), check_same_thread=False))


def thread_config(thread_id: str) -> dict:
	''' Build the LangGraph config that ties a run to the given thread ID. '''
	return {"configurable": {"thread_id": thread_id}}


def human_resolution(answer: dict | str, triage: dict) -> dict:
	''' Build the resolution from the human's answer; blank owner/priority fall back to the AI's triage. '''
	if not isinstance(answer, dict):  # a plain string from older callers is the decision alone
		answer = {"decision": str(answer)}
	return {
		"path": "human_resolved",
		"decision": answer.get("decision") or "(no decision given)",
		"owner": answer.get("owner") or triage.get("suggested_owner", "support-team"),
		"priority": answer.get("priority") or triage.get("priority", ""),
	}
