// Entry point for dashboard.html: loads ticket statuses, fills the three columns,
// and runs the review dialog for tickets that are waiting on a human.

import { DASHBOARD_GROUPS, REVIEW_MESSAGES } from "./config/settings.js";
import { fetchStatuses } from "./dashboard/status-api.js";
import { groupTickets } from "./dashboard/group-tickets.js";
import { renderGroup, setBusy, showStatus, showUpdatedTime } from "./dashboard/dashboard-view.js";
import { resolveTicket } from "./dashboard/resolve-api.js";
import { openReview, readDecision, setReviewBusy, showReviewError } from "./dashboard/review-form.js";

// What the last load returned: tickets by ID (for the review dialog) and the form's options.
const state = { tickets: new Map(), options: {} };

function findElements() {
  const columns = {};
  DASHBOARD_GROUPS.forEach((group) => {
    columns[group.key] = document.querySelector(`[data-group="${group.key}"]`);
  });
  const review = {
    dialog: document.getElementById("review-dialog"), form: document.getElementById("review-form"),
    title: document.getElementById("review-title"), text: document.getElementById("review-text"),
    error: document.getElementById("review-error"), submit: document.getElementById("review-submit"),
    cancel: document.getElementById("review-cancel"),
  };
  const ui = {
    columns, review,
    board: document.querySelector(".board"),
    refreshButton: document.getElementById("refresh-button"),
    status: document.getElementById("status"),
  };
  const allFound = [ui.board, ui.refreshButton, ui.status, ...Object.values(columns), ...Object.values(review)]
    .every(Boolean);
  return allFound ? ui : null;
}

async function loadDashboard(ui) {
  setBusy(ui.refreshButton, true);
  const { board, error } = await fetchStatuses();
  setBusy(ui.refreshButton, false);
  if (error) {
    showStatus(ui.status, error, "error");
    return;
  }
  state.tickets = new Map(board.tickets.map((ticket) => [ticket.id, ticket]));
  state.options = board.options;
  const groups = groupTickets(board.tickets);
  DASHBOARD_GROUPS.forEach((group) => renderGroup(ui.columns[group.key], groups[group.key]));
  showUpdatedTime(ui.status);
}

function handleReviewClick(ui, event) {
  const button = event.target.closest("[data-review]");
  const ticket = button ? state.tickets.get(button.dataset.review) : undefined;
  if (ticket) {
    openReview(ui.review, ticket, state.options);
  }
}

async function handleReviewSubmit(ui, event) {
  event.preventDefault();
  const decision = readDecision(ui.review.form);
  if (!decision.decision) {
    showReviewError(ui.review.error, REVIEW_MESSAGES.decisionMissing);
    return;
  }
  const ticketId = ui.review.form.dataset.ticketId;
  setReviewBusy(ui.review.submit, true);
  const { error } = await resolveTicket(ticketId, decision);
  setReviewBusy(ui.review.submit, false);
  if (error) {
    showReviewError(ui.review.error, error);
    return;
  }
  ui.review.dialog.close();
  await loadDashboard(ui);
  showStatus(ui.status, `${REVIEW_MESSAGES.saved} ${ticketId}.`, "success");
}

function start() {
  const ui = findElements();
  if (ui === null) {
    console.error("Dashboard: required page elements are missing.");
    return;
  }
  ui.refreshButton.addEventListener("click", () => {
    if (!ui.refreshButton.disabled) {
      loadDashboard(ui);
    }
  });
  ui.board.addEventListener("click", (event) => handleReviewClick(ui, event));
  ui.review.form.addEventListener("submit", (event) => {
    if (!ui.review.submit.disabled) {
      handleReviewSubmit(ui, event);
    } else {
      event.preventDefault();
    }
  });
  ui.review.cancel.addEventListener("click", () => ui.review.dialog.close());
  loadDashboard(ui);
}

start();
