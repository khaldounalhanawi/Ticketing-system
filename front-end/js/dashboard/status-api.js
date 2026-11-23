// Fetches every ticket with its status, plus the review form's category/priority options.
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
      return { board: null, error: DASHBOARD_MESSAGES.loadFailed };
    }
    const body = await response.json();
    const options = body.options && typeof body.options === "object" ? body.options : {};
    return Array.isArray(body.tickets)
      ? { board: { tickets: body.tickets, options }, error: null }
      : { board: null, error: DASHBOARD_MESSAGES.loadFailed };
  } catch (error) {
    return { board: null, error: MESSAGES.serverUnreachable };
  } finally {
    clearTimeout(timer);
  }
}
