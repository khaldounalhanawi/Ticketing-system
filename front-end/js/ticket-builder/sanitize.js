// Turns raw user input into clean, single-line strings.
// Never throws: anything that is not a string becomes "".

const CONTROL_CHARS = /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g;
const INVISIBLE_CHARS = /[​-‏‪-‮⁠-⁩﻿]/g;
const ANY_WHITESPACE = /\s+/g;

export function toSafeString(value) {
  if (typeof value !== "string") {
    return "";
  }
  return value.normalize("NFC");
}

export function cleanText(value) {
  return toSafeString(value)
    .replace(CONTROL_CHARS, "")
    .replace(INVISIBLE_CHARS, "")
    .replace(ANY_WHITESPACE, " ")
    .trim();
}

export function cleanCustomerId(value) {
  return cleanText(value).replace(ANY_WHITESPACE, "");
}
