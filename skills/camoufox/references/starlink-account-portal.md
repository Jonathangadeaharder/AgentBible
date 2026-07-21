# Starlink Account Portal — Automation Notes

## Login Flow

- URL: `https://www.starlink.com/account` → redirects to login
- Email + password + 2FA (email-based verification code)
- 2FA code sent to account email, retrieve via `himalaya message read -a gmail <ID>`
- Cookie banner: OneTrust — reject with `click_element '#onetrust-reject-all-handler'`

## Account Structure

- Account ID format: `ACC-DF-XXXXXXXXXX-XXXXX-XX`
- Order ID format: `ORD-DF-XXXXXXXXXXXXXXXXXX`
- Service Line ID format: `SL-DF-XXXXXXXXXX-XXXXX-XX`
- Billing via PayPal (plus-address email)

## Order Detail Page

- Orders list at `/account/orders` — MUI DataGrid
- Row click requires `eval` with `dispatchEvent` (see SKILL.md "MUI DataGrid Row Click")
- Direct URL: `/account/order/<ORDER_ID>` works after row click
- Order statuses: `Shipped`, `Closed`, `Returned`, `Cancelled`
- `Return` button may be `disabled` even when status shows "Returned" — means RMA initiated but not necessarily completed

## Return Kit Workflow

1. Check order status — if "Returned" with disabled Return button, RMA is initiated
2. Check DHL tracking number from order detail — `<TRACKING_NUMBER>` format
3. Verify at DHL tracking page — if "We are expecting your shipment data soon", package was never shipped
4. Create support ticket via chatbot:
   - Navigate to `/support/tickets` → "New Ticket"
   - Or use chatbot at `/support/contact` → describe issue → chatbot suggests "Create a Ticket"
   - "Create a Ticket" is a `<p>` element, not a button — use `eval` text scan
5. Form requires: Title (max 100 chars), Description, optional order number
6. Chatbot pre-fills title/description from conversation context

## Key URLs

- Login: `https://www.starlink.com/account`
- Orders: `https://www.starlink.com/account/orders`
- Order detail: `https://www.starlink.com/account/order/<ORDER_ID>`
- Subscriptions: `https://www.starlink.com/account/subscriptions`
- Billing: `https://www.starlink.com/account/billing`
- Support tickets: `https://www.starlink.com/support/tickets`
- Contact form: `https://www.starlink.com/support/contact`
- DHL tracking: `https://www.dhl.de/en/privatkunden/dhl-sendungsverfolgung.html?piececode=<TRACKING_NUMBER>`

## Pitfalls

- Title field has 100 char limit — chatbot-generated titles often exceed this. Shorten before submit.
- Autocomplete order field needs native value setter (React-controlled, `fill_element` fails silently).
- Chatbot "Create a Ticket" link is a `<p>` element with `children.length === 0` — not a button.
- Support chatbot is powered by Grok — responds with suggestions, not direct actions.
- DHL tracking may show "expecting shipment data" even when Starlink shows "Returned" status — means label created but package not yet shipped.
