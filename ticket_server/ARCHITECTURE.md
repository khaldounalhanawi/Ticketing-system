# ticket_server — Architecture

How the `ticket_server` module fits together. It has three request flows: serving static files, submitting a ticket, and resolving a ticket.

Start it with `python -m ticket_server`.

`ticket_server` is only the **web adapter**. The ticket workflow itself (storage, statuses, resolving) lives in `src/scoutbot/tickets/`, so the CLI scripts (`run_graph.py`, `run_answer.py`) and any future website use the same code without importing the server.

```
            src/scoutbot/tickets   (core: storage, status_store, status_view, resolve, settings)
               ▲                ▲
               │                │
        ticket_server/     run_graph.py / run_answer.py
        (HTTP adapter)     (CLI adapters)
```

## 1. Module map (who imports whom)

```
                         __main__.py   (python -m ticket_server)
                              │  starts ThreadingHTTPServer on 127.0.0.1:8000
                              ▼
                       request_handler.py   TicketRequestHandler
                       • adds security headers   • blocks folder listings
                       • GET  → static file OR status API
                       • POST → ticket API OR resolve API
                       • catches any crash → 500 JSON
                              │
                              ▼
                          routes.py   ◄── http_helpers.py
                          (one function     origin_allowed()
                           per endpoint,    read_json_body()
                           maps core        send_json()
                           problems to
                           HTTP codes)
        ┌─────────────────────┼─────────────────────────┐
        ▼                     ▼                         ▼
  validation.py         shared_graph.py         ── scoutbot.tickets (core) ──
  validate_payload()    shared_graph()          status_view.merged_ticket_statuses()
  validate_decision()   one graph for all       storage.save_ticket()
  clean_text()          requests                resolve.resolve_ticket()  → ResolveProblem
        ▲                     │                 status_store (ticket_status.json)
  scoutbot.schema             ▼
  (Category, Priority)  scoutbot (LangGraph) + checkpoints.db

  settings.py → web settings (port, endpoints, regexes, limits);
                re-exports the data paths from scoutbot.tickets.settings
```

## 2. Request flows

```
Browser / dashboard
   │
   ├─ GET /anything.html ─────────► SimpleHTTPRequestHandler serves front-end/
   │
   ├─ GET /api/tickets/status
   │     └► handle_status_get
   │          └► merged_ticket_statuses
   │               ├ tickets.json        → every ticket starts as "new"
   │               └ ticket_status.json  → replaces it with pending_human / resolved / failed
   │          ◄── 200 {tickets: [...], options: {categories, priorities}}
   │
   ├─ POST /api/tickets           {customer_id, text}
   │     └► handle_ticket_post
   │          ├ _read_body: Origin check (403) → JSON/size checks (415/411/413/400)
   │          ├ validate_payload  (clean text, ID regex, length 10–2000)  → 400
   │          └ save_ticket  (lock → load → next id T-100X → write .tmp → replace)
   │          ◄── 201 {id: "T-1005"}
   │
   └─ POST /api/tickets/<id>/resolve   {decision, owner, category, priority}
         └► handle_resolve_post
              ├ _read_body (same checks)
              ├ validate_decision   → 400
              └ resolve_ticket(shared_graph(), id, decision, STATUS_FILE)   [under _resolve_lock]
                   ├ no saved state      → UNKNOWN_TICKET   → 404
                   ├ not paused anymore  → fix the status record, ALREADY_ANSWERED → 409
                   ├ status file write fails → SAVE_FAILED  → 500
                   └ graph.invoke(Command(resume=decision))
                        → status_from_snapshot → save_status
              ◄── 200 {ticket: {id, status: "resolved", ...}}
```

## 3. Ticket lifecycle (where the status comes from)

```
 form POST         run_graph.py (LangGraph)          dashboard review form / run_answer.py
     │                    │                                  │
     ▼                    ▼                                  ▼
   "new"  ──────►  "pending_human"  ───── resolve ─────►  "resolved"
(tickets.json)    (ticket_status.json,                (ticket_status.json)
                   graph paused in checkpoints.db)
                          │
                          └──► "failed"   (triage crashed: failed_record)
```

## Design points

- `storage.py` and `status_store.py` both write through `write_tickets`: they write a `.tmp` file first, then swap it in. A crash in the middle of a write can't corrupt the file.
- The core never speaks HTTP. `resolve_ticket` returns a `ResolveProblem` enum; `routes.py` turns it into a status code, and `run_answer.py` prints its message.
- `shared_graph.py` builds the server's graph lazily on first use. `status_store.py` imports LangGraph for type hints only.
- Two locks prevent races: `_write_lock` keeps two requests from writing `tickets.json` at once, and `_resolve_lock` stops a double-click from resuming the same ticket twice.
