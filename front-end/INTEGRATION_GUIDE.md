# Adding the Ticket Builder to Your Website

The Ticket Builder takes a customer ID and a problem description and returns a support ticket in the same format as `sample_tickets.json`:

```json
{ "id": "T-482913", "customer_id": "1001", "text": "I was charged twice this month..." }
```

It never touches HTML or the DOM, so you can use the same code behind any form, framework, or app.

## Folder layout

```
front-end/
├── submission_form.html        Demo page (one possible user of the builder)
├── styles/theme.css            Every color, font, spacing and radius value
└── js/
    ├── config/settings.js      Every rule, limit and user-facing message
    ├── ticket-builder/         ← the reusable part
    │   ├── index.js            Public API: import from here only
    │   ├── ticket-builder.js   buildTicket()
    │   ├── validate.js         Input rules
    │   ├── sanitize.js         Input cleaning
    │   └── id-generator.js     Default ID generator
    ├── form/                   Code for the demo page only
    │   └── ticket-api.js       Sends tickets to the server (POST /api/tickets)
    └── app.js                  Entry point for the demo page

ticket_server/                  Small Python backend (standard library only)
├── settings.py                 Port, file location, limits
├── request_handler.py          Hosts front-end/ and accepts POST /api/tickets
├── validation.py               Checks every ticket again on the server
├── storage.py                  Appends to tickets.json safely
└── http_helpers.py

data/tickets.json               Created on the first submit (data/ is gitignored)
```

**Copy these two folders to reuse the builder:** `js/ticket-builder/` and `js/config/`. Keep them next to each other, because the builder imports `../config/settings.js`.

The `form/` folder, `app.js`, and the HTML page only matter for the demo page. You don't need them.

## Running the demo page

Run this from the project root, not from `front-end/`:

```bash
python -m ticket_server
# open http://127.0.0.1:8000/submission_form.html
```

That one command hosts the page and saves every submitted ticket to `data/tickets.json`. Press Ctrl+C to stop it.

The page has to come from this server. If you open the HTML file straight from disk, the browser blocks the scripts. If you open it from a different server, the saving request goes to the wrong place.

## How saving works

1. In the browser, `buildTicket()` cleans and checks the input.
2. `ticket-api.js` sends `{ customer_id, text }` to `POST /api/tickets`.
3. The server checks the input again, gives the ticket the next free ID (`T-1001`, `T-1002`, …, counting up from the highest ID already in the file), and appends it to `tickets.json`.
4. The server replies `201 { "id": "T-1004" }`. The page thanks the customer and shows the ticket number.

**Saving is write-only.** `POST /api/tickets` can only add tickets, and its reply contains only the new ID. The server never serves `data/` as files (it sits outside `front-end/`). The one read path is `GET /api/tickets/status`, used by `dashboard.html`, which returns every ticket with its status. That is fine while the server only listens on 127.0.0.1, but it must sit behind a login before the dashboard is ever exposed to other people.

The server ignores any `id` the browser sends. It assigns IDs itself, so they stay unique and sequential. The random ID that `buildTicket()` creates only matters when you use the builder without this server.

On errors, the server replies with `{ "error": "message" }` and one of these status codes:

| Code | When                                                  |
|------|-------------------------------------------------------|
| 400  | Invalid JSON, or the input breaks a rule              |
| 403  | The request came from a different website            |
| 413  | The body is larger than 10 KB                        |
| 415  | The Content-Type isn't `application/json`            |
| 500  | `tickets.json` is damaged or can't be written. The server never overwrites a damaged file, so you can fix it by hand without losing tickets. |

### Server settings

Everything is in `ticket_server/settings.py`: `HOST`, `PORT`, `TICKETS_FILE`, `TICKET_ID_START`, size limits, and `ALLOWED_ORIGINS`.

If you change `PORT`, `ALLOWED_ORIGINS` updates automatically. If you change the text or customer ID rules, change them in `front-end/js/config/settings.js` too, so the browser and server agree.

### Using your own backend

You don't have to use this server. Any backend that accepts `POST` with `{ customer_id, text }` and returns `{ "id": "..." }` works. Point `API_SETTINGS.ticketsEndpoint` in `js/config/settings.js` at it. If it runs on another origin, add that origin to the page's `connect-src` and enable CORS on the backend.

## The API

### `buildTicket(rawInput, options?)`

