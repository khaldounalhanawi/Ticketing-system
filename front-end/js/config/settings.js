// All tunable settings for the front-end live in this one file.
// Change values here instead of editing the modules that use them.

export const TICKET_RULES = Object.freeze({
  idPrefix: "T-",
  idDigits: 6,
  textMinLength: 10,
  textMaxLength: 2000,
  customerIdMaxLength: 20,
  customerIdPattern: /^[A-Za-z0-9-]+$/,
});

export const API_SETTINGS = Object.freeze({
  ticketsEndpoint: "/api/tickets",
  statusEndpoint: "/api/tickets/status",
  resolveEndpoint: "/api/tickets/{id}/resolve",
  timeoutMs: 8000,
});

export const MESSAGES = Object.freeze({
  customerIdTooLong: "Customer ID is too long.",
  customerIdInvalid: "Customer ID may only contain letters, numbers and dashes.",
  textMissing: "Please describe your issue.",
  textTooShort: "Please add a little more detail.",
  textTooLong: "Your description is too long.",
  idFailed: "Could not create a ticket ID. Please try again.",
  ticketSaved: "Thank you! Your ticket has been submitted. Your ticket number is",
  saveFailed: "The ticket could not be saved. Please try again.",
  serverUnreachable: "Cannot reach the ticket server. Is it running? (python -m ticket_server)",
  submitIdle: "Submit ticket",
  submitBusy: "Sending…",
});

// Dashboard: which ticket statuses belong in which column, and how they are labelled.
export const DASHBOARD_GROUPS = Object.freeze([
  { key: "unresolved", statuses: ["new", "failed"] },
  { key: "pending", statuses: ["pending_human"] },
  { key: "resolved", statuses: ["resolved"] },
]);

export const STATUS_LABELS = Object.freeze({
  new: "Not triaged",
  failed: "Triage failed",
  pending_human: "Needs human",
  resolved: "Resolved",
});

export const DASHBOARD_MESSAGES = Object.freeze({
  loading: "Loading tickets…",
  loadFailed: "Could not load ticket statuses.",
  emptyGroup: "Nothing here.",
  noCustomer: "No customer ID",
  updatedAt: "Last updated",
  refreshIdle: "Refresh",
  refreshBusy: "Loading…",
});

// Review form: rules must match ticket_server/settings.py (DECISION_MAX_LENGTH).
export const REVIEW_RULES = Object.freeze({
  decisionMaxLength: 500,
  ownerMaxLength: 60,
});

export const REVIEW_MESSAGES = Object.freeze({
  button: "Review",
  submitIdle: "Save decision",
  submitBusy: "Saving…",
  decisionMissing: "Please describe your decision.",
  saveFailed: "The decision could not be saved.",
  saved: "Decision saved for",
});
