
from langgraph.types import interrupt
from scoutbot.core import triage
from scoutbot.tools import look_up_customer
from langgraph.config import get_stream_writer
from .state import TicketState
from .helpers import human_resolution, ticket_with_customer
from .utils import otel

@otel
def look_up_customer_node(state: TicketState) -> dict:
	''' Fetch the customer record and add a note on whether it was found. '''
	writer = get_stream_writer()
	writer({"status": "Looking up customer:"})

	record = look_up_customer(state["customer_id"])
	outcome = "found" if record.get("found") else "not found"
	return {
		"customer": record,
		"notes": [f"looked up {state['customer_id']}: {outcome}"],
	}

@otel
def triage_ticket_node(state: TicketState) -> dict:
	''' Classify the ticket with the LLM and store the triage result. '''
	writer = get_stream_writer()
	writer({"status": "Calling Mr.Agent..."})

	result = triage(ticket_with_customer(state))
	return {
		"triage": result.model_dump(mode="json"),
		"notes": [f"triaged as {result.category.value}/{result.priority.value}"],
	}

@otel
def escalate_node(state: TicketState) -> dict:
	''' Pause for a human, apply their priority/owner to the triage and keep the AI's original in resolution. '''
	writer = get_stream_writer()
	writer({"status": "HUMAN ASSISTANCE NEEDED!"})

	answer = interrupt({
		'ticket': state['ticket_text'],
		'triage': state['triage'],
		'notes': state['notes'],
	})

	resolution = human_resolution(answer, state['triage'])
	return {
		"triage": {
			**state['triage'],
			"priority": resolution['priority'],
			"suggested_owner": resolution['owner'],
		},
		"resolution": {**resolution, "ai_triage": state['triage']},
		"notes": [f"human decided: {resolution['decision']} "
				  f"({resolution['priority']}, {resolution['owner']})"],
	}

@otel
def auto_resolve_node(state: TicketState) -> dict:
	''' Terminal node for everything else: ScoutBot handles it and the run is done. '''
	writer = get_stream_writer()
	writer({"status": "Autoresolved."})
	return {
		"resolution": {
			"path": "auto_resolved",
			"awaiting_human": False,
			"owner": state["triage"].get("suggested_owner", "support-team"),
		},
		"notes": ["auto-resolved: no human needed"],
	}