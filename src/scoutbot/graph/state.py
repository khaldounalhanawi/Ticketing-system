import operator
from typing import Annotated, TypedDict


class TicketState(TypedDict):
	ticket_id: str
	ticket_text: str
	customer_id: str
	customer: dict
	triage: dict
	resolution: dict
	notes: Annotated[list[str], operator.add]
