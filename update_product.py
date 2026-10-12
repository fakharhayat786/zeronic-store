import re

with open('product.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Rename 'TH Flex Earbuds' to 'ZERONIC Flex Earbuds' and 'TH Flex' to 'ZERONIC Flex'
html = html.replace('<h1>TH Flex Earbuds</h1>', '<h1>ZERONIC Flex Earbuds</h1>')
html = html.replace('<title>TH Flex Earbuds', '<title>ZERONIC Flex Earbuds')
html = html.replace('TH Flex Earbuds', 'ZERONIC Flex Earbuds')
html = html.replace('1x TH Flex,', '1x ZERONIC Flex,')

# 2. Add proper Review Modal Overlay CSS in <style>
modal_css = """
    /* Review Modal Dialog */
    .th-modal-dialog {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.65);
      -webkit-backdrop-filter: blur(6px);
      backdrop-filter: blur(6px);
      z-index: 99999;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }
    .th-modal-dialog.open {
      display: flex !important;
    }
    .th-modal-box {
      background: #ffffff;
      border-radius: 20px;
      max-width: 480px;
      width: 100%;
      padding: 24px;
      position: relative;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
      border: 1px solid rgba(0, 0, 0, 0.08);
    }
"""

# 3. New Refined Brand-Aligned MMC (Sticky Add to Cart) Styles
new_mmc_css = """
    /* =========================================================
       BRAND-ALIGNED STICKY ADD TO CART BAR (MMC)
    ========================================================= */
    #mobile-mini-cta {
      display: none;
    }
    @media (max-width: 767px) {
      .mmc {
        position: fixed;
        left: 12px;
        right: 12px;
        bottom: 14px;
        z-index: 10000;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.95);
        -webkit-backdrop-filter: blur(20px);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 98, 216, 0.15);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.14), 0 2px 6px rgba(0, 0, 0, 0.05);
        color: #111111;
        transform: translateY(140%);
        opacity: 0;
        pointer-events: none;
        transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
        display: block !important;
      }
      .mmc.mmc--show {
        transform: translateY(0);
        opacity: 1;
        pointer-events: auto;
      }
      .mmc__content {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 10px 8px 18px;
      }
      .mmc__info {
        flex: 1 1 auto;
        min-width: 0;
      }
      .mmc__title {
        font-family: 'Inter', -apple-system, sans-serif;
        font-weight: 700;
        font-size: 13px;
        line-height: 1.2;
        color: #111111;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 2px;
      }
      .mmc__price {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 13.5px;
        color: #0062d8;
        display: flex;
        align-items: baseline;
        gap: 6px;
      }
      .mmc__price s {
        color: #9ca3af;
        font-weight: 500;
        font-size: 11.5px;
        text-decoration: line-through;
      }
      .mmc__divider {
        width: 1px;
        height: 24px;
        background: rgba(0, 0, 0, 0.1);
        display: block;
      }
      .mmc__btn {
        flex: 0 0 auto;
        border: 0;
        border-radius: 999px;
        padding: 10px 20px;
        background: #0062d8;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 0.01em;
        box-shadow: 0 4px 14px rgba(0, 98, 216, 0.35);
        cursor: pointer;
        transition: background 0.2s ease, transform 0.15s ease;
      }
      .mmc__btn:active {
        transform: scale(0.97);
        background: #004eb0;
      }
    }
"""

# Replace old MMC block
old_mmc_start = html.find('/* =========================================================\n       MOBILE MINI BOTTOM CTA BAR')
old_mmc_end = html.find('/* =========================================================\n       FOOTER')
if old_mmc_start != -1 and old_mmc_end != -1:
    html = html[:old_mmc_start] + new_mmc_css.strip() + '\n\n' + html[old_mmc_end:]

# Insert modal CSS before responsive breakpoints
resp_marker = '/* =========================================================\n       RESPONSIVE BREAKPOINTS'
if resp_marker in html:
    html = html.replace(resp_marker, modal_css.strip() + '\n\n    ' + resp_marker)

# 4. Enhance Mobile CSS:
mobile_fixes = """
    /* =========================================================
       SPECIFIC MOBILE SCREEN OPTIMIZATIONS (Up to 768px)
    ========================================================= */
    @media (max-width: 768px) {
      /* Gallery Image & Frame containment */
      .gallery-main-frame {
        aspect-ratio: 1 / 1;
        max-height: 380px;
        margin: 0 auto;
      }
      .gallery-main-img {
        padding: 16px;
        max-height: 340px;
        width: 100%;
        height: 100%;
        object-fit: contain;
      }
      .gallery-thumbs-row {
        justify-content: center;
        gap: 8px;
        margin-top: 10px;
      }
      .th-thumb-item {
        flex: 0 0 64px;
        height: 64px;
      }

      /* Feature strip (ANC, EQ, Gaming, Leather) 4 columns compact */
      .th-fstrip__card {
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 2px !important;
        padding: 10px 4px !important;
      }
      .th-fstrip__item {
        padding: 2px !important;
      }
      .th-fstrip__icon svg {
        width: 20px;
        height: 20px;
      }
      .th-fstrip__title {
        font-size: 11px !important;
      }
      .th-fstrip__sub {
        font-size: 9px !important;
      }

      /* Buttons - Always visible and distinct */
      .th-btn-group {
        display: flex !important;
        flex-direction: column !important;
        gap: 10px !important;
        margin: 16px 0 !important;
        visibility: visible !important;
        opacity: 1 !important;
      }
      .th-add-to-cart-btn {
        display: flex !important;
        width: 100% !important;
        padding: 14px 20px !important;
        background: #ffffff !important;
        color: #0062d8 !important;
        border: 2px solid #0062d8 !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        border-radius: 999px !important;
        box-shadow: 0 2px 8px rgba(0, 98, 216, 0.08) !important;
      }
      .th-buy-now-btn {
        display: flex !important;
        width: 100% !important;
        padding: 14px 20px !important;
        background: #0062d8 !important;
        color: #ffffff !important;
        border: 0 !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        border-radius: 999px !important;
        box-shadow: 0 4px 14px rgba(0, 98, 216, 0.35) !important;
      }

      /* WhatsApp float elevation so it does not collide with MMC */
      .whatsapp-float {
        bottom: 84px !important;
        right: 16px !important;
        width: 48px !important;
        height: 48px !important;
      }
      .whatsapp-float svg {
        width: 24px !important;
        height: 24px !important;
      }
    }
"""

# Append mobile fixes right before </style>
html = html.replace('</style>', mobile_fixes.strip() + '\n  </style>')

with open('product.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated product.html successfully!')
