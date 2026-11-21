// Entry point for submission_form.html: finds the page elements and wires events.

import { TICKET_RULES } from "./config/settings.js";
import { updateCharCounter } from "./form/form-view.js";
import { handleSubmit } from "./form/submit-handler.js";

function findElements() {
  const ui = {
    form: document.getElementById("ticket-form"),
    submitButton: document.getElementById("submit-button"),
    textarea: document.getElementById("text"),
    counter: document.getElementById("char-counter"),
    status: document.getElementById("status"),
  };
  const allFound = Object.values(ui).every((element) => element !== null);
  return allFound ? ui : null;
}

function bindEvents(ui) {
  const refreshCounter = () => updateCharCounter(ui.textarea, ui.counter, TICKET_RULES.textMaxLength);
  ui.form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (ui.submitButton.disabled) {
      return;
    }
    await handleSubmit(ui);
    refreshCounter();
  });
  ui.textarea.addEventListener("input", refreshCounter);
  refreshCounter();
}

function start() {
  const ui = findElements();
  if (ui === null) {
    console.error("Ticket form: required page elements are missing.");
    return;
  }
  bindEvents(ui);
}

start();
