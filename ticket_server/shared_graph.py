"""The one ticket graph the server keeps alive for all requests, built on first use."""

import threading

from langgraph.graph.state import CompiledStateGraph

from scoutbot import build_ticket_graph, sqlite_checkpointer
from ticket_server import settings

_graph_lock = threading.Lock()      # builds the server's graph only once
_graph: CompiledStateGraph | None = None


def shared_graph() -> CompiledStateGraph:
	"""Return the server's ticket graph, built on first use and backed by data/checkpoints.db."""
	global _graph
	with _graph_lock:
		if _graph is None:
			_graph = build_ticket_graph(sqlite_checkpointer(settings.CHECKPOINTS_FILE))
	return _graph
