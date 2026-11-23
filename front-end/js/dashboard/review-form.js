// The review dialog: shows one escalated ticket, pre-filled with the AI's triage,
// and reads the human's decision back out. Uses textContent only, never innerHTML.

import { REVIEW_MESSAGES } from "../config/settings.js";

function fillSelect(select, options, selected) {
  const choices = options.map((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    option.selected = value === selected;
    return option;
  });
  select.replaceChildren(...choices);
}

export function openReview(review, ticket, options) {
  const triage = ticket.triage && typeof ticket.triage === "object" ? ticket.triage : {};
  review.title.textContent = `Review ${ticket.id}`;
  review.text.textContent = ticket.text || "";
  review.form.reset();
  review.form.elements.namedItem("owner").value = triage.suggested_owner || "";
  fillSelect(review.form.elements.namedItem("category"), options.categories || [], triage.category);
  fillSelect(review.form.elements.namedItem("priority"), options.priorities || [], triage.priority);
  review.form.dataset.ticketId = ticket.id;
  showReviewError(review.error, "");
  setReviewBusy(review.submit, false);
  review.dialog.showModal();
}

export function readDecision(form) {
  const value = (name) => String(form.elements.namedItem(name).value || "").trim();
  return {
    decision: value("decision"),
    owner: value("owner"),
    category: value("category"),
    priority: value("priority"),
  };
}

export function setReviewBusy(button, busy) {
  button.disabled = busy;
  button.textContent = busy ? REVIEW_MESSAGES.submitBusy : REVIEW_MESSAGES.submitIdle;
}

export function showReviewError(element, message) {
  element.textContent = message;
}
