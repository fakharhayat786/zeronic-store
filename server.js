import express from 'express';
import compression from 'compression';
import path from 'path';
import fs from 'fs';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

/* Trust exactly one proxy hop (Render). Behind Render, req.ip would
   otherwise be the proxy's own address, so every visitor would share
   a single rate-limit bucket. With this, req.ip is the real client IP
   from X-Forwarded-For. */
app.set('trust proxy', 1);
const PORT = process.env.PORT || 3000;

app.disable('x-powered-by');

/* ------------------------------------------------------------------ */
/* Security headers (all responses). No Content-Security-Policy yet:  */
/* the pages use inline scripts/styles, so a CSP needs browser testing */
/* before it can be tightened safely — see README.md.                  */
/* ------------------------------------------------------------------ */
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'SAMEORIGIN');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), payment=()');
  next();
});

/* Gzip/deflate for HTML, CSS, JS and JSON responses. */
app.use(compression());

/* ------------------------------------------------------------------ */
/* Catalogue: products.json is the single source of truth for prices. */
/* The server re-prices every order from this file — client totals   */
/* are never trusted. Startup fails loudly if the file is invalid.   */
/* ------------------------------------------------------------------ */
let CATALOG;
try {
  CATALOG = JSON.parse(fs.readFileSync(path.join(__dirname, 'products.json'), 'utf8'));
  if (!CATALOG || !Array.isArray(CATALOG.products) || !CATALOG.products.length) {
    throw new Error('products.json has no products');
  }
} catch (err) {
  console.error('FATAL: could not load products.json:', err.message);
  process.exit(1);
}
const PRODUCTS_BY_SKU = new Map(CATALOG.products.map((p) => [p.sku, p]));
const DELIVERY_FEE = typeof CATALOG.settings?.deliveryFee === 'number' ? CATALOG.settings.deliveryFee : 0;

/* ------------------------------------------------------------------ */
/* JSON-file storage. Orders, messages, subscribers and reviews live   */
/* in ./data/*.json — see README.md for the limits of this approach    */
/* (single-server, no database yet; back up ./data before redeploys).  */
/* ./data is git-ignored so customer details never land in the repo.   */
/* ------------------------------------------------------------------ */
const DATA_DIR = path.join(__dirname, 'data');
fs.mkdirSync(DATA_DIR, { recursive: true });

function readJsonFile(file, fallback) {
  try {
    return JSON.parse(fs.readFileSync(path.join(DATA_DIR, file), 'utf8'));
  } catch {
    return fallback;
  }
}

function writeJsonFile(file, data) {
  const target = path.join(DATA_DIR, file);
  const tmp = `${target}.tmp-${process.pid}`;
  fs.writeFileSync(tmp, JSON.stringify(data, null, 2), 'utf8');
  fs.renameSync(tmp, target);
}

function nextOrderNumber() {
  const meta = readJsonFile('meta.json', { lastOrderSeq: 1000 });
  const seq = (typeof meta.lastOrderSeq === 'number' ? meta.lastOrderSeq : 1000) + 1;
  writeJsonFile('meta.json', { lastOrderSeq: seq });
  return { number: `ZN-${seq}`, seq };
}

/* ------------------------------------------------------------------ */
/* Validation helpers                                                  */
/* ------------------------------------------------------------------ */
function cleanText(value, maxLen) {
  if (typeof value !== 'string') return '';
  // Trim, cap length, strip control characters (keep newlines in addresses).
  return value.trim().replace(/[^\S\n ]+/g, ' ').replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '').slice(0, maxLen);
}

function normalizePhone(raw) {
  const digits = String(raw || '').replace(/[^\d]/g, '');
  if (digits.startsWith('92')) return `0${digits.slice(2)}`;
  return digits;
}

function isValidPakistaniMobile(raw) {
  return /^03\d{9}$/.test(normalizePhone(raw));
}

function isValidEmail(raw) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(raw || '').trim());
}

function badRequest(res, message, field) {
  return res.status(400).json(field ? { error: message, field } : { error: message });
}

