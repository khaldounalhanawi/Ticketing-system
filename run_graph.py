import json
from dotenv import load_dotenv
from scoutbot import build_ticket_graph, print_ticket,stream_graph
import genai_otel
from config import TICKETS_PATH, CHECKPOINTER

load_dotenv()

genai_otel.instrument(
	service_name="Awesome_graph",
	enable_prompt_injection_detection=True,
)

def main():
	''' Build ticket graph and stream it for each ticket. '''
	graph	= build_ticket_graph (CHECKPOINTER)
	tickets	= json.loads (TICKETS_PATH.read_text())

	for ticket in tickets[2:4]:
		print_ticket (ticket)
		stream_graph (graph, ticket)
		print()


if __name__ == "__main__":
	main()