import json
from dotenv import load_dotenv
from scoutbot import build_ticket_graph, print_ticket, stream_graph, thread_config
from scoutbot.core import TriageError
import genai_otel
from config import TICKETS_PATH, STATUS_PATH, CHECKPOINTER
from ticket_server.status_store import failed_record, load_statuses, save_status, status_from_snapshot

load_dotenv()

genai_otel.instrument(
	service_name="Awesome_graph",
	enable_prompt_injection_detection=True,
)

def main():
	''' Build ticket graph, stream each new ticket through it and save its status. '''
	graph		= build_ticket_graph (CHECKPOINTER)
	tickets		= json.loads (TICKETS_PATH.read_text())
	done, error	= load_statuses (STATUS_PATH)
	if error:
		print(error)
		return

	for ticket in tickets:
		if ticket["id"] in done:
			print(f"skipping {ticket['id']}: already processed")
			continue
		print_ticket (ticket)
		try:
			stream_graph (graph, ticket)
			record = status_from_snapshot (graph.get_state (thread_config (ticket["id"])))
		except TriageError as exc:
			record = failed_record (ticket, str(exc))
		save_status (STATUS_PATH, ticket["id"], record)
		print()


if __name__ == "__main__":
	main()
