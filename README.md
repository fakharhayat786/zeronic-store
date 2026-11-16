# ZERONIC — Premium Wireless Earbuds (Pakistan, Cash on Delivery)

A small custom e-commerce storefront: static HTML pages served by a tiny
Express server, with a real COD checkout and a simple orders dashboard.

> **Status: demo catalogue.** All products, prices, descriptions and the
> three review cards currently on the site are placeholders. Replace them
> with real products and real reviews before launch — see "Changing
> products" below. The review numbers that used to be on the site
> ("4.6 / 142 reviews", "1M+ customers", "15,000+ customers") were
> removed in Phase 2 because they had no evidence behind them. Do not
> re-add aggregate ratings until real, verifiable reviews exist.

> **Domain assumption.** Canonical URLs, the sitemap, `robots.txt` and
> social-sharing tags use `https://zeronicpk.store` — the domain named
> in the site's own contact details and Privacy Policy. If the live
> domain ends up different, search the repo for `zeronicpk.store` and
> update the canonical/OG/sitemap URLs together.

## What works

- **Real cart** — saved in the browser (`localStorage`), shared across all
  pages, with quantity and colour, subtotal and remove. The header badge and
  the cart drawer always show the same cart.
- **COD checkout on the site** — `/checkout`: name, phone, address, city,
  order summary, Cash on Delivery only. Orders get a number (`ZN-1001`,
  counting up) and a confirmation page. The server re-prices every order
  from `products.json`, so prices cannot be tampered with in the browser.
- **Orders dashboard** — `/admin`: sign in with the admin password, view
  orders newest-first, search by order number / name / phone, and change
  each order's status (New → Confirmed → Shipped → Delivered / Cancelled).
  Contact messages, newsletter subscribers and submitted reviews are
  listed there too.
- **Moderated reviews** — the Write-a-Review form sends to
  `POST /api/reviews` and stores the review as "pending" for the admin
  dashboard. Nothing a visitor submits appears on the product page
  automatically, and no review claims "Verified Buyer" any more.
- **Real contact + newsletter** — the contact form and footer newsletter
  forms save to the server.
- **Real search** — the search box filters the product catalogue on the
  homepage; on other pages it takes you to the matching homepage results.
- **One catalogue file** — `products.json` is the single source of truth
  for product names, prices, colours and images used by the cart, checkout
  and order pricing.
- **Complete policy pages** — Privacy, Shipping, Returns & Refunds
  (7-day returns, 13-month replacement warranty) and Terms of Service,
  all linked from every footer. The returns/warranty terms follow what
  the site already promised; confirm them before launch.
- **SEO foundations** — one canonical URL per page (clean paths, no
  `.html`), 301 redirects from legacy/duplicate URLs, `robots.txt`,
  `sitemap.xml`, favicon, Open Graph + Twitter cards with absolute
  image URLs, and JSON-LD (Organization/WebSite on the homepage,
  Product + FAQPage on the product page — no review aggregate, because
  there is no verified review data yet).
- **Real 404 + hardening** — unknown URLs get the branded 404 page with
  HTTP 404 (never the homepage with 200). The server sends security
  headers, gzip compression, and sensible cache headers (pages and
  prices always revalidated; images/JS cached for a day). Sensitive
  paths (`/data/`, `server.js`, `package.json`, edit scripts,
  duplicate `app/` copies, `*.orig.*` images) return 404.

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
http://localhost:3000/checkout
http://localhost:3000/admin
```

- Without `ADMIN_PASSWORD`, the store still works but `/admin` refuses
  access until the variable is set and the server is restarted.
- The GitHub preview link only shows the static design — the Express
  server (checkout, orders, admin) does **not** run there. Test the
  store with `node server.js` as above. Launching live later needs a
  Node host (for example Render or Railway) plus the domain.

## How orders are stored (please read before launch)

Orders, contact messages, newsletter subscribers and reviews are saved
as JSON files in `./data/` (`orders.json`, `messages.json`,
`subscribers.json`, `reviews.json`). This is deliberately simple, with
real limits:

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
5. If the real product has verified reviews, add them as static cards
   in `product.html` and only then consider an `aggregateRating` in
   the Product JSON-LD. Never invent review counts or ratings.

## Project layout

```
server.js               Express server: pages + /api/* + admin API
products.json           Catalogue (single source of truth) + settings
index.html              Homepage
product.html            Product detail page (ZERONIC Flex)
checkout.html           COD checkout + order confirmation
admin.html              Orders / messages / reviews / subscribers dashboard
contact-us.html         Contact page (real form -> /api/contact)
privacy-policy.html     Privacy policy
shipping-policy.html    Shipping policy
returns-policy.html     Returns & refunds + warranty claims
terms-of-service.html   Terms of service
404.html                Branded 404 page (served with HTTP 404)
favicon.svg             Site favicon
robots.txt              Crawler rules + sitemap location
sitemap.xml             Canonical page list for search engines
assets/js/zeronic.js    Shared cart, search, newsletter logic
assets/                 Images and logo
data/                   Runtime order/message data (git-ignored, created on first run)
```

## API summary

- `GET /api/products` — catalogue JSON (public).
- `POST /api/orders` — `{ customer: { name, phone, address, city, notes? }, items: [{ sku, colour, qty }] }` → `201 { order }`. Server-side pricing and Pakistani-mobile validation.
- `POST /api/contact` — `{ name, email, phone?, subject?, message }`.
- `POST /api/subscribe` — `{ email }` (duplicates return `already: true`).
- `POST /api/reviews` — `{ name, rating (1-5), text, sku? }` → stored as `pending` for moderation; visible only in `/admin`.
- `GET /api/admin/orders`, `GET /api/admin/messages`,
  `GET /api/admin/subscribers`, `GET /api/admin/reviews`,
  `PATCH /api/admin/orders/:id/status` — all require header
  `x-admin-password: <ADMIN_PASSWORD>`.

## Deliberately not done yet

- Payment gateway (COD only). Bank transfer is not offered: the old
  Privacy Policy mention was removed; add it only with real bank
  details and a checkout option.
- No Content-Security-Policy yet — the pages use inline scripts and
  styles, so a CSP must be browser-tested before it is switched on.
- Image optimisation: several images are very heavy (hero/product
  photos ~700KB+, one trust icon ~935KB). Compress and resize them,
  and add width/height attributes from the real dimensions, before
  launch. (Not done here: image binaries cannot be edited through
  the text-only GitHub workflow used for this pass.)
- No shared CSS file yet — each page still carries its own inline
  styles. Extracting shared styles is a bigger refactor that needs a
  browser visual check afterwards.
- No analytics yet — add GA4 / Search Console / Meta Pixel with the
  owner's real IDs when the domain is live.
- Gaming Pods and Pro Wireless have no detail pages yet; they can be
  added to the cart from the homepage. Detail pages come with the real
  catalogue (no invented specs).
- The `app/applet/` duplicate copies and the old Python edit scripts
  in the repo root are blocked from being served, but the files still
  exist in the repo. Delete them via git/GitHub when a laptop is
  available (the text-only push workflow cannot delete files).
