// Updates what the user sees. Uses textContent only, never innerHTML,
// so user input can never be interpreted as HTML or script.

export function clearFieldErrors(form) {
  form.querySelectorAll("[data-error-for]").forEach((element) => {
    element.textContent = "";
  });
  form.querySelectorAll("[aria-invalid]").forEach((element) => {
    element.removeAttribute("aria-invalid");
  });
}

export function showFieldErrors(form, errors) {
  Object.keys(errors).forEach((fieldName) => {
    const message = form.querySelector(`[data-error-for="${CSS.escape(fieldName)}"]`);
    const field = form.elements.namedItem(fieldName);
    if (message) {
      message.textContent = errors[fieldName];
    }
    if (field && typeof field.setAttribute === "function") {
      field.setAttribute("aria-invalid", "true");
    }
  });
}

export function showStatus(element, message, kind) {
  element.textContent = message;
  element.dataset.kind = kind;
}

export function updateCharCounter(textarea, counter, maxLength) {
  const length = textarea.value.length;
  counter.textContent = `${length} / ${maxLength}`;
  counter.dataset.over = String(length > maxLength);
}