/* ------------------------------------------------------------------ */
/* Simple in-memory rate limit for /api/* (60 requests/minute per IP). */
/* Guards the order/contact endpoints against casual flooding.         */
/* ------------------------------------------------------------------ */
const rateBuckets = new Map();
function apiRateLimit(req, res, next) {
  const now = Date.now();
  const key = req.ip || 'unknown';
  const bucket = rateBuckets.get(key);
  if (!bucket || now >= bucket.resetAt) {
    rateBuckets.set(key, { count: 1, resetAt: now + 60_000 });
    return next();
  }
  bucket.count += 1;
  if (bucket.count > 60) {
    return res.status(429).json({ error: 'Too many requests. Please try again in a moment.' });
  }
  return next();
}

/* ------------------------------------------------------------------ */
/* Block sensitive paths BEFORE static serving. express.static serves  */
/* the repo root, so without this guard the edit scripts, server code, */
/* package metadata and the ./data store would be public. Also blocks  */
/* the duplicate app/ copies and *.orig.* images from being served —   */
/* they stay in the repo (git history) but never reach visitors.       */
/* ------------------------------------------------------------------ */
const BLOCKED_BASENAMES = new Set(['package.json', 'bun.lock', 'server.js', 'metadata.json', '404.html']);
app.use((req, res, next) => {
  const pathname = req.path || '';
  const base = path.basename(pathname);
  if (
    pathname.startsWith('/data/') ||
    pathname.startsWith('/node_modules/') ||
    pathname.startsWith('/.git/') ||
    pathname.startsWith('/app/') ||
    pathname === '/app' ||
    pathname.endsWith('.py') ||
    pathname.startsWith('/.env') ||
    base.includes('.orig.') ||
    BLOCKED_BASENAMES.has(base)
  ) {
    return res.status(404).json({ error: 'Not found.' });
  }
  return next();
});

/* ------------------------------------------------------------------ */
/* Canonical redirects (301, query string preserved). One canonical    */
/* URL per page: clean paths, no .html, no trailing slash. Legacy and  */
/* duplicate URLs (old /products/th-flex, /privacy, /pages/*, .html    */
/* versions, /index.html) redirect here so search engines and visitors */
/* always land on the canonical page. Checkout/admin .html URLs are    */
/* deliberately NOT redirected — they are noindex utility pages.       */
/* ------------------------------------------------------------------ */
const CANONICAL_REDIRECTS = new Map([
  ['/index.html', '/'],
  ['/privacy', '/privacy-policy'],
  ['/privacy.html', '/privacy-policy'],
  ['/privacy-policy/index.html', '/privacy-policy'],
  ['/privacy-policy.html', '/privacy-policy'],
  ['/contact', '/contact-us'],
  ['/contact-us.html', '/contact-us'],
  ['/contact-us/index.html', '/contact-us'],
  ['/pages/contact-us', '/contact-us'],
  ['/shipping', '/shipping-policy'],
  ['/shipping-policy.html', '/shipping-policy'],
  ['/shipping-policy/index.html', '/shipping-policy'],
  ['/pages/shipping-policy', '/shipping-policy'],
  ['/pages/shipping-return-policy', '/shipping-policy'],
  ['/product.html', '/product'],
  ['/products/zeronic-flex', '/product'],
  ['/products/th-flex', '/product'],
  ['/zeronic-flex', '/product'],
  ['/zeronic-flex.html', '/product'],
  ['/returns-policy.html', '/returns-policy'],
  ['/terms-of-service.html', '/terms-of-service'],
]);

app.use((req, res, next) => {
  if (req.method !== 'GET' && req.method !== 'HEAD') return next();
  const pathname = req.path || '';
  const queryIndex = req.originalUrl.indexOf('?');
  const query = queryIndex >= 0 ? req.originalUrl.slice(queryIndex) : '';
  const target = CANONICAL_REDIRECTS.get(pathname);
  if (target) {
    return res.redirect(301, target + query);
  }
  if (pathname.length > 1 && pathname.endsWith('/')) {
    return res.redirect(301, pathname.slice(0, -1) + query);
  }
  return next();
});

app.use(express.json({ limit: '64kb' }));
app.use((err, req, res, next) => {
  if (err && err.type === 'entity.parse.failed') {
    return res.status(400).json({ error: 'Invalid request format.' });
  }
  return next(err);
});
app.use('/api/', (req, res, next) => {
  res.setHeader('Cache-Control', 'no-store');
  next();
}, apiRateLimit);

