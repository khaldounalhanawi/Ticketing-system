COMPOSE    = docker compose -f otel_collector/compose.yaml
SERVER_PID = data/server.pid
SERVER_LOG = data/server.log

.PHONY: up down graph

up:		## start the containers and the ticket server, both in the background
	$(COMPOSE) up -d
	@mkdir -p data
	@if [ -f $(SERVER_PID) ] && kill -0 $$(cat $(SERVER_PID)) 2>/dev/null; then \
		echo "Server already running (pid $$(cat $(SERVER_PID)))."; \
	else \
		nohup uv run python3 -u -m ticket_server > $(SERVER_LOG) 2>&1 & echo $$! > $(SERVER_PID); \
		sleep 2; \
		if kill -0 $$(cat $(SERVER_PID)) 2>/dev/null; then \
			echo "Server running: http://127.0.0.1:8000/dashboard.html  (log: $(SERVER_LOG))"; \
		else \
			echo "Server failed to start:"; cat $(SERVER_LOG); rm -f $(SERVER_PID); exit 1; \
		fi; \
	fi

down:	## stop the ticket server and the containers
	@if [ -f $(SERVER_PID) ] && kill $$(cat $(SERVER_PID)) 2>/dev/null; then \
		echo "Server stopped."; \
	else \
		echo "Server was not running."; \
	fi
	@rm -f $(SERVER_PID)
	$(COMPOSE) down

graph:	## run new tickets through the triage graph
	uv run python3 run_graph.py
