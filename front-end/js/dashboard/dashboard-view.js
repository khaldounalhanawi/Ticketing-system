// Puts grouped tickets on the page and shows loading/error state.

import { DASHBOARD_MESSAGES } from "../config/settings.js";
import { createTicketCard } from "./ticket-card.js";

export function renderGroup(column, tickets) {
  const list = column.querySelector("[data-list]");
  const count = column.querySelector("[data-count]");
  count.textContent = String(tickets.length);
  if (tickets.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = DASHBOARD_MESSAGES.emptyGroup;
    list.replaceChildren(empty);
    return;
  }
  list.replaceChildren(...tickets.map(createTicketCard));
}

export function setBusy(button, busy) {
  button.disabled = busy;
  button.textContent = busy ? DASHBOARD_MESSAGES.refreshBusy : DASHBOARD_MESSAGES.refreshIdle;
}

export function showStatus(element, message, kind) {
  element.textContent = message;
  element.dataset.kind = kind;
}

export function showUpdatedTime(element) {
  const time = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  showStatus(element, `${DASHBOARD_MESSAGES.updatedAt} ${time}`, "info");
}
