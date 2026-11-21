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
