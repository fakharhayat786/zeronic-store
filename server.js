import express from 'express';
import path from 'path';
import fs from 'fs';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

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
/* JSON-file storage (Phase 1). Orders, messages and subscribers live  */
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
/* the repo root (existing behaviour), so without this guard the edit  */
/* scripts, package metadata and the ./data store would be public.     */
/* ------------------------------------------------------------------ */
const BLOCKED_BASENAMES = new Set(['package.json', 'bun.lock']);
app.use((req, res, next) => {
  const pathname = req.path || '';
  const base = path.basename(pathname);
  if (
    pathname.startsWith('/data/') ||
    pathname.startsWith('/node_modules/') ||
    pathname.startsWith('/.git/') ||
    pathname.endsWith('.py') ||
    pathname.startsWith('/.env') ||
    BLOCKED_BASENAMES.has(base)
  ) {
    return res.status(404).json({ error: 'Not found.' });
  }
  return next();
});

// Set cache headers to avoid stale cached assets on live/published URLs.
// NOTE (Phase 3): this no-cache-everything policy hurts speed; it is kept
// for now so Phase 1 behaviour matches what the site already did.
app.use((req, res, next) => {
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  next();
});

app.use(express.json({ limit: '64kb' }));
app.use((err, req, res, next) => {
  if (err && err.type === 'entity.parse.failed') {
    return res.status(400).json({ error: 'Invalid request format.' });
  }
  return next(err);
});
app.use('/api/', apiRateLimit);

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
  const address = cleanText(customer.address, 500);
  const city = cleanText(customer.city, 100);
  const notes = cleanText(customer.notes, 500);

  if (name.length < 2) return badRequest(res, 'Please enter your full name.', 'name');
  if (!isValidPakistaniMobile(phoneRaw)) {
    return badRequest(res, 'Please enter a valid Pakistani mobile number, e.g. 03XX-XXXXXXX.', 'phone');
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
    customer: { name, phone: normalizePhone(phoneRaw), address, city, notes },
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

/* ------------------------------------------------------------------ */
/* Static files + page routes (existing behaviour, kept intact).       */
/* ------------------------------------------------------------------ */
app.use(express.static(__dirname, {
  etag: false,
  lastModified: false,
  setHeaders: (res) => {
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');
  },
}));

// Guarantee asset paths resolve even with sub-paths like /pages/assets or /shipping-policy/assets
app.use(['/assets', '/pages/assets', '/*/assets'], express.static(path.join(__dirname, 'assets'), {
  etag: false,
  lastModified: false,
  setHeaders: (res) => {
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');
  },
}));

function sendPage(file) {
  return (req, res) => {
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.sendFile(path.join(__dirname, file));
  };
}

// Privacy policy page route
app.get(['/privacy-policy', '/privacy', '/privacy.html', '/privacy-policy/', '/privacy-policy/index.html'], sendPage('privacy-policy.html'));

// Contact us page route
app.get(['/contact-us', '/contact', '/contact-us.html', '/pages/contact-us', '/contact-us/', '/contact-us/index.html'], sendPage('contact-us.html'));

// Shipping policy page route
app.get(['/shipping-policy', '/shipping', '/shipping-policy.html', '/pages/shipping-policy', '/pages/shipping-return-policy', '/shipping-policy/', '/shipping-policy/index.html'], sendPage('shipping-policy.html'));

// Product page route
app.get(['/product', '/product.html', '/products/zeronic-flex', '/products/th-flex', '/zeronic-flex', '/zeronic-flex.html'], sendPage('product.html'));

// Checkout page route (Phase 1: COD checkout on the site itself)
app.get(['/checkout', '/checkout.html'], sendPage('checkout.html'));

// Admin dashboard route (Phase 1: orders, messages, subscribers)
app.get(['/admin', '/admin.html'], sendPage('admin.html'));

// Unknown API paths return JSON, not the homepage.
app.all('/api/*', (req, res) => {
  res.status(404).json({ error: 'Not found.' });
});

// Route fallback to index.html.
// NOTE (Phase 3): this catch-all returns the homepage with HTTP 200 for
// every unknown URL, so there is no real 404 page yet. It is kept for now
// to preserve existing behaviour; Phase 3 replaces it with a real 404.
app.get('*', (req, res) => {
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`ZERONIC store running at http://0.0.0.0:${PORT}`);
  console.log(`Admin dashboard: ${process.env.ADMIN_PASSWORD ? 'configured (ADMIN_PASSWORD is set)' : 'NOT configured — set ADMIN_PASSWORD to enable /admin'}`);
  console.log(`Orders are stored in ${DATA_DIR} (JSON files; see README.md)`);
});
