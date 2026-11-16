/* ==========================================================================
   ZERONIC shared store logic (Phase 1)
   Loaded by every storefront page. Provides:
   - product catalogue (from products.json, with an embedded fallback below)
   - real cart saved in localStorage, shared across pages
   - cart drawer rendering + header badge sync
   - newsletter subscribe (POST /api/subscribe)
   - real product search (filters the catalogue on the homepage)
   Everything lives inside one IIFE so it cannot clash with each page's own
   inline script (which still owns openCart/closeCart, menus and galleries).
   Catalogue source of truth is products.json. Keep FALLBACK below in sync
   with products.json — it is only used when products.json cannot be fetched
   (for example on a static preview without the Express server).
   ========================================================================== */
(function () {
  'use strict';

  var CART_KEY = 'zeronic_cart_v1';
  var MAX_QTY = 10;

  var FALLBACK = {
    settings: {
      currency: 'PKR',
      deliveryFee: 0,
      freeShipping: true,
      supportEmail: 'support@zeronicpk.store',
      supportPhone: '+92 342 0672554',
      supportWhatsApp: 'https://wa.me/923420672554'
    },
    products: [
      {
        sku: 'flex',
        name: 'ZERONIC Flex Earbuds',
        price: 4950,
        comparePrice: 7000,
        image: 'assets/airpods-1.png',
        shortDesc: 'Ultra Bass | Clear Sound | USB-C',
        colours: [
          { name: 'Flex Black', image: 'assets/airpods-1.png' },
          { name: 'Flex White', image: 'assets/airpods-2.png' }
        ]
      },
      {
        sku: 'gaming-pods',
        name: 'ZERONIC Gaming Pods',
        price: 5250,
        comparePrice: null,
        image: 'assets/airpods-2.png',
        shortDesc: 'Mode Switch | Dual Mic for Calls',
        colours: [{ name: 'Standard', image: 'assets/airpods-2.png' }]
      },
      {
        sku: 'pro-wireless',
        name: 'ZERONIC Pro Wireless',
        price: 6490,
        comparePrice: null,
        image: 'assets/airpods-3.png',
        shortDesc: 'ANC Mode | High Fidelity Sound',
        colours: [{ name: 'Standard', image: 'assets/airpods-3.png' }]
      }
    ]
  };

  var catalog = FALLBACK;
  var cart = loadCart();

  /* ---------------- catalogue ---------------- */

  function findProduct(sku) {
    for (var i = 0; i < catalog.products.length; i++) {
      if (catalog.products[i].sku === sku) return catalog.products[i];
    }
    return null;
  }

  function colourImage(product, colourName) {
    if (product && product.colours) {
      for (var i = 0; i < product.colours.length; i++) {
        if (product.colours[i].name === colourName) return product.colours[i].image;
      }
    }
    return product ? product.image : '';
  }

  function hasManyColours(product) {
    return !!(product && product.colours && product.colours.length > 1);
  }

  function refreshCatalog() {
    if (typeof fetch !== 'function') return;
    fetch('/products.json', { cache: 'no-store' })
      .then(function (res) {
        if (!res.ok) throw new Error('catalogue unavailable');
        return res.json();
      })
      .then(function (data) {
        if (data && Array.isArray(data.products) && data.products.length) {
          catalog = data;
          cart = sanitiseCart(cart);
          saveCart();
          renderCart();
        }
      })
      .catch(function () {
        /* Keep the embedded fallback catalogue. */
      });
  }

  /* ---------------- cart storage ---------------- */

  function sanitiseCart(lines) {
    var seen = {};
    var out = [];
    (lines || []).forEach(function (line) {
      if (!line || typeof line.sku !== 'string') return;
      var product = findProduct(line.sku);
      if (!product) return;
      var colour = line.colour;
      var validColour = false;
      if (product.colours) {
        for (var i = 0; i < product.colours.length; i++) {
          if (product.colours[i].name === colour) validColour = true;
        }
      }
      if (!validColour) colour = product.colours && product.colours[0] ? product.colours[0].name : 'Standard';
      var qty = parseInt(line.qty, 10);
      if (isNaN(qty) || qty < 1) qty = 1;
      if (qty > MAX_QTY) qty = MAX_QTY;
      var key = line.sku + '|' + colour;
      if (seen[key] !== undefined) {
        out[seen[key]].qty = Math.min(MAX_QTY, out[seen[key]].qty + qty);
      } else {
        seen[key] = out.length;
        out.push({ sku: line.sku, colour: colour, qty: qty });
      }
    });
    return out;
  }

  function loadCart() {
    try {
      var raw = window.localStorage.getItem(CART_KEY);
      if (!raw) return [];
      return sanitiseCart(JSON.parse(raw));
    } catch (e) {
      return [];
    }
  }

  function saveCart() {
    try {
      window.localStorage.setItem(CART_KEY, JSON.stringify(cart));
    } catch (e) {
      /* Storage unavailable (private mode) — cart still works in memory. */
    }
  }

  function cartCount() {
    var n = 0;
    cart.forEach(function (line) { n += line.qty; });
    return n;
  }

  function formatMoney(n) {
    return 'Rs.' + Number(n || 0).toLocaleString('en-US');
  }

  function getCartDetailed() {
    var lines = [];
    var subtotal = 0;
    cart.forEach(function (line) {
      var product = findProduct(line.sku);
      if (!product) return;
      var lineTotal = product.price * line.qty;
      subtotal += lineTotal;
      lines.push({
        sku: line.sku,
        name: product.name,
        colour: line.colour,
        image: colourImage(product, line.colour),
        unitPrice: product.price,
        qty: line.qty,
        lineTotal: lineTotal,
        showColour: hasManyColours(product)
      });
    });
    var deliveryFee = catalog.settings && typeof catalog.settings.deliveryFee === 'number'
      ? catalog.settings.deliveryFee : 0;
    return { lines: lines, subtotal: subtotal, deliveryFee: deliveryFee, total: subtotal + deliveryFee };
  }

  function addToCart(sku, qty, colour) {
    var product = findProduct(sku);
    if (!product) return false;
    var wanted = parseInt(qty, 10);
    if (isNaN(wanted) || wanted < 1) wanted = 1;
    if (wanted > MAX_QTY) wanted = MAX_QTY;
    var colourName = colour || (product.colours && product.colours[0] ? product.colours[0].name : 'Standard');
    var merged = false;
    cart.forEach(function (line) {
      if (line.sku === sku && line.colour === colourName) {
        line.qty = Math.min(MAX_QTY, line.qty + wanted);
        merged = true;
      }
    });
    if (!merged) cart.push({ sku: sku, colour: colourName, qty: wanted });
    saveCart();
    renderCart();
    return true;
  }

  function setQty(index, qty) {
    var line = cart[index];
    if (!line) return;
    var wanted = parseInt(qty, 10);
    if (isNaN(wanted)) return;
    if (wanted < 1) {
      cart.splice(index, 1);
    } else {
      line.qty = Math.min(MAX_QTY, wanted);
    }
    saveCart();
    renderCart();
  }

  function removeLine(index) {
    if (cart[index]) {
      cart.splice(index, 1);
      saveCart();
      renderCart();
    }
  }

  function clearCart() {
    cart = [];
    saveCart();
    renderCart();
  }

  /* ---------------- drawer rendering ---------------- */

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  function closeDrawer() {
    if (typeof window.closeCart === 'function') {
      window.closeCart();
      return;
    }
    var drawer = document.getElementById('cartDrawer');
    var overlay = document.getElementById('overlay');
    if (drawer) drawer.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  function isHomePage() {
    var path = window.location.pathname || '';
    return path === '/' || path.endsWith('/') || path.endsWith('index.html');
  }

  function renderCart() {
    /* Header badge (every page has #cartCount). */
    var badges = document.querySelectorAll('#cartCount, [data-cart-count]');
    badges.forEach(function (badge) { badge.textContent = String(cartCount()); });

    var drawer = document.getElementById('cartDrawer');
    if (!drawer) return;
    var body = drawer.querySelector('.cart-body');
    if (!body) return;

    var detailed = getCartDetailed();

    /* Replace the drawer body with the real lines (or the empty state). */
    body.innerHTML = '';
    body.classList.toggle('zn-has-items', detailed.lines.length > 0);

    if (!detailed.lines.length) {
      var empty = el('div', 'zn-cart-empty');
      empty.appendChild(el('div', 'zn-empty-icon', '🛍️'));
      empty.appendChild(el('h4', null, 'Your cart is empty'));
      empty.appendChild(el('p', null, 'Explore our wireless earbuds collection and find your sound.'));
      var link = el('a', 'zn-continue-btn', 'View Collection');
      link.href = isHomePage() ? '#earbuds' : 'index.html#earbuds';
      link.addEventListener('click', function () { closeDrawer(); });
      empty.appendChild(link);
      body.appendChild(empty);
    } else {
      detailed.lines.forEach(function (line, index) {
        var row = el('div', 'zn-cart-line');

        var img = document.createElement('img');
        img.className = 'zn-cart-line-img';
        img.src = line.image;
        img.alt = line.name;
        img.loading = 'lazy';
        row.appendChild(img);

        var info = el('div', 'zn-cart-line-info');
        info.appendChild(el('div', 'zn-cart-line-name', line.name));
        if (line.showColour) info.appendChild(el('div', 'zn-cart-line-meta', 'Colour: ' + line.colour));
        info.appendChild(el('div', 'zn-cart-line-meta', formatMoney(line.unitPrice) + ' each'));

        var controls = el('div', 'zn-cart-line-row');
        var dec = el('button', 'zn-qty-btn', '−');
        dec.type = 'button';
        dec.setAttribute('aria-label', 'Decrease quantity');
        dec.addEventListener('click', function () { setQty(index, line.qty - 1); });
        var qtyText = el('span', 'zn-qty-text', String(line.qty));
        var inc = el('button', 'zn-qty-btn', '+');
        inc.type = 'button';
        inc.setAttribute('aria-label', 'Increase quantity');
        inc.addEventListener('click', function () { setQty(index, line.qty + 1); });
        var total = el('span', 'zn-cart-line-total', formatMoney(line.lineTotal));
        var stepper = el('span', 'zn-stepper');
        stepper.appendChild(dec);
        stepper.appendChild(qtyText);
        stepper.appendChild(inc);
        controls.appendChild(stepper);
        controls.appendChild(total);
        info.appendChild(controls);
        row.appendChild(info);

        var remove = el('button', 'zn-remove-btn', '×');
        remove.type = 'button';
        remove.setAttribute('aria-label', 'Remove ' + line.name + ' from cart');
        remove.addEventListener('click', function () { removeLine(index); });
        row.appendChild(remove);

        body.appendChild(row);
      });
    }

    /* Footer: reuse the product page's #cartFooter when present, otherwise
       create one. The footer only shows when the cart has items. */
    var footer = document.getElementById('cartFooter');
    if (!footer) {
      footer = document.getElementById('znCartFooter');
      if (!footer) {
        footer = el('div', 'zn-cart-footer');
        footer.id = 'znCartFooter';
        drawer.appendChild(footer);
      }
      footer.innerHTML = '';
      var subLine = el('div', 'zn-subtotal-line');
      var itemCount = cartCount();
      subLine.appendChild(el('span', null, 'Subtotal (' + itemCount + ' item' + (itemCount === 1 ? '' : 's') + ')'));
      subLine.appendChild(el('span', null, formatMoney(detailed.subtotal)));
      footer.appendChild(subLine);
      footer.appendChild(el('div', 'zn-footer-note', '🚚 Free shipping across Pakistan \u00B7 Cash on Delivery'));
      var checkoutLink = el('a', 'zn-checkout-btn', 'Checkout (Cash on Delivery)');
      checkoutLink.href = 'checkout.html';
      footer.appendChild(checkoutLink);
      var cont = el('button', 'zn-continue-btn', 'Continue Shopping');
      cont.type = 'button';
      cont.addEventListener('click', function () { closeDrawer(); });
      footer.appendChild(cont);
    } else {
      /* Product page footer: keep its markup, but make checkout a real link
         to checkout.html instead of the old fake-order alert button. */
      var subtotalText = document.getElementById('cartSubtotalText');
      if (subtotalText) subtotalText.textContent = formatMoney(detailed.subtotal);
      var oldBtn = footer.querySelector('button.btn-checkout-now');
      if (oldBtn) {
        var link = document.createElement('a');
        link.className = oldBtn.className;
        link.href = 'checkout.html';
        link.textContent = 'Checkout (Cash on Delivery)';
        oldBtn.replaceWith(link);
      }
      var footerLink = footer.querySelector('a.btn-checkout-now');
      if (footerLink) footerLink.href = 'checkout.html';
      if (!footer.querySelector('.zn-footer-note')) {
        var pNote = el('div', 'zn-footer-note', '🚚 Free shipping across Pakistan \u00B7 Cash on Delivery');
        if (footerLink) footer.insertBefore(pNote, footerLink); else footer.appendChild(pNote);
      }
    }

    footer.style.display = detailed.lines.length ? '' : 'none';
    if (footer.id === 'cartFooter') footer.style.display = detailed.lines.length ? 'block' : 'none';
  }

  function injectStyles() {
    if (document.getElementById('zn-shared-styles')) return;
    var style = document.createElement('style');
    style.id = 'zn-shared-styles';
    style.textContent = [
      '.zn-skip-link{position:absolute;left:-9999px;top:auto;width:1px;height:1px;overflow:hidden}',
      '.zn-skip-link:focus{position:fixed;left:16px;top:16px;width:auto;height:auto;padding:12px 18px;background:#111;color:#fff !important;border-radius:10px;z-index:9999;font-size:14px;font-weight:700;text-decoration:none}',
      '.cart-body.zn-has-items{display:block;text-align:left;padding:8px 20px 20px;overflow-y:auto}',
      '.zn-cart-empty{text-align:center;padding:48px 10px}',
      '.zn-empty-icon{font-size:40px;margin-bottom:12px}',
      '.zn-cart-empty h4{font-size:16px;font-weight:700;margin-bottom:6px;color:#111}',
      '.zn-cart-empty p{font-size:13px;color:#6b7280}',
      '.zn-cart-line{display:flex;gap:14px;padding:18px 0;border-bottom:1px solid #f0f0f0;align-items:flex-start;text-align:left}',
      '.zn-cart-line:last-child{border-bottom:0}',
      '.zn-cart-line-img{width:76px;height:76px;object-fit:contain;background:#f6f7f8;border:1px solid #f0f0f0;border-radius:12px;padding:6px;box-sizing:border-box;flex-shrink:0}',
      '.zn-cart-line-info{flex:1;min-width:0}',
      '.zn-cart-line-name{font-size:15px;font-weight:700;color:#111;line-height:1.35}',
      '.zn-cart-line-meta{font-size:13px;color:#6b7280;margin-top:3px}',
      '.zn-cart-line-row{display:flex;align-items:center;gap:10px;margin-top:12px}',
      '.zn-stepper{display:inline-flex;align-items:center;border:1px solid #e5e7eb;border-radius:999px;background:#fff;overflow:hidden}',
      '.zn-qty-btn{width:44px;height:44px;border:0;background:transparent;font-size:20px;line-height:1;cursor:pointer;color:#111}',
      '.zn-qty-btn:active{background:#f3f4f6}',
      '.zn-qty-text{min-width:30px;text-align:center;font-size:14px;font-weight:700;color:#111}',
      '.zn-cart-line-total{margin-left:auto;font-size:15px;font-weight:800;color:#111;white-space:nowrap}',
      '.zn-remove-btn{border:0;background:none;font-size:20px;line-height:1;color:#9ca3af;cursor:pointer;padding:12px 14px;flex-shrink:0;margin-top:-10px;margin-right:-12px}',
      '.zn-remove-btn:active{color:#111}',
      '.zn-cart-footer{padding:16px 16px 20px;border-top:1px solid #eee;background:#fff}',
      '.zn-subtotal-line{display:flex;justify-content:space-between;font-size:15px;font-weight:700;color:#111;margin-bottom:8px}',
      '.zn-footer-note{font-size:12.5px;color:#6b7280;text-align:center;margin:0 0 12px}',
      '.zn-checkout-btn{display:flex;align-items:center;justify-content:center;min-height:48px;padding:0 20px;border-radius:999px;background:#111;color:#fff !important;font-size:13px;font-weight:700;text-decoration:none;width:100%;box-sizing:border-box}',
      '.zn-continue-btn{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:0 22px;border-radius:999px;background:#fff;color:#111 !important;border:1px solid rgba(0,0,0,.12);font-size:12.5px;font-weight:600;text-decoration:none;cursor:pointer;margin-top:12px}',
      '.zn-cart-footer .zn-continue-btn{width:100%;box-sizing:border-box}',
      '#cartFooter{padding:16px;border-top:1px solid #eee;background:#fff}',
      '#cartFooter .cart-subtotal-line{display:flex;justify-content:space-between;font-size:15px;font-weight:700;color:#111;margin-bottom:8px}',
      '.zn-form-status{font-size:13px;margin-top:8px;color:#111}',
      '.zn-form-status.is-error{color:#b91c1c}',
      '#znSearchNote{margin:0 0 20px;padding:14px 16px;border:1px solid #eee;border-radius:12px;background:#f8f9fa;font-size:14px;color:#111;display:flex;gap:12px;align-items:center;flex-wrap:wrap}',
      '#znSearchNote button{margin-left:auto;border:1px solid #d1d5db;background:#fff;border-radius:999px;padding:6px 14px;font-size:12.5px;font-weight:600;cursor:pointer;color:#111}'
    ].join('\n');
    document.head.appendChild(style);
  }

  /* ---------------- newsletter ---------------- */

  function wireNewsletter() {
    var form = document.getElementById('contact_form');
    if (!form || form.dataset.znWired) return;
    form.dataset.znWired = '1';
    var input = form.querySelector('input[type="email"]');
    var button = form.querySelector('button[type="submit"], button');
    var status = document.createElement('p');
    status.className = 'zn-form-status';
    status.setAttribute('role', 'status');
    status.style.display = 'none';
    form.insertAdjacentElement('afterend', status);

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var email = input ? input.value.trim() : '';
      status.style.display = 'none';
      status.classList.remove('is-error');
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        status.textContent = 'Please enter a valid email address.';
        status.classList.add('is-error');
        status.style.display = '';
        return;
      }
      var originalText = button ? button.textContent : '';
      if (button) {
        button.disabled = true;
        button.textContent = 'Sending...';
      }
      fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
      })
        .then(function (res) { return res.json().then(function (data) { return { ok: res.ok, data: data }; }); })
        .then(function (result) {
          if (result.ok) {
            status.textContent = result.data && result.data.already
              ? 'You are already subscribed. Thank you!'
              : 'Thank you! You are subscribed.';
            status.style.display = '';
            form.reset();
          } else {
            status.textContent = (result.data && result.data.error) || 'Could not subscribe. Please try again.';
            status.classList.add('is-error');
            status.style.display = '';
          }
        })
        .catch(function () {
          status.textContent = 'Could not subscribe right now. Please try again later.';
          status.classList.add('is-error');
          status.style.display = '';
        })
        .finally(function () {
          if (button) {
            button.disabled = false;
            button.textContent = originalText;
          }
        });
    });
  }

  /* ---------------- search ---------------- */

  function productCards() {
    var section = document.getElementById('earbuds');
    if (!section) return [];
    return Array.prototype.slice.call(section.querySelectorAll('.th-product-card'));
  }

  function clearSearchNote() {
    var note = document.getElementById('znSearchNote');
    if (note) note.remove();
  }

  function showSearchNote(message, query) {
    var section = document.getElementById('earbuds');
    if (!section) return;
    clearSearchNote();
    var note = document.createElement('div');
    note.id = 'znSearchNote';
    var text = document.createElement('span');
    text.textContent = message;
    note.appendChild(text);
    var clear = document.createElement('button');
    clear.type = 'button';
    clear.textContent = 'Clear search';
    clear.addEventListener('click', function () {
      var input = document.getElementById('searchInput');
      if (input) input.value = '';
      applySearch('', { scroll: false });
    });
    note.appendChild(clear);
    var container = section.querySelector('.container') || section;
    var wrapper = section.querySelector('.products-carousel-wrapper');
    if (wrapper && wrapper.parentNode === container) {
      container.insertBefore(note, wrapper.nextSibling);
    } else {
      container.appendChild(note);
    }
  }

  function applySearch(query, options) {
    var q = (query || '').trim().toLowerCase();
    var cards = productCards();
    if (!cards.length) {
      /* No catalogue on this page — search on the homepage instead. */
      if (q) window.location.href = 'index.html?q=' + encodeURIComponent(q);
      return;
    }
    var matches = 0;
    cards.forEach(function (card) {
      var haystack = (card.textContent || '').toLowerCase();
      var img = card.querySelector('img');
      if (img && img.alt) haystack += ' ' + img.alt.toLowerCase();
      var show = !q || haystack.indexOf(q) !== -1;
      card.style.display = show ? '' : 'none';
      if (show) matches++;
    });
    if (!q) {
      clearSearchNote();
    } else if (matches) {
      showSearchNote('Showing ' + matches + ' result' + (matches === 1 ? '' : 's') + ' for "' + query.trim() + '"', q);
    } else {
      showSearchNote('No products found for "' + query.trim() + '". Try another keyword.', q);
    }
    if (!options || options.scroll !== false) {
      var section = document.getElementById('earbuds');
      if (section) section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function wireSearch() {
    var input = document.getElementById('searchInput');
    if (!input || input.dataset.znWired) return;
    input.dataset.znWired = '1';
    input.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter') return;
      e.preventDefault();
      /* Stop the page's own scroll-only search handler from also running. */
      if (typeof e.stopImmediatePropagation === 'function') e.stopImmediatePropagation();
      var panel = document.getElementById('searchPanel');
      if (panel) panel.classList.remove('active');
      applySearch(input.value, { scroll: true });
    });
  }

  function applyQueryFromUrl() {
    try {
      var params = new URLSearchParams(window.location.search);
      var q = params.get('q');
      if (!q) return;
      if (!productCards().length) return;
      var input = document.getElementById('searchInput');
      if (input) input.value = q;
      applySearch(q, { scroll: true });
    } catch (e) {
      /* Ignore malformed query strings. */
    }
  }

  /* ---------------- init ---------------- */

  function init() {
    injectStyles();
    renderCart();
    wireNewsletter();
    wireSearch();
    applyQueryFromUrl();
    refreshCatalog();
    window.addEventListener('storage', function (e) {
      if (e.key === CART_KEY) {
        cart = loadCart();
        renderCart();
      }
    });
  }

  window.Zeronic = {
    addToCart: addToCart,
    getCart: function () { return cart.slice(); },
    getCartDetailed: getCartDetailed,
    getCatalog: function () { return catalog; },
    setQty: setQty,
    removeLine: removeLine,
    clearCart: clearCart,
    renderCart: renderCart,
    applySearch: applySearch,
    formatMoney: formatMoney
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
