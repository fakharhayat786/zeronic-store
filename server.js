import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Set cache headers to avoid stale cached assets on live/published URLs
app.use((req, res, next) => {
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  next();
});

// Serve static assets and root files
app.use(express.static(__dirname, {
  etag: false,
  lastModified: false,
  setHeaders: (res) => {
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');
  }
}));

// Guarantee asset paths resolve even with sub-paths like /pages/assets or /shipping-policy/assets
app.use(['/assets', '/pages/assets', '/*/assets'], express.static(path.join(__dirname, 'assets'), {
  etag: false,
  lastModified: false,
  setHeaders: (res) => {
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');
  }
}));

// Privacy policy page route
app.get(['/privacy-policy', '/privacy', '/privacy.html'], (req, res) => {
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.sendFile(path.join(__dirname, 'privacy-policy.html'));
});

// Contact us page route
app.get(['/contact-us', '/contact', '/contact-us.html', '/pages/contact-us'], (req, res) => {
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.sendFile(path.join(__dirname, 'contact-us.html'));
});

// Shipping policy page route
app.get(['/shipping-policy', '/shipping', '/shipping-policy.html', '/pages/shipping-policy', '/pages/shipping-return-policy'], (req, res) => {
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.sendFile(path.join(__dirname, 'shipping-policy.html'));
});

// Route fallback to index.html
app.get('*', (req, res) => {
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`ZERONIC store running at http://0.0.0.0:${PORT}`);
});
