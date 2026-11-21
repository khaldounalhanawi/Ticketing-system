// Handles the form submit: build the ticket, save it on the server, show the result.

import { buildTicket } from "../ticket-builder/index.js";
import { MESSAGES } from "../config/settings.js";
import { readFormInput } from "./form-reader.js";
import { clearFieldErrors, showFieldErrors, showStatus } from "./form-view.js";
import { saveTicket } from "./ticket-api.js";

function setBusy(ui, isBusy) {
  ui.submitButton.disabled = isBusy;
  ui.submitButton.textContent = isBusy ? MESSAGES.submitBusy : MESSAGES.submitIdle;
}

export async function handleSubmit(ui) {
  clearFieldErrors(ui.form);
  const { ticket, errors } = buildTicket(readFormInput(ui.form));
  if (errors) {
    showFieldErrors(ui.form, errors);
    showStatus(ui.status, errors.id || "", "error");
    return;
  }

  setBusy(ui, true);
  const { ticketId, error } = await saveTicket(ticket);
  setBusy(ui, false);
  if (error) {
    showStatus(ui.status, error, "error");
    return;
  }

  ui.form.reset();
  showStatus(ui.status, `${MESSAGES.ticketSaved} ${ticketId}`, "success");
}