/* ------------------------------------------------------------------ */
/* Public API                                                          */
/* ------------------------------------------------------------------ */
app.get('/api/products', (req, res) => {
  res.json(CATALOG);
});

const ORDER_STATUSES = ['New', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled'];

app.post('/api/orders', (req, res) => {
  const body = req.body && typeof req.body === 'object' ? req.body : {};
  const customer = body.customer && typeof body.customer === 'object' ? body.customer : {};
  const items = Array.isArray(body.items) ? body.items : [];

  const name = cleanText(customer.name, 100);
  const phoneRaw = cleanText(customer.phone, 20);
  const email = cleanText(customer.email, 200);
  const address = cleanText(customer.address, 500);
  const city = cleanText(customer.city, 100);
  const notes = cleanText(customer.notes, 500);

  if (name.length < 2) return badRequest(res, 'Please enter your full name.', 'name');
  if (!isValidPakistaniMobile(phoneRaw)) {
    return badRequest(res, 'Please enter a valid Pakistani mobile number, e.g. 03XX-XXXXXXX.', 'phone');
  }
  if (email && !isValidEmail(email)) {
    return badRequest(res, 'Please enter a valid email address, or leave it blank.', 'email');
  }
  if (address.length < 10) return badRequest(res, 'Please enter your complete delivery address.', 'address');
  if (city.length < 2) return badRequest(res, 'Please enter your city.', 'city');
  if (!items.length) return badRequest(res, 'Your cart is empty.');
  if (items.length > 10) return badRequest(res, 'Too many different items in one order.');

  // Price every line from the catalogue. Client-supplied prices are ignored.
  const pricedItems = [];
  let subtotal = 0;
  for (const item of items) {
    if (!item || typeof item !== 'object') return badRequest(res, 'Invalid order item.');
    const product = PRODUCTS_BY_SKU.get(item.sku);
    if (!product) return badRequest(res, 'One of the products in your cart is no longer available.');
    const colourNames = (product.colours || []).map((c) => c.name);
    const colour = typeof item.colour === 'string' && colourNames.includes(item.colour)
      ? item.colour
      : colourNames[0] || 'Standard';
    const qty = Number.parseInt(item.qty, 10);
    if (!Number.isInteger(qty) || qty < 1 || qty > 10) {
      return badRequest(res, 'Quantity must be between 1 and 10 per item.');
    }
    const lineTotal = product.price * qty;
    subtotal += lineTotal;
    pricedItems.push({
      sku: product.sku,
      name: product.name,
      colour,
      unitPrice: product.price,
      qty,
      lineTotal,
    });
  }

  const { number, seq } = nextOrderNumber();
  const order = {
    id: crypto.randomUUID(),
    number,
    seq,
    customer: { name, phone: normalizePhone(phoneRaw), email, address, city, notes },
    items: pricedItems,
    subtotal,
    deliveryFee: DELIVERY_FEE,
    total: subtotal + DELIVERY_FEE,
    payment: 'COD',
    status: 'New',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  const orders = readJsonFile('orders.json', []);
  orders.push(order);
  writeJsonFile('orders.json', orders);

  return res.status(201).json({ order });
});

app.post('/api/contact', (req, res) => {
  const body = req.body && typeof req.body === 'object' ? req.body : {};
  const name = cleanText(body.name, 100);
  const email = cleanText(body.email, 200);
  const phone = cleanText(body.phone, 30);
  const subject = cleanText(body.subject, 200);
  const message = cleanText(body.message, 2000);

  if (name.length < 2) return badRequest(res, 'Please enter your name.', 'name');
  if (!isValidEmail(email)) return badRequest(res, 'Please enter a valid email address.', 'email');
  if (message.length < 5) return badRequest(res, 'Please write your message.', 'message');

  const messages = readJsonFile('messages.json', []);
  messages.push({
    id: crypto.randomUUID(),
    name,
    email,
    phone,
    subject,
    message,
    createdAt: new Date().toISOString(),
  });
  writeJsonFile('messages.json', messages);
  return res.status(201).json({ ok: true });
});

app.post('/api/subscribe', (req, res) => {
  const body = req.body && typeof req.body === 'object' ? req.body : {};
  const email = cleanText(body.email, 200).toLowerCase();
  if (!isValidEmail(email)) return badRequest(res, 'Please enter a valid email address.', 'email');

  const subscribers = readJsonFile('subscribers.json', []);
  if (subscribers.some((s) => String(s.email || '').toLowerCase() === email)) {
    return res.status(200).json({ ok: true, already: true });
  }
  subscribers.push({ id: crypto.randomUUID(), email, createdAt: new Date().toISOString() });
  writeJsonFile('subscribers.json', subscribers);
  return res.status(201).json({ ok: true, already: false });
});

/* Reviews are stored as "pending" and shown only in the admin dashboard. */
/* Nothing a visitor submits appears on the product page automatically.   */
app.post('/api/reviews', (req, res) => {
  const body = req.body && typeof req.body === 'object' ? req.body : {};
  const name = cleanText(body.name, 100);
  const text = cleanText(body.text, 1000);
  const rating = Number.parseInt(body.rating, 10);
  const sku = typeof body.sku === 'string' && body.sku ? body.sku : 'flex';

  if (name.length < 2) return badRequest(res, 'Please enter your name.', 'name');
  if (!Number.isInteger(rating) || rating < 1 || rating > 5) {
    return badRequest(res, 'Please choose a rating between 1 and 5 stars.', 'rating');
  }
  if (text.length < 5) return badRequest(res, 'Please write a few words about the product.', 'text');
  if (!PRODUCTS_BY_SKU.has(sku)) return badRequest(res, 'Unknown product.');

  const reviews = readJsonFile('reviews.json', []);
  reviews.push({
    id: crypto.randomUUID(),
    name,
    rating,
    text,
    sku,
    status: 'pending',
    createdAt: new Date().toISOString(),
  });
  writeJsonFile('reviews.json', reviews);
  return res.status(201).json({ ok: true });
});

/* Order tracking: order number + the phone used at checkout. Returns only
   status and order summary — never the customer's name or address. Every
   failure (bad number, bad phone, no match) gets the same generic 404 so
   the endpoint cannot be used to probe which orders exist. Rate-limited
   with the rest of /api/*. */
app.get('/api/track', (req, res) => {
  const noMatch = 'No order matches these details. Please check the order number and phone number.';
  const rawNumber = String(req.query.number || '').trim().toUpperCase();
  const phoneRaw = cleanText(req.query.phone, 20);
  if (!/^ZN-\d+$/.test(rawNumber)) return res.status(404).json({ error: noMatch });
  if (!isValidPakistaniMobile(phoneRaw)) return res.status(404).json({ error: noMatch });
  const orders = readJsonFile('orders.json', []);
  const order = orders.find((o) => o.number === rawNumber);
  if (!order || normalizePhone(order.customer.phone) !== normalizePhone(phoneRaw)) {
    return res.status(404).json({ error: noMatch });
  }
  return res.json({
    order: {
      number: order.number,
      status: order.status,
      createdAt: order.createdAt,
      items: order.items,
      subtotal: order.subtotal,
      deliveryFee: order.deliveryFee,
      total: order.total,
      payment: order.payment,
    },
  });
});

/* ------------------------------------------------------------------ */
/* Admin API — protected by ADMIN_PASSWORD (env var, never hard-coded).*/
/* The dashboard sends it as x-admin-password on every request. If the */
/* variable is unset, admin endpoints refuse with 503 until it is set. */
/* ------------------------------------------------------------------ */
function requireAdmin(req, res, next) {
  const configured = process.env.ADMIN_PASSWORD;
  if (!configured) {
    return res.status(503).json({
      error: 'Admin access is not configured on this server. Set ADMIN_PASSWORD and restart.',
    });
  }
  const supplied = req.get('x-admin-password') || '';
  const a = crypto.createHash('sha256').update(supplied).digest();
  const b = crypto.createHash('sha256').update(configured).digest();
  if (!crypto.timingSafeEqual(a, b)) {
    return res.status(401).json({ error: 'Unauthorized.' });
  }
  return next();
}

function newestFirst(list) {
  return [...list].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
}

app.get('/api/admin/orders', requireAdmin, (req, res) => {
  res.json({ orders: newestFirst(readJsonFile('orders.json', [])) });
});

app.patch('/api/admin/orders/:id/status', requireAdmin, (req, res) => {
  const body = req.body && typeof req.body === 'object' ? req.body : {};
  if (!ORDER_STATUSES.includes(body.status)) {
    return badRequest(res, 'Invalid status.');
  }
  const orders = readJsonFile('orders.json', []);
  const order = orders.find((o) => o.id === req.params.id);
  if (!order) return res.status(404).json({ error: 'Order not found.' });
  order.status = body.status;
  order.updatedAt = new Date().toISOString();
  writeJsonFile('orders.json', orders);
  return res.json({ order });
});

app.get('/api/admin/messages', requireAdmin, (req, res) => {
  res.json({ messages: newestFirst(readJsonFile('messages.json', [])) });
});

app.get('/api/admin/subscribers', requireAdmin, (req, res) => {
  res.json({ subscribers: newestFirst(readJsonFile('subscribers.json', [])) });
});

app.get('/api/admin/reviews', requireAdmin, (req, res) => {
  res.json({ reviews: newestFirst(readJsonFile('reviews.json', [])) });
});

// Unknown API paths return JSON, not the homepage or the 404 page.
app.all('/api/*', (req, res) => {
  res.status(404).json({ error: 'Not found.' });
});

/* ------------------------------------------------------------------ */
/* Static files. Pages and data files are always revalidated (prices   */
/* and content must never go stale); images, fonts, CSS and JS may be  */
/* cached by the browser for a day, with ETag revalidation after that. */
/* ------------------------------------------------------------------ */
function staticCacheHeaders(res, filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === '.html' || ext === '.htm' || ext === '.json' || ext === '.xml' || ext === '.txt') {
    res.setHeader('Cache-Control', 'no-cache');
  } else {
    res.setHeader('Cache-Control', 'public, max-age=86400, must-revalidate');
  }
}

app.use(express.static(__dirname, { index: false, redirect: false, setHeaders: staticCacheHeaders }));

// Guarantee asset paths resolve even with sub-paths like /pages/assets or /shipping-policy/assets
app.use(['/assets', '/pages/assets', '/*/assets'], express.static(path.join(__dirname, 'assets'), {
  index: false,
  redirect: false,
  setHeaders: staticCacheHeaders,
}));

function sendPage(file) {
  return (req, res) => {
    res.setHeader('Cache-Control', 'no-cache');
    res.sendFile(path.join(__dirname, file));
  };
}

// Health check for hosting platforms (Render healthCheckPath: /healthz).
app.get('/healthz', (req, res) => {
  res.json({ ok: true });
});

// Page routes — clean canonical URLs only (see the redirect map above).
app.get('/', sendPage('index.html'));
app.get('/privacy-policy', sendPage('privacy-policy.html'));
app.get('/contact-us', sendPage('contact-us.html'));
app.get('/shipping-policy', sendPage('shipping-policy.html'));
app.get('/returns-policy', sendPage('returns-policy.html'));
app.get('/terms-of-service', sendPage('terms-of-service.html'));
app.get('/product', sendPage('product.html'));

// Checkout page route (COD checkout on the site itself; .html kept working)
app.get(['/checkout', '/checkout.html'], sendPage('checkout.html'));

// Track-order page route (utility page; .html kept working, noindex)
app.get(['/track-order', '/track-order.html'], sendPage('track-order.html'));

// Admin dashboard route (orders, messages, reviews, subscribers)
app.get(['/admin', '/admin.html'], sendPage('admin.html'));

/* Real 404: unknown URLs get the branded 404 page with HTTP 404 —     */
/* never the homepage with 200. API-style requests get a JSON 404.     */
app.use((req, res) => {
  if (req.method === 'GET' && req.accepts('html')) {
    res.status(404);
    res.setHeader('Cache-Control', 'no-cache');
    res.sendFile(path.join(__dirname, '404.html'));
    return;
  }
  res.status(404).json({ error: 'Not found.' });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`ZERONIC store running at http://0.0.0.0:${PORT}`);
  console.log(`Admin dashboard: ${process.env.ADMIN_PASSWORD ? 'configured (ADMIN_PASSWORD is set)' : 'NOT configured — set ADMIN_PASSWORD to enable /admin'}`);
  console.log(`Orders are stored in ${DATA_DIR} (JSON files; see README.md)`);
});
