// Entry point for dashboard.html: loads ticket statuses and fills the three columns.

import { DASHBOARD_GROUPS } from "./config/settings.js";
import { fetchStatuses } from "./dashboard/status-api.js";
import { groupTickets } from "./dashboard/group-tickets.js";
import { renderGroup, setBusy, showStatus, showUpdatedTime } from "./dashboard/dashboard-view.js";

function findElements() {
  const columns = {};
  DASHBOARD_GROUPS.forEach((group) => {
    columns[group.key] = document.querySelector(`[data-group="${group.key}"]`);
  });
  const ui = {
    columns,
    refreshButton: document.getElementById("refresh-button"),
    status: document.getElementById("status"),
  };
  const allFound = ui.refreshButton && ui.status && Object.values(columns).every(Boolean);
  return allFound ? ui : null;
}

async function loadDashboard(ui) {
  setBusy(ui.refreshButton, true);
  const { tickets, error } = await fetchStatuses();
  setBusy(ui.refreshButton, false);
  if (error) {
    showStatus(ui.status, error, "error");
    return;
  }
  const groups = groupTickets(tickets);
  DASHBOARD_GROUPS.forEach((group) => renderGroup(ui.columns[group.key], groups[group.key]));
  showUpdatedTime(ui.status);
}

function start() {
  const ui = findElements();
  if (ui === null) {
    console.error("Dashboard: required page elements are missing.");
    return;
  }
  ui.refreshButton.addEventListener("click", () => {
    if (!ui.refreshButton.disabled) {
      loadDashboard(ui);
    }
  });
  loadDashboard(ui);
}

start();
