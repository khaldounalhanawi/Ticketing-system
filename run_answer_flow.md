# How `run_answer.py` relates to the HTML

**Short answer: the HTML never calls `run_answer.py`.** The dashboard and `run_answer.py` are two separate ways to answer an escalated ticket. Both end in the same function, `resolve_ticket()` in `src/scoutbot/tickets/resolve.py`.

```
dashboard.html (browser)                     terminal
        │                                        │
        ▼                                        ▼
  ticket_server (HTTP)                     run_answer.py
        │                                        │
        └──────────────►  resolve_ticket()  ◄────┘
                                │
                                ▼
              resumes the paused graph in data/checkpoints.db
              writes the new status to data/ticket_status.json
```

## Path 1: from the HTML (dashboard)

| # | Domain | Function | File |
|---|--------|----------|------|
| 1 | HTML | User clicks **Review** on a `pending_human` card, then **Save decision** | `front-end/dashboard.html` |
| 2 | JS | `handleReviewClick()` → `openReview()` fills the dialog | `front-end/js/dashboard-app.js`, `dashboard/review-form.js` |
| 3 | JS | `handleReviewSubmit()` → `readDecision()` | `front-end/js/dashboard-app.js` |
| 4 | JS | `resolveTicket()` sends `POST /api/tickets/<id>/resolve` | `front-end/js/dashboard/resolve-api.js` |
| 5 | Server | `TicketRequestHandler.do_POST()` matches the URL | `ticket_server/request_handler.py` |
| 6 | Server | `handle_resolve_post()` → `_read_body()` → `validate_decision()` | `ticket_server/routes.py`, `validation.py` |
| 7 | Server | `shared_graph()` builds the graph once, on `data/checkpoints.db` | `ticket_server/shared_graph.py` |
| 8 | Core | **`resolve_ticket(graph, ticket_id, decision, STATUS_FILE)`** | `src/scoutbot/tickets/resolve.py` |

## Path 2: from the terminal (`python run_answer.py`)

| # | Function | What it does |
|---|----------|--------------|
| 1 | `main()` | `load_statuses()` reads `ticket_status.json` and keeps the `pending_human` tickets |
| 2 | `build_ticket_graph(CHECKPOINTER)` | Builds its own graph on the same `data/checkpoints.db` (from `config.py`) |
| 3 | `answer_ticket()` | `graph.get_state()` loads the paused ticket and prints the AI triage |
| 4 | `ask_decision()` → `ask_choice()` | Asks for the decision, team, category and priority with `input()` |
| 5 | **`resolve_ticket(graph, ticket_id, decision, STATUS_PATH)`** | Same function the dashboard uses |

## What `resolve_ticket()` does (shared by both)

1. `graph.get_state(thread_config(ticket_id))`. If there's no state, it returns `UNKNOWN_TICKET`. If the run isn't paused anymore, it returns `ALREADY_ANSWERED`.
2. `graph.invoke(Command(resume=decision))` resumes `escalate_node()` after its `interrupt()`. `human_resolution()` merges the human's fields over the AI's triage.
3. `status_from_snapshot()` → `save_status()` writes `resolved` to `data/ticket_status.json`.

## Why both paths work on the same ticket

- `run_graph.py` pauses high-priority tickets with `interrupt()` and saves the run in `data/checkpoints.db`. The ticket ID is used as the LangGraph thread ID.
- The server and `run_answer.py` both open that same database and look the ticket up by its ID, so either one can resume it.
- A ticket answered in one place shows up as `ALREADY_ANSWERED` in the other.
