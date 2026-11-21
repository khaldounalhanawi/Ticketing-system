// Creates ticket IDs such as "T-482913".
// Uses the browser's secure random generator when it is available.

function randomIntBetween(min, max) {
  const range = max - min;
  const cryptoApi = globalThis.crypto;

  if (cryptoApi && typeof cryptoApi.getRandomValues === "function") {
    const buffer = new Uint32Array(1);
    cryptoApi.getRandomValues(buffer);
    return min + (buffer[0] % range);
  }
  return min + Math.floor(Math.random() * range);
}

export function generateTicketId(rules) {
  const smallest = 10 ** (rules.idDigits - 1);
  const largestExclusive = 10 ** rules.idDigits;
  const number = randomIntBetween(smallest, largestExclusive);
  return rules.idPrefix + String(number);
}
