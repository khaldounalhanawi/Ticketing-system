// Fetches every ticket with its status from the server (tickets.json + ticket_status.json).
// Read-only: this module never changes anything on the server.

import { API_SETTINGS, DASHBOARD_MESSAGES, MESSAGES } from "../config/settings.js";

export async function fetchStatuses() {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), API_SETTINGS.timeoutMs);
  try {
    const response = await fetch(API_SETTINGS.statusEndpoint, {
      headers: { Accept: "application/json" },
      signal: controller.signal,
    });
    if (!response.ok) {
      return { tickets: null, error: DASHBOARD_MESSAGES.loadFailed };
    }
    const body = await response.json();
    return Array.isArray(body.tickets)
      ? { tickets: body.tickets, error: null }
      : { tickets: null, error: DASHBOARD_MESSAGES.loadFailed };
  } catch (error) {
    return { tickets: null, error: MESSAGES.serverUnreachable };
  } finally {
    clearTimeout(timer);
  }
}
