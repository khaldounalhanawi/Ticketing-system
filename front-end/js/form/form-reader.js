// Reads the raw values out of the submission form.
// Only collects values; cleaning and validation happen in the Ticket Builder.

function readField(form, fieldName) {
  const field = form.elements.namedItem(fieldName);
  if (!field || typeof field.value !== "string") {
    return "";
  }
  return field.value;
}

export function readFormInput(form) {
  return {
    customerId: readField(form, "customerId"),
    text: readField(form, "text"),
  };
}
