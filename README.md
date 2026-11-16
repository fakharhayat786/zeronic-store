# ZERONIC — Premium Wireless Earbuds (Pakistan, Cash on Delivery)

A small custom e-commerce storefront: static HTML pages served by a tiny
Express server, with a real COD checkout and a simple orders dashboard.

> **Status: demo catalogue.** All products, prices, descriptions and review
> figures currently on the site are placeholders. Replace them in
> `products.json` (and the product page copy) before launch — see
> "Changing products" below.

## What works (Phase 1)

- **Real cart** — saved in the browser (`localStorage`), shared across all
  pages, with quantity and colour, subtotal and remove. The header badge and
  the cart drawer always show the same cart.
- **COD checkout on the site** — `checkout.html`: name, phone, address, city,
  order summary, Cash on Delivery only. Orders get a number (`ZN-1001`,
  counting up) and a confirmation page. The server re-prices every order
  from `products.json`, so prices cannot be tampered with in the browser.
- **Orders dashboard** — `/admin`: sign in with the admin password, view
  orders newest-first, search by order number / name / phone, and change
  each order's status (New → Confirmed → Shipped → Delivered / Cancelled).
  Contact messages and newsletter subscribers are listed there too.
- **Real contact + newsletter** — the contact form and footer newsletter
  forms now save to the server (previously they only pretended to send).
- **Real search** — the search box filters the product catalogue on the
  homepage; on other pages it takes you to the matching homepage results.
- **One catalogue file** — `products.json` is the single source of truth
  for product names, prices, colours and images used by the cart, checkout
  and order pricing.

## Run it locally

You need Node.js 18+ installed.

```bash
npm install
```

Start the server with an admin password set (PowerShell on Windows):

```powershell
$env:ADMIN_PASSWORD="choose-a-strong-password"; node server.js
```

Or on macOS / Linux:

```bash
ADMIN_PASSWORD="choose-a-strong-password" node server.js
```

Then open these in your browser (plain text, copy-paste friendly):

```
http://localhost:3000/
http://localhost:3000/checkout.html
http://localhost:3000/admin
```

- Without `ADMIN_PASSWORD`, the store still works but `/admin` refuses
  access until the variable is set and the server is restarted.
- The GitHub preview link only shows the static design — the Express
  server (checkout, orders, admin) does **not** run there. Test the
  store with `node server.js` as above. Launching live later needs a
  Node host (for example Render or Railway) plus the domain.

## How orders are stored (please read before launch)

Orders, contact messages and newsletter subscribers are saved as JSON
files in `./data/` (`orders.json`, `messages.json`, `subscribers.json`).
This is deliberately simple for Phase 1, with real limits:

- **No database yet.** Fine for testing and low volume; move to a proper
  database (or a third-party order service) before heavy traffic.
- **Back up `./data/` before redeploying.** On hosts with ephemeral
  filesystems (most free tiers), files written at runtime can disappear
  on redeploy or restart. Copy the folder down regularly until a
  database replaces it.
- **`./data/*.json` is git-ignored on purpose.** Customer names, phones
  and addresses must never be committed to this public repository.
- **Admin auth is a single shared password** sent as a header and kept
  only in the browser tab (`sessionStorage`). Good enough for one owner
  testing locally; add proper accounts / HTTPS-only hosting before
  real customer data flows through it. Always run the live site over
  HTTPS.

## Changing products

1. Edit `products.json` — name, `price`, `comparePrice`, `colours`
   (name + image), `image`, `shortDesc`. Keep each `sku` unique and
   stable; never reuse an old SKU for a different product.
2. Keep the embedded fallback catalogue in `assets/js/zeronic.js`
   (`FALLBACK`) in sync with `products.json`. It is only used when
   `products.json` cannot be fetched, but a stale fallback shows stale
   prices on static previews.
3. Update the product page copy in `product.html` (specs, FAQ, reviews)
   to match the real product. The homepage cards still use hard-coded
   titles/prices in `index.html` — update those lines too until the
   homepage is switched to render from `products.json` (planned).
4. Delivery fee lives in `products.json` under `settings.deliveryFee`
   (currently `0` = free shipping). The checkout page text says
   delivery is free — change that text too if you ever charge delivery.

## Project layout

```
server.js               Express server: pages + /api/* + admin API
products.json           Catalogue (single source of truth) + settings
index.html              Homepage
product.html            Product detail page (ZERONIC Flex)
checkout.html           COD checkout + order confirmation
admin.html              Orders / messages / subscribers dashboard
contact-us.html         Contact page (real form -> /api/contact)
privacy-policy.html     Privacy policy
shipping-policy.html    Shipping policy
assets/js/zeronic.js    Shared cart, search, newsletter logic
assets/                 Images and logo
data/                   Runtime order/message data (git-ignored, created on first run)
```

## API summary

- `GET /api/products` — catalogue JSON (public).
- `POST /api/orders` — `{ customer: { name, phone, address, city, notes? }, items: [{ sku, colour, qty }] }` → `201 { order }`. Server-side pricing and Pakistani-mobile validation.
- `POST /api/contact` — `{ name, email, phone?, subject?, message }`.
- `POST /api/subscribe` — `{ email }` (duplicates return `already: true`).
- `GET /api/admin/orders`, `GET /api/admin/messages`,
  `GET /api/admin/subscribers`, `PATCH /api/admin/orders/:id/status` —
  all require header `x-admin-password: <ADMIN_PASSWORD>`.

## Deliberately not done yet

- Payment gateway (COD only). The "Secure Payments" wording on the site
  predates Phase 1 and must be revisited before launch.
- Reviews: the "142 reviews / 4.6" figure and self-posted "Verified
  Buyer" reviews are untouched — reconcile with real evidence first.
- SEO/technical pass (canonical URLs, robots.txt, sitemap, schema,
  real 404, caching, image optimisation, shared CSS) — planned after
  the domain exists.
- Gaming Pods and Pro Wireless have no detail pages yet; they can be
  added to the cart from the homepage. Detail pages come with the real
  catalogue (no invented specs).
- The `app/applet/` duplicate copies and the old Python edit scripts in
  the repo root are untouched in Phase 1 and should be cleaned up
  before launch.
