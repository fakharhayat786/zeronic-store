with open('product.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. REMOVE REVIEWS: Zeeshan & Ahwazazeem
# In fullReviewsGrid:
# Find each card by looking for Zeeshan and Ahwazazeem
def remove_card_containing(content, keyword):
    idx = content.find(keyword)
    if idx == -1:
        return content
    # Find enclosing <article ... </article> or <div class="th-review-card" ... </div>
    art_start = content.rfind('<article class="th-full-rev-card">', 0, idx)
    if art_start != -1:
        art_end = content.find('</article>', idx)
        if art_end != -1:
            return content[:art_start] + content[art_end + len('</article>'):]
    card_start = content.rfind('<div class="th-review-card">', 0, idx)
    if card_start != -1:
        card_end = content.find('</div>\n            </div>', idx)
        if card_end == -1:
            card_end = content.find('</div>', idx + 10)
        # Let's search for closing of review-card:
        # It ends with - Zeeshan</div>\n            </div>
        dash_pos = content.find('- ' + keyword, idx)
        if dash_pos != -1:
            end_tag = content.find('</div>', dash_pos) + len('</div>')
            # and closing card </div>
            end_card = content.find('</div>', end_tag) + len('</div>')
            return content[:card_start] + content[end_card:]
    return content

# Remove Zeeshan and Ahwazazeem from both places
while 'Zeeshan' in html:
    pos = html.find('Zeeshan')
    art_start = html.rfind('<article class="th-full-rev-card">', 0, pos)
    if art_start != -1 and pos - art_start < 400:
        art_end = html.find('</article>', pos) + len('</article>')
        html = html[:art_start] + html[art_end:]
        continue
    card_start = html.rfind('<div class="th-review-card">', 0, pos)
    if card_start != -1 and pos - card_start < 600:
        dash_pos = html.find('- Zeeshan', pos)
        div1 = html.find('</div>', dash_pos) + len('</div>')
        div2 = html.find('</div>', div1) + len('</div>')
        html = html[:card_start] + html[div2:]
        continue
    break

while 'Ahwazazeem' in html:
    pos = html.find('Ahwazazeem')
    art_start = html.rfind('<article class="th-full-rev-card">', 0, pos)
    if art_start != -1 and pos - art_start < 400:
        art_end = html.find('</article>', pos) + len('</article>')
        html = html[:art_start] + html[art_end:]
        continue
    card_start = html.rfind('<div class="th-review-card">', 0, pos)
    if card_start != -1 and pos - card_start < 600:
        dash_pos = html.find('- Ahwazazeem', pos)
        div1 = html.find('</div>', dash_pos) + len('</div>')
        div2 = html.find('</div>', div1) + len('</div>')
        html = html[:card_start] + html[div2:]
        continue
    break

print('Removed Zeeshan and Ahwazazeem reviews. Remaining Zeeshan:', 'Zeeshan' in html, 'Ahwazazeem:', 'Ahwazazeem' in html)

# 2. REMOVE YOUTUBE REVIEW SECTION & QUICK VIDEO BUTTON
# Remove quick video button
q_start = html.find('<div class="th-video-review-float">')
if q_start != -1:
    q_end = html.find('</div>', q_start) + len('</div>')
    html = html[:q_start] + html[q_end:]

# Remove YouTube review section
yt_start = html.find('<!-- =========================================================\n       SECTION: YOUTUBE REVIEW')
if yt_start != -1:
    yt_end = html.find('<!-- =========================================================\n       SECTION: PRODUCT SPECIFICATION', yt_start)
    if yt_end != -1:
        html = html[:yt_start] + html[yt_end:]

# 3. REPLACE BENEFITS INFINITE CAROUSEL WITH EXACT HOMEPAGE STATEMENT TICKER BAR
statement_section_html = """  <!-- BRAND STATEMENT TICKER (EXACT HOMEPAGE MATCH) -->
  <section class="statement">
    <div class="container">
      <div class="statement-track">
        <span>PURE SOUND</span>
        <span class="statement-dot"></span>
        <span>PRECISION ENGINEERING</span>
        <span class="statement-dot"></span>
        <span>EVERYDAY ESSENTIAL</span>
        <span class="statement-dot"></span>
        <span>ZERONIC AUDIO</span>
        <span class="statement-dot"></span>
        <span>PURE SOUND</span>
        <span class="statement-dot"></span>
        <span>PRECISION ENGINEERING</span>
        <span class="statement-dot"></span>
        <span>EVERYDAY ESSENTIAL</span>
        <span class="statement-dot"></span>
        <span>ZERONIC AUDIO</span>
      </div>
    </div>
  </section>"""

ben_start = html.find('<!-- =========================================================\n       BENEFITS INFINITE CAROUSEL')
if ben_start != -1:
    ben_end = html.find('<!-- =========================================================\n       STICKY PILL NAVIGATION BAR', ben_start)
    if ben_end != -1:
        html = html[:ben_start] + statement_section_html + '\n\n' + html[ben_end:]

# Statement CSS:
statement_css = """
/* =========================================================
   STATEMENT BAR (Exact Homepage Electric Blue Marquee)
========================================================= */
.statement {
  padding: 14px 0;
  background: linear-gradient(135deg, #0062d8 0%, #004eb0 100%);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  position: relative;
  display: flex;
  align-items: center;
}

.statement-track {
  display: flex;
  white-space: nowrap;
  gap: 40px;
  font-family: "Poppins", "Inter", sans-serif;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #ffffff;
  animation: dynamic-marquee-fast 10s linear infinite;
  will-change: transform;
}

.statement-dot {
  align-self: center;
  width: 5px;
  height: 5px;
  background: #ffffff;
  border-radius: 50%;
  opacity: 0.8;
  flex-shrink: 0;
}

@keyframes dynamic-marquee-fast {
  0% {
    transform: translate3d(0, 0, 0);
  }
  100% {
    transform: translate3d(-50%, 0, 0);
  }
}
"""

if '.statement {' not in html:
    html = html.replace('/* =========================================================\n       STICKY PILL NAVIGATION BAR', statement_css.strip() + '\n\n/* =========================================================\n       STICKY PILL NAVIGATION BAR')

# 4. FIX BUTTONS & SWATCHES TO MATCH EXACT SCREENSHOT 6
# Swatches with rounded circular images
swatch_block_start = html.find('<div class="th-swatches-grid">')
if swatch_block_start != -1:
    swatch_block_end = html.find('</div>\n        </div>', swatch_block_start) + len('</div>\n        </div>')
    new_swatches = """<div class="th-swatches-grid">
            <button type="button" class="th-swatch-input th-swatch-circle-btn active" data-color="Flex Black" data-img="assets/airpods-1.png" aria-label="Flex Black">
              <img src="assets/airpods-1.png" alt="Flex Black" />
            </button>
            <button type="button" class="th-swatch-input th-swatch-circle-btn" data-color="Flex White" data-img="assets/airpods-2.png" aria-label="Flex White">
              <img src="assets/airpods-2.png" alt="Flex White" />
            </button>
          </div>
        </div>"""
    html = html[:swatch_block_start] + new_swatches + html[swatch_block_end:]

# Update button text to make sure the text is crisp and clean
btn_css = """
    /* EXACT SCREENSHOT MATCH FOR CTA BUTTONS & SWATCHES */
    .th-swatches-grid {
      display: flex !important;
      gap: 14px !important;
      align-items: center !important;
      margin-top: 6px !important;
    }
    .th-swatch-circle-btn {
      width: 46px !important;
      height: 46px !important;
      border-radius: 50% !important;
      border: 2px solid #e5e7eb !important;
      background: #ffffff !important;
      padding: 3px !important;
      cursor: pointer !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      transition: all 0.2s ease !important;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06) !important;
    }
    .th-swatch-circle-btn img {
      width: 100% !important;
      height: 100% !important;
      object-fit: contain !important;
      border-radius: 50% !important;
    }
    .th-swatch-circle-btn.active {
      border-color: #0062d8 !important;
      box-shadow: 0 0 0 2px rgba(0, 98, 216, 0.3) !important;
    }

    .th-btn-group {
      display: flex !important;
      flex-direction: column !important;
      gap: 12px !important;
      margin: 22px 0 18px !important;
      width: 100% !important;
    }
    .th-add-to-cart-btn {
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      width: 100% !important;
      padding: 16px 24px !important;
      background: #ffffff !important;
      color: #0062d8 !important;
      border: 2px solid #0062d8 !important;
      font-family: 'Inter', -apple-system, sans-serif !important;
      font-size: 15px !important;
      font-weight: 700 !important;
      border-radius: 999px !important;
      cursor: pointer !important;
      box-shadow: 0 2px 8px rgba(0, 98, 216, 0.08) !important;
      transition: all 0.2s ease !important;
    }
    .th-add-to-cart-btn span {
      color: #0062d8 !important;
      font-size: 15px !important;
      font-weight: 700 !important;
    }
    .th-add-to-cart-btn:hover {
      background: #eff6ff !important;
      transform: translateY(-1px) !important;
    }
    .th-buy-now-btn {
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      width: 100% !important;
      padding: 16px 24px !important;
      background: #0062d8 !important;
      color: #ffffff !important;
      border: 0 !important;
      font-family: 'Inter', -apple-system, sans-serif !important;
      font-size: 15px !important;
      font-weight: 700 !important;
      border-radius: 999px !important;
      cursor: pointer !important;
      box-shadow: 0 4px 16px rgba(0, 98, 216, 0.35) !important;
      transition: all 0.2s ease !important;
    }
    .th-buy-now-btn span {
      color: #ffffff !important;
      font-size: 15px !important;
      font-weight: 700 !important;
    }
    .th-buy-now-btn:hover {
      background: #004eb0 !important;
      box-shadow: 0 6px 22px rgba(0, 98, 216, 0.45) !important;
      transform: translateY(-1px) !important;
    }
"""

html = html.replace('</style>', btn_css.strip() + '\n  </style>')

with open('product.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated product.html successfully!')
