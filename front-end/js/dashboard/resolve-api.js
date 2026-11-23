// Sends a human's review decision for one escalated ticket. The server resumes the
// paused graph run and replies with the ticket's updated record.

import { API_SETTINGS, MESSAGES, REVIEW_MESSAGES } from "../config/settings.js";

async function readErrorMessage(response) {
  try {
    const body = await response.json();
    return typeof body.error === "string" ? body.error : REVIEW_MESSAGES.saveFailed;
  } catch (error) {
    return REVIEW_MESSAGES.saveFailed;
  }
}

export async function resolveTicket(ticketId, decision) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), API_SETTINGS.timeoutMs);
  const url = API_SETTINGS.resolveEndpoint.replace("{id}", encodeURIComponent(ticketId));
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(decision),
      signal: controller.signal,
    });
    if (!response.ok) {
      return { ticket: null, error: await readErrorMessage(response) };
    }
    const body = await response.json();
    return { ticket: body.ticket || null, error: null };
  } catch (error) {
    return { ticket: null, error: MESSAGES.serverUnreachable };
  } finally {
    clearTimeout(timer);
  }
}
