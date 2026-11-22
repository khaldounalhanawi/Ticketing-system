"""Tests for the ticket status export (ticket_status.json) and the dashboard's merged view.

The snapshot test runs the real graph against a real SQLite file, with the Anthropic SDK
patched, so it checks the exact object run_graph.py hands to status_from_snapshot.
"""
import json
from types import SimpleNamespace
from unittest.mock import patch

from scoutbot.graph import build_ticket_graph, initial_state, sqlite_checkpointer, thread_config
from ticket_server.status_store import (
    failed_record,
    load_statuses,
    save_status,
    status_from_snapshot,
)
from ticket_server.status_view import merged_ticket_statuses

HIGH = {"category": "billing", "priority": "high", "suggested_owner": "billing-team"}
LOW = {"category": "technical", "priority": "low", "suggested_owner": "support-team"}


def _fake_response(input_dict):
    block = SimpleNamespace(type="tool_use", name="triage_ticket", input=input_dict, id="tu_1")
    return SimpleNamespace(content=[block], stop_reason="tool_use")


def _run(tmp_path, triage_result, ticket_id):
    graph = build_ticket_graph(sqlite_checkpointer(tmp_path / "cp.db"))
    with patch("scoutbot.core._client") as client:
        client.return_value.messages.create.return_value = _fake_response(triage_result)
        graph.invoke(initial_state("Charged twice!", "1001", ticket_id), thread_config(ticket_id))
    return graph.get_state(thread_config(ticket_id))


def test_escalated_ticket_is_pending_human(tmp_path):
    record = status_from_snapshot(_run(tmp_path, HIGH, "T-1"))
    assert record["status"] == "pending_human"
    assert record["triage"]["priority"] == "high"
    assert record["resolution"] == {}


def test_low_priority_ticket_is_resolved(tmp_path):
    record = status_from_snapshot(_run(tmp_path, LOW, "T-2"))
    assert record["status"] == "resolved"
    assert record["resolution"]["path"] == "auto_resolved"


def test_save_status_round_trips_and_keeps_other_records(tmp_path):
    path = tmp_path / "status.json"
    assert save_status(path, "T-1", failed_record({"text": "x"}, "boom")) is None
    assert save_status(path, "T-2", {"status": "resolved"}) is None
    statuses, error = load_statuses(path)
    assert error is None
    assert statuses["T-1"]["status"] == "failed"
    assert statuses["T-2"]["status"] == "resolved"
    assert "updated_at" in statuses["T-2"]


def test_damaged_status_file_is_not_overwritten(tmp_path):
    path = tmp_path / "status.json"
    path.write_text("not json")
    assert save_status(path, "T-1", {"status": "resolved"}) is not None
    assert path.read_text() == "not json"


def test_merged_view_marks_untriaged_tickets_as_new(tmp_path):
    tickets = tmp_path / "tickets.json"
    statuses = tmp_path / "status.json"
    tickets.write_text(json.dumps([
        {"id": "T-1", "customer_id": "1", "text": "a"},
        {"id": "T-2", "customer_id": "2", "text": "b"},
    ]))
    statuses.write_text(json.dumps({"T-2": {"status": "resolved"}, "S-9": {"status": "failed"}}))
    merged, error = merged_ticket_statuses(tickets, statuses)
    assert error is None
    by_id = {t["id"]: t["status"] for t in merged}
    assert by_id == {"T-1": "new", "T-2": "resolved", "S-9": "failed"}
