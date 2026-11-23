// Builds one ticket card. Uses textContent only, never innerHTML,
// so ticket text can never be interpreted as HTML or script.

import { DASHBOARD_MESSAGES, REVIEW_MESSAGES, STATUS_LABELS } from "../config/settings.js";

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  if (text !== undefined && text !== null && text !== "") {
    node.textContent = String(text);
  }
  return node;
}

function cardHeader(ticket) {
  const header = element("div", "ticket-head");
  header.append(element("span", "ticket-id", ticket.id));
  const badge = element("span", "badge", STATUS_LABELS[ticket.status] || ticket.status);
  badge.dataset.status = String(ticket.status);
  header.append(badge);
  return header;
}

function triageChips(triage, resolution) {
  const chips = element("div", "chips");
  const values = [
    ["category", triage.category],
    ["priority", triage.priority],
    ["owner", triage.suggested_owner || resolution.owner],
  ];
  values.filter(([, value]) => value).forEach(([kind, value]) => {
    const chip = element("span", "chip", value);
    chip.dataset.kind = kind;
    chip.dataset.value = String(value);
    chips.append(chip);
  });
  return chips;
}

function notesBlock(notes) {
  const details = element("details", "notes");
  details.append(element("summary", null, `Notes (${notes.length})`));
  const list = element("ul");
  notes.forEach((note) => list.append(element("li", null, note)));
  details.append(list);
  return details;
}

export function createTicketCard(ticket) {
  const triage = ticket.triage && typeof ticket.triage === "object" ? ticket.triage : {};
  const resolution = ticket.resolution && typeof ticket.resolution === "object" ? ticket.resolution : {};
  const notes = Array.isArray(ticket.notes) ? ticket.notes : [];
  const card = element("article", "ticket");
  card.append(cardHeader(ticket));
  card.append(element("p", "ticket-customer", ticket.customer_id
    ? `Customer ${ticket.customer_id}` : DASHBOARD_MESSAGES.noCustomer));
  card.append(element("p", "ticket-text", ticket.text));
  card.append(triageChips(triage, resolution));
  if (resolution.path === "human_resolved" && resolution.decision) {
    card.append(element("p", "ticket-decision", `Human decision: ${resolution.decision}`));
  }
  if (notes.length > 0) {
    card.append(notesBlock(notes));
  }
  if (ticket.status === "pending_human") {
    const review = element("button", "button button-small", REVIEW_MESSAGES.button);
    review.type = "button";
    review.dataset.review = ticket.id;   // dashboard-app.js listens for clicks on [data-review]
    card.append(review);
  }
  return card;
}
