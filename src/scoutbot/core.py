import os

from anthropic import Anthropic

from .schema import TicketTriage

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")

TRIAGE_TOOL = {
	"name": "triage_ticket",
	"description": "Record the triage decision for a single support ticket.",
	"input_schema": TicketTriage.model_json_schema(),
}


class TriageError(RuntimeError):
	"""Raised when the model's reply can't be turned into a valid TicketTriage, even after a
	retry. Loud and specific beats a silent, wrong guess."""


def _client() -> Anthropic:
	return Anthropic()


def _request_triage(ticket_text: str) -> TicketTriage:
	response = _client().messages.create(
		model = MODEL,
		max_tokens = 1024,
		system = "You triage support tickets by calling triage_ticket exactly once.",
		messages = [{"role": "user", "content": ticket_text}],
		tools = [TRIAGE_TOOL],
		tool_choice = {"type": "tool", "name": "triage_ticket"},
	)
	tool_use_blocks = [block for block in response.content if block.type == "tool_use"]
	if not tool_use_blocks:
		raise TriageError("Model did not call triage_ticket.")
	return TicketTriage.model_validate(tool_use_blocks[0].input)


def triage(ticket_text: str) -> TicketTriage:

	try:
		return _request_triage(ticket_text)
	except Exception:
		try:
			return _request_triage(ticket_text)
		except Exception as exc:
			raise TriageError(f"triage() failed twice for ticket: {ticket_text!r}") from exc
