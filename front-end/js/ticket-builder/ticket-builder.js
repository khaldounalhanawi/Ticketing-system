// Core logic: raw input in, ticket object out.
// Has no knowledge of HTML, the DOM or any page. Safe to reuse anywhere.

import { TICKET_RULES, MESSAGES } from "../config/settings.js";
import { cleanText, cleanCustomerId } from "./sanitize.js";
import { validateTicketInput } from "./validate.js";
import { generateTicketId } from "./id-generator.js";

function cleanInput(rawInput) {
  const source = rawInput !== null && typeof rawInput === "object" ? rawInput : {};
  return {
    customerId: cleanCustomerId(source.customerId),
    text: cleanText(source.text),
  };
}

function createId(options, rules) {
  try {
    const makeId = typeof options.idGenerator === "function"
      ? options.idGenerator
      : () => generateTicketId(rules);
    const id = cleanText(String(makeId()));
    return id.length > 0 ? id : null;
  } catch (error) {
    return null;
  }
}

export function buildTicket(rawInput, options = {}) {
  const safeOptions = options !== null && typeof options === "object" ? options : {};
  const rules = { ...TICKET_RULES, ...(safeOptions.rules || {}) };
  const cleaned = cleanInput(rawInput);
  const result = validateTicketInput(cleaned, rules);

  if (!result.isValid) {
    return { ticket: null, errors: result.errors };
  }
  const id = createId(safeOptions, rules);
  if (id === null) {
    return { ticket: null, errors: { id: MESSAGES.idFailed } };
  }
  const ticket = Object.freeze({ id, customer_id: cleaned.customerId, text: cleaned.text });
  return { ticket, errors: null };
}