```js
import { buildTicket } from "./js/ticket-builder/index.js";

const { ticket, errors } = buildTicket({ customerId: "1001", text: "Export keeps failing" });

if (errors) {
  // errors looks like { customerId: "...", text: "...", id: "..." }; only failing keys are present
} else {
  // ticket looks like { id, customer_id, text } and is frozen (read-only)
}
```

| Input field  | Type   | Notes                                                        |
|--------------|--------|--------------------------------------------------------------|
| `customerId` | string | **Optional.** Empty or missing means `""` (the customer has no ID). Spaces are removed. Letters, numbers and `-` only. 20 characters max. |
| `text`       | string | Whitespace is collapsed to one line, invisible characters are removed, 10 to 2000 characters. |

The function always returns exactly `{ ticket, errors }`, and exactly one of the two is `null`. It never throws, even when you pass `null`, numbers, objects, or a broken `options` value.

**Options**

| Option        | Purpose                                                           |
|---------------|-------------------------------------------------------------------|
| `idGenerator` | A function that returns the ticket ID. Use it when your backend or database assigns IDs. If it throws or returns an empty value, you get `errors.id`. |
| `rules`       | Overrides some of the rules in `TICKET_RULES` for one call, e.g. `{ textMaxLength: 500 }`. |

```js
let next = 3001;
buildTicket(input, { idGenerator: () => `T-${next++}` });   // T-3001, T-3002, ...
```

### `validateTicketInput(cleanedInput, rules)` and `TICKET_RULES`

These are exported in case you want to validate input before calling the builder, for example while the user types. Use `TICKET_RULES` to show the limits in your own UI.

## Integration recipes

### 1. Your own HTML form

Your field names don't need to match ours. Map them yourself:

```html
<form id="support">
  <input name="account">
  <textarea name="message"></textarea>
  <button>Send</button>
</form>

<script type="module">
  import { buildTicket } from "/js/ticket-builder/index.js";

  document.getElementById("support").addEventListener("submit", (event) => {
    event.preventDefault();
    const form = event.target;
    const { ticket, errors } = buildTicket({
      customerId: form.account.value,
      text: form.message.value,
    });
    if (errors) return alert(Object.values(errors).join("\n"));
    console.log(ticket);
  });
</script>
```

### 2. Sending the ticket to a backend

```js
const { ticket, errors } = buildTicket(input);
if (!errors) {
  await fetch("/api/tickets", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(ticket),
  });
}
```

If the page has a Content-Security-Policy, add your API's origin to `connect-src`.

### 3. React, Vue, or Svelte

Call the builder in your submit handler. It is a plain function with no state:

```jsx
import { buildTicket } from "./ticket-builder/index.js";

function onSubmit() {
  const { ticket, errors } = buildTicket({ customerId, text });
  setErrors(errors ?? {});
  if (ticket) onTicketCreated(ticket);
}
```

### 4. Node.js (scripts, servers, tests)

The builder has no browser dependencies, so it also runs in Node 18 and later:

```js
import { buildTicket } from "./front-end/js/ticket-builder/index.js";
console.log(buildTicket({ customerId: "1001", text: "Charged twice this month" }).ticket);
```

## Customising

- **Rules and messages:** edit `js/config/settings.js`. All limits, the ID prefix, the ID length, and every error message are in that file. To translate the messages, replace the `MESSAGES` values.
- **Look and feel:** edit the variables at the top of `styles/theme.css`. Other pages can link the same file and reuse its variables (`var(--color-accent)`, `var(--font-display)`, and so on).
- **ID format:** when you use `ticket_server`, the server assigns sequential IDs (`T-1001`, …). When you use the builder on its own, the default is `T-` followed by 6 random digits. Pass `idGenerator` to use your own scheme.

## Security notes

- The builder only cleans input. It doesn't escape HTML, because a ticket is data. Whoever **displays** a ticket must insert it with `textContent` or a framework's normal text binding, never `innerHTML`. The demo page follows this rule.
- **Validate again on the server.** A user can bypass any browser-side check. `ticket_server` does this.
- `ticket_server` only listens on `127.0.0.1`, so other computers can't reach it. It refuses posts from other websites, never shows folder listings, and only serves files inside `front-end/`. It's built for local use. Don't put it on the public internet as it is: it has no login and no rate limiting.
- The demo page sends a strict Content-Security-Policy: scripts only from the page's own origin, no inline scripts, and fonts only from Google Fonts. Keep a similar policy when you embed the form elsewhere.
