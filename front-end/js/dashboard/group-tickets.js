// Sorts tickets into the dashboard columns defined in DASHBOARD_GROUPS.

import { DASHBOARD_GROUPS } from "../config/settings.js";

function isValidTicket(ticket) {
  return ticket !== null && typeof ticket === "object" && typeof ticket.id === "string";
}

function newestFirst(a, b) {
  return String(b.updated_at || b.id).localeCompare(String(a.updated_at || a.id));
}

// Returns { unresolved: [...], pending: [...], resolved: [...] }.
// Tickets with an unknown status land in the first group, so nothing silently disappears.
export function groupTickets(tickets) {
  const groups = Object.fromEntries(DASHBOARD_GROUPS.map((group) => [group.key, []]));
  const fallbackKey = DASHBOARD_GROUPS[0].key;
  tickets.filter(isValidTicket).forEach((ticket) => {
    const match = DASHBOARD_GROUPS.find((group) => group.statuses.includes(ticket.status));
    groups[match ? match.key : fallbackKey].push(ticket);
  });
  Object.values(groups).forEach((list) => list.sort(newestFirst));
  return groups;
}
