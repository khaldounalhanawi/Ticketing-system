// Checks cleaned input against the ticket rules.
// Returns error messages keyed by field name, never throws.

import { MESSAGES } from "../config/settings.js";

// The customer ID is optional: an empty string is valid (customer has no ID).
function checkCustomerId(customerId, rules) {
  if (customerId.length === 0) {
    return null;
  }
  if (customerId.length > rules.customerIdMaxLength) {
    return MESSAGES.customerIdTooLong;
  }
  if (!rules.customerIdPattern.test(customerId)) {
    return MESSAGES.customerIdInvalid;
  }
  return null;
}

function checkText(text, rules) {
  if (text.length === 0) {
    return MESSAGES.textMissing;
  }
  if (text.length < rules.textMinLength) {
    return MESSAGES.textTooShort;
  }
  if (text.length > rules.textMaxLength) {
    return MESSAGES.textTooLong;
  }
  return null;
}

export function validateTicketInput(cleanedInput, rules) {
  const errors = {};
  const customerIdError = checkCustomerId(cleanedInput.customerId, rules);
  const textError = checkText(cleanedInput.text, rules);

  if (customerIdError) {
    errors.customerId = customerIdError;
  }
  if (textError) {
    errors.text = textError;
  }
  const isValid = Object.keys(errors).length === 0;
  return { isValid, errors };
}
