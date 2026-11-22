from typing import Optional
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from .state import TicketState
from .nodes import look_up_customer_node, triage_ticket_node, escalate_node, auto_resolve_node
from .helpers import route_after_triage, sqlite_checkpointer, thread_config
from .printers import print_custom, print_updates


def build_ticket_graph(checkpointer: Optional[BaseCheckpointSaver] = None):
	''' Build and compile the ticket-processing graph with its nodes and edges. '''
	builder = StateGraph(TicketState)
	builder.add_node("look_up_customer", look_up_customer_node)
	builder.add_node("triage_ticket", triage_ticket_node)
	builder.add_node("escalate", escalate_node)
	builder.add_node("auto_resolve", auto_resolve_node)

	builder.add_edge(START, "look_up_customer")
	builder.add_edge("look_up_customer", "triage_ticket")
	builder.add_conditional_edges(
		"triage_ticket",
		route_after_triage,
		{"escalate": "escalate", "auto_resolve": "auto_resolve"},
	)
	builder.add_edge("escalate", END)
	builder.add_edge("auto_resolve", END)

	return builder.compile(checkpointer=checkpointer)


def initial_state(
	ticket_text: str, customer_id: str, ticket_id: Optional[str] = None
	) -> TicketState:
	''' Create the starting state for a ticket with empty result fields. '''
	return {
		"ticket_id": ticket_id or "",
		"ticket_text": ticket_text,
		"customer_id": customer_id,
		"customer": {},
		"triage": {},
		"resolution": {},
		"notes": [],
	}


def stream_graph(graph, ticket: dict) -> None:
	''' Stream a ticket through the graph, printing node updates and custom status events. '''
	state = initial_state(ticket["text"], ticket["customer_id"], ticket["id"])
	config = thread_config(ticket["id"])
	for mode, chunk in graph.stream(
		state, stream_mode=["updates", "custom"], config=config, durability="sync"
	):
		if mode == "updates":
			print_updates(chunk)
		elif mode == "custom":
			print_custom(chunk)
