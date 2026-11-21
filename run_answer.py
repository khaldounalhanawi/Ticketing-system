import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from scoutbot import build_ticket_graph
from rich import print
import sys

load_dotenv()
DB_PATH = Path(__file__).parent / "checkpoints.db"

checkpointer = SqliteSaver(sqlite3.connect(str(DB_PATH), check_same_thread=False))
graph = build_ticket_graph(checkpointer)

config = {"configurable": {"thread_id": "T-1001"}}

snapshot = graph.get_state(config)
if not snapshot.next:
	print ('No pending tickets')
	sys.exit(0)

print(f"[cyan]waiting at: {snapshot.next}[/cyan]")
print(f"[red]question: {snapshot.interrupts[0].value}[/red]")

answer = input("Your decision:")
final = graph.invoke(Command(resume=answer), config)

print(f"[green]resolution: {final["resolution"]}[/green]")
