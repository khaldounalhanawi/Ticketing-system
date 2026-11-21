import json
from rich import print

WATCHED_FIELDS = ("customer", "triage", "notes")

def _print_fields(indent: str, data: dict, fields=WATCHED_FIELDS) -> None:
	for field in fields:
		if field in data:
			print(f"{indent}{field}: {json.dumps(data[field])}")


def print_ticket(ticket: dict) -> None:
	print(f"=== {ticket['id']}: {ticket['text'][:60]}... ===")


def print_updates(chunk: dict) -> None:
	for node_name, update in chunk.items():
		if node_name == "__interrupt__":
			print(update[0].value)
		else:
			print(f"  node {node_name!r} returned:")
			_print_fields("      ", update)


def print_custom(chunk: dict) -> None:
	print(24 * "+")
	print(f"[cyan]{chunk['status']}[/cyan]")
	print(24 * "=")
