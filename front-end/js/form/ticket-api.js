// Sends a ticket to the server, which appends it to tickets.json.
// Write-only: the server replies with the new ticket number and nothing else.

import { API_SETTINGS, MESSAGES } from "../config/settings.js";

async function readErrorMessage(response) {
  try {
    const body = await response.json();
    return typeof body.error === "string" ? body.error : MESSAGES.saveFailed;
  } catch (error) {
    return MESSAGES.saveFailed;
  }
}

export async function saveTicket(ticket) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), API_SETTINGS.timeoutMs);
  try {
    const response = await fetch(API_SETTINGS.ticketsEndpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ customer_id: ticket.customer_id, text: ticket.text }),
      signal: controller.signal,
    });
    if (!response.ok) {
      return { ticketId: null, error: await readErrorMessage(response) };
    }
    const body = await response.json();
    return typeof body.id === "string"
      ? { ticketId: body.id, error: null }
      : { ticketId: null, error: MESSAGES.saveFailed };
  } catch (error) {
    return { ticketId: null, error: MESSAGES.serverUnreachable };
  } finally {
    clearTimeout(timer);
  }
}
