from dotenv import load_dotenv
from langgraph.types import Command
from rich import print
from scoutbot import Priority, build_ticket_graph, thread_config
from ticket_server.status_store import PENDING_HUMAN, load_statuses, save_status, status_from_snapshot
from config import STATUS_PATH, CHECKPOINTER

load_dotenv()
PRIORITIES = [p.value for p in Priority]

def ask_priority(suggested: str) -> str:
	''' Ask until the answer is a valid priority. Blank keeps the AI's suggestion. '''
	while True:
		answer = input(f"Priority {PRIORITIES} [{suggested}]: ").strip().lower()
		if answer == "" or answer in PRIORITIES:
			return answer
		print(f"[red]Type one of {PRIORITIES}, or press Enter to keep {suggested}.[/red]")


def ask_decision(triage: dict) -> dict | None:
	''' Collect the human's decision, or None to skip. Blank owner/priority keeps the AI's values. '''
	text = input("Decision (Enter to skip): ").strip()      # e.g. "refund approved"
	if not text:
		return None
	return {
		"decision": text,
		"owner": input(f"Assign to team [{triage.get('suggested_owner', '')}]: ").strip(),
		"priority": ask_priority(triage.get("priority", "")),
	}


def answer_ticket(graph, ticket_id: str) -> None:
	''' Show one paused ticket, resume it with the human's decision and save its new status. '''
	config		= thread_config (ticket_id)
	snapshot	= graph.get_state (config)
	if not snapshot.next:
		# The status file was out of date (e.g. answered elsewhere): copy the graph's real state over.
		save_status (STATUS_PATH, ticket_id, status_from_snapshot (snapshot))
		print(f"[yellow]{ticket_id} was already answered; status file updated.[/yellow]")
		return

	triage = snapshot.values.get("triage", {})   # from the state, so tickets paused earlier work too
	print(f"\n[bold cyan]{ticket_id}[/bold cyan]: {snapshot.values.get('ticket_text', '')}")
	print(f"[red]AI triage: {triage}[/red]")

	decision = ask_decision (triage)
	if decision is None:
		print("[yellow]skipped[/yellow]")
		return
	graph.invoke (Command (resume=decision), config)
	record = status_from_snapshot (graph.get_state (config))
	save_status (STATUS_PATH, ticket_id, record)
	print(f"[green]resolution: {record['resolution']}[/green]")


def main():
	''' Load every pending_human ticket and answer them one by one. '''
	statuses, error = load_statuses (STATUS_PATH)
	if error:
		print(f"[red]{error}[/red]")
		return
	pending = [ticket_id for ticket_id, record in statuses.items() if record.get("status") == PENDING_HUMAN]
	if not pending:
		print("No pending tickets.")
		return

	print(f"{len(pending)} ticket(s) waiting for a human: {', '.join(pending)}")
	graph = build_ticket_graph (CHECKPOINTER)
	try:
		for ticket_id in pending:
			answer_ticket (graph, ticket_id)
	except KeyboardInterrupt:
		print("\nStopped. Answered tickets are saved; the rest stay pending.")


if __name__ == "__main__":
	main()
