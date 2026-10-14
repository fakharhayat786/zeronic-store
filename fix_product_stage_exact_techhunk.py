with open('product.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Clean out the conflicting USER EDIT style blocks that forced centering
# Let's locate the user-added MASTER FIX at the top (lines 26-125) and bottom
import re

# Remove top MASTER FIX block if present
html = re.sub(r'/\* =+.*?MASTER FIX: TECH HUNK EDGE-TO-EDGE & CENTER ALIGNMENT.*?\*/\s*html, body \{.*?@media screen and \(max-width: 749px\) \{.*?\}\s*\}', '', html, flags=re.DOTALL)

# Remove duplicate / lingering rules that center .th-product-title-wrap, .product-info-column, etc.
html = re.sub(r'\.th-product-title-wrap,\s*\.product__title,\s*\.product-info-column.*?width: 100% !important;\s*\}', '', html, flags=re.DOTALL)

# Remove the bottom patch style block if present
html = re.sub(r'/\* Tech Hunk Ultimate Mobile Core Alignment Patch Integration Rules \*/\s*<style>.*?</style>', '', html, flags=re.DOTALL)

# 2. Tech Hunk Exact Stage Styling
techhunk_stage_css = """
/* =========================================================
   TECH HUNK EXACT PRODUCT MAIN STAGE (DESKTOP & MOBILE)
========================================================= */
.product-stage-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: start;
  margin-top: 20px;
  margin-bottom: 30px;
}

.product-media-column {
  position: relative;
}

/* Gallery Frame - Tech Hunk has seamless clean white container with rounded corners and no heavy box */
.gallery-main-frame {
  position: relative;
  background: #ffffff;
  border: none;
  box-shadow: none;
  border-radius: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  aspect-ratio: 1 / 1;
}

.gallery-main-img {
  width: 100%;
  height: 100%;
  max-height: 480px;
  object-fit: contain;
  padding: 10px;
}

/* Floating 29% OFF Badge - Pill top right */
.th-top-badge {
  position: absolute;
  top: 14px;
  right: 14px;
  left: auto !important;
  z-index: 10;
  background: #eef5ff;
  color: #0062d8;
  font-family: inherit;
  font-size: 11.5px;
  font-weight: 800;
  padding: 5px 12px;
  border-radius: 999px;
  letter-spacing: 0.02em;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

/* Floating Video Review Red Icon at bottom right of image */
.th-media-video-review {
  position: absolute;
  bottom: 12px;
  right: 12px;
  z-index: 12;
  cursor: pointer;
}
.th-media-video-review svg {
  width: 32px;
  height: 32px;
  filter: drop-shadow(0 2px 6px rgba(0,0,0,0.15));
}

/* 1/6 Navigation counter under image */
.th-counter-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  width: 100%;
  margin: 14px 0 10px;
  font-size: 13px;
  color: #9ca3af;
  font-family: "Manrope", sans-serif;
  font-weight: 500;
}
.th-counter-arrow {
  background: transparent;
  border: none;
  color: #9ca3af;
  font-size: 16px;
  cursor: pointer;
  padding: 0 8px;
  line-height: 1;
  transition: color 0.15s ease;
}
.th-counter-arrow:hover {
  color: #111111;
}

/* LEFT-ALIGNED PRODUCT INFO COLUMN (Tech Hunk Standard) */
.product-info-column {
  display: flex !important;
  flex-direction: column !important;
  text-align: left !important;
  align-items: flex-start !important;
  padding: 0;
  width: 100%;
}

.th-product-title-wrap {
  width: 100%;
  text-align: left !important;
  margin-bottom: 2px;
}

.th-product-title-wrap h1 {
  font-family: "Poppins", "Manrope", sans-serif;
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.15;
  margin: 0;
  letter-spacing: -0.02em;
}

.th-product-subtitle {
  font-size: 11.5px;
  font-weight: 600;
  color: #94a3b8;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin: 6px 0 8px 0;
  text-align: left !important;
  width: 100%;
}

/* Rating Box - Left aligned */
.th-jd-rating-box {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  justify-content: flex-start !important;
  text-align: left !important;
  gap: 6px;
  margin: 4px 0 12px;
  line-height: 1;
  width: 100%;
}
.th-jd-stars {
  color: #f59e0b;
  font-size: 15px;
  letter-spacing: 1px;
}
.th-jd-rating-number {
  font-size: 13.5px;
  font-weight: 700;
  color: #0f172a;
}
.th-jd-review-link {
  font-size: 13.5px;
  font-weight: 600;
  color: #0062d8;
  text-decoration: none;
}

/* Price Bar - Left aligned */
.th-pricebar {
  display: flex !important;
  flex-direction: row !important;
  align-items: baseline !important;
  justify-content: flex-start !important;
  text-align: left !important;
  gap: 12px;
  flex-wrap: wrap;
  margin: 8px 0 16px;
  width: 100%;
}
.th-pricebar .th-price {
  font-weight: 800;
  font-size: 28px;
  line-height: 1;
  color: #0f172a;
  letter-spacing: -0.02em;
}
.th-pricebar .th-compare {
  font-weight: 600;
  font-size: 17px;
  color: #94a3b8;
  text-decoration: line-through;
}
.th-pricebar .th-off {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: #dc2626;
  color: #ffffff;
  font-size: 11.5px;
  font-weight: 800;
  line-height: 1;
  transform: translateY(-2px);
}

/* 4-Column Feature Strip (th-fstrip) - Exactly like Tech Hunk screenshot */
.th-fstrip {
  margin: 6px 0 18px;
  width: 100%;
}
.th-fstrip__card {
  display: grid;
  grid-template-columns: repeat(4, 1fr) !important;
  align-items: stretch;
  background: #ffffff;
  border: 1px solid #f1f5f9;
  border-radius: 16px;
  padding: 14px 6px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
}
.th-fstrip__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 5px;
  padding: 2px 4px;
  position: relative;
}
.th-fstrip__item + .th-fstrip__item::before {
  content: "";
  position: absolute;
  left: 0;
  top: 15%;
  height: 70%;
  width: 1px;
  background: #e2e8f0;
}
.th-fstrip__icon svg {
  width: 22px;
  height: 22px;
  color: #1e293b;
}
.th-fstrip__title {
  font-family: inherit;
  font-weight: 800;
  font-size: 12px;
  color: #0f172a;
  line-height: 1.1;
  letter-spacing: 0.02em;
}
.th-fstrip__sub {
  font-weight: 500;
  font-size: 10px;
  color: #64748b;
  line-height: 1;
  letter-spacing: 0.04em;
}

/* Color: Flex Black text & round circular swatches */
.th-variant-selects {
  width: 100%;
  text-align: left;
  margin-bottom: 16px;
}
.th-variant-label {
  font-size: 12.5px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
  text-align: left !important;
}
.th-swatches-grid {
  display: flex;
  gap: 12px;
  align-items: center;
}
.th-swatch-circle-btn {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 1.5px solid #cbd5e1;
  background: #ffffff;
  padding: 2px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}
.th-swatch-circle-btn img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 50%;
}
.th-swatch-circle-btn.active {
  border-color: #0062d8;
  box-shadow: 0 0 0 2px rgba(0, 98, 216, 0.25);
}

/* Quantity Selector - Centered row with round subtle pill buttons */
#thQtyWrap {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin: 12px 0 16px;
}
.thQtyLabel {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
}
.thQtyBtn {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 15px;
  line-height: 1;
  transition: all 0.15s ease;
}
.thQtyBtn:hover {
  border-color: #64748b;
  color: #0f172a;
}
.thQtyInput {
  width: 26px;
  border: 0;
  background: transparent;
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  color: #475569;
  outline: none;
}

/* Action Buttons - Add to cart (Outlined) & Buy it now (Solid Blue) */
.th-btn-group {
  display: flex !important;
  flex-direction: column !important;
  gap: 12px !important;
  width: 100% !important;
  margin: 4px 0 20px !important;
}
.th-add-to-cart-btn {
  width: 100% !important;
  padding: 14px 20px !important;
  background: #ffffff !important;
  color: #0062d8 !important;
  border: 2px solid #0062d8 !important;
  border-radius: 999px !important;
  font-size: 14px !important;
  font-weight: 700 !important;
  cursor: pointer !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 1px 4px rgba(0, 98, 216, 0.08) !important;
}
.th-add-to-cart-btn:hover {
  background: #f0f7ff !important;
}
.th-buy-now-btn {
  width: 100% !important;
  padding: 15px 20px !important;
  background: #0062d8 !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 999px !important;
  font-size: 14px !important;
  font-weight: 700 !important;
  cursor: pointer !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 4px 14px rgba(0, 98, 216, 0.3) !important;
}
.th-buy-now-btn:hover {
  background: #004eb0 !important;
  box-shadow: 0 6px 20px rgba(0, 98, 216, 0.4) !important;
}

/* Full Width Thin Divider */
.hm-custom-divider {
  display: block !important;
  width: 100% !important;
  height: 0 !important;
  border-top: 1px solid #e2e8f0 !important;
  margin: 18px 0 !important;
}

/* In-Page Review Slider Cards (Exact Tech Hunk Layout) */
.th-jdgm-cards-wrap {
  width: 100%;
  overflow: hidden;
}
.th-review-slider {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  padding-bottom: 8px;
  scrollbar-width: none;
}
.th-review-slider::-webkit-scrollbar {
  display: none;
}
.th-review-card {
  flex: 0 0 210px;
  min-height: 180px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px 14px;
  scroll-snap-align: start;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
}
.th-review-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.th-review-img {
  width: 44px;
  height: 44px;
  object-fit: contain;
  flex-shrink: 0;
}
.th-review-top h3 {
  font-size: 12px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 2px;
  line-height: 1.2;
}
.th-stars-micro {
  color: #f59e0b;
  font-size: 11px;
}
.th-verified-micro {
  color: #16a34a;
  font-size: 10px;
  font-weight: 600;
}
.th-review-text {
  font-size: 11px;
  color: #475569;
  line-height: 1.4;
  margin: 4px 0 0;
}
.th-review-footer {
  font-size: 10px;
  color: #94a3b8;
  margin-top: auto;
  padding-top: 8px;
}

/* Dots indicator under in-page reviews */
.th-inpage-dots {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 10px;
}
.th-inpage-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #cbd5e1;
}
.th-inpage-dot.active {
  background: #64748b;
}

@media (max-width: 768px) {
  .product-stage-grid {
    grid-template-columns: 1fr;
    gap: 16px;
    margin-top: 8px;
  }
  .gallery-main-img {
    max-height: 340px;
    padding: 0;
  }
  .gallery-thumbs-row {
    display: none !important; /* Tech Hunk hides small thumbnails on mobile in favor of the < 1/6 > dial */
  }
  .th-product-title-wrap h1 {
    font-size: 26px;
  }
}
"""

# Replace existing stage CSS
stage_marker = '/* =========================================================\n       TECH HUNK PRODUCT MAIN STAGE'
if stage_marker in html:
    end_marker = '/* =========================================================\n       TECH HUNK BENEFITS'
    if end_marker in html:
        s_pos = html.find(stage_marker)
        e_pos = html.find(end_marker)
        html = html[:s_pos] + techhunk_stage_css.strip() + '\n\n    ' + html[e_pos:]

# 3. Update the HTML Markup in .product-stage-grid
# Replace Media Gallery and Info column with exact Tech Hunk architecture
old_stage_start = html.find('<!-- LEFT: MEDIA GALLERY -->')
old_stage_end = html.find('<!-- =========================================================\n       BRAND STATEMENT TICKER', old_stage_start)

new_stage_markup = """<!-- LEFT: MEDIA GALLERY (Tech Hunk Exact Layout) -->
      <div class="product-media-column">
        <div class="gallery-main-frame">
          <span class="th-top-badge">29% OFF</span>
          
          <img
            src="assets/airpods-1.png"
            alt="ZERONIC Flex Earbuds"
            class="gallery-main-img"
            id="mainGalleryImg"
          />

          <!-- Floating Video Review Icon at bottom right of image -->
          <div class="th-media-video-review" onclick="document.querySelector('#reviews').scrollIntoView({behavior:'smooth'})" title="Video Review">
            <svg viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="12" fill="#ef4444"/>
              <polygon points="18,14 34,24 18,34" fill="#ffffff"/>
            </svg>
          </div>
        </div>

        <!-- Numeration Dial < 1/6 > -->
        <div class="th-counter-row">
          <button type="button" class="th-counter-arrow" onclick="changeSlide(-1)">&lt;</button>
          <span id="slideCounterText">1 / 4</span>
          <button type="button" class="th-counter-arrow" onclick="changeSlide(1)">&gt;</button>
        </div>
      </div>

      <!-- RIGHT: PRODUCT INFO & ORDER COLUMN (Tech Hunk Left-Aligned Standard) -->
      <div class="product-info-column">
        <div class="th-product-title-wrap">
          <h1>ZERONIC Flex Earbuds</h1>
        </div>

        <p class="th-product-subtitle">
          ANC | TRANSPARENCY | EQ CONTROL | GAMING MODE
        </p>

        <!-- Rating Box -->
        <div class="th-jd-rating-box">
          <span class="th-jd-stars">★★★★★</span>
          <span class="th-jd-rating-number">4.6</span>
          <a href="#reviews" class="th-jd-review-link">(142+ Reviews)</a>
        </div>

        <!-- Price Bar -->
        <div class="th-pricebar">
          <span class="th-price" id="priceDisplay">Rs.4,950</span>
          <span class="th-compare">Rs.7,000</span>
          <span class="th-off">Save Rs.2,050</span>
        </div>

        <!-- 4-Column Feature Strip (Tech Hunk Exact Card) -->
        <div class="th-fstrip">
          <div class="th-fstrip__card">
            <div class="th-fstrip__item">
              <div class="th-fstrip__icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 2v20M17 5v14M7 5v14M22 9v6M2 9v6"></path>
                </svg>
              </div>
              <div class="th-fstrip__title">ANC</div>
              <div class="th-fstrip__sub">MODE</div>
            </div>
            <div class="th-fstrip__item">
              <div class="th-fstrip__icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="4" y1="21" x2="4" y2="14"></line>
                  <line x1="4" y1="10" x2="4" y2="3"></line>
                  <line x1="12" y1="21" x2="12" y2="12"></line>
                  <line x1="12" y1="8" x2="12" y2="3"></line>
                  <line x1="20" y1="21" x2="20" y2="16"></line>
                  <line x1="20" y1="12" x2="20" y2="3"></line>
                  <line x1="1" y1="14" x2="7" y2="14"></line>
                  <line x1="9" y1="8" x2="15" y2="8"></line>
                  <line x1="17" y1="16" x2="23" y2="16"></line>
                </svg>
              </div>
              <div class="th-fstrip__title">EQ</div>
              <div class="th-fstrip__sub">CONTROL</div>
            </div>
            <div class="th-fstrip__item">
              <div class="th-fstrip__icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="2" y="6" width="20" height="12" rx="3"></rect>
                  <path d="M6 12h4m-2-2v4"></path>
                  <circle cx="17" cy="10" r="1" fill="currentColor"></circle>
                  <circle cx="15" cy="14" r="1" fill="currentColor"></circle>
                </svg>
              </div>
              <div class="th-fstrip__title">GAMING</div>
              <div class="th-fstrip__sub">MODE</div>
            </div>
            <div class="th-fstrip__item">
              <div class="th-fstrip__icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke-dasharray="2 2"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
              </div>
              <div class="th-fstrip__title">LEATHER</div>
              <div class="th-fstrip__sub">TEXTURE</div>
            </div>
          </div>
        </div>

        <!-- Color Variant Swatches (Left-Aligned) -->
        <div class="th-variant-selects">
          <div class="th-variant-label">
            Color: <span id="colorNameDisplay" style="color: #0f172a; font-weight: 700;">Flex Black</span>
          </div>
          <div class="th-swatches-grid">
            <button type="button" class="th-swatch-circle-btn active" data-color="Flex Black" data-img="assets/airpods-1.png" aria-label="Flex Black">
              <img src="assets/airpods-1.png" alt="Flex Black" />
            </button>
            <button type="button" class="th-swatch-circle-btn" data-color="Flex White" data-img="assets/airpods-2.png" aria-label="Flex White">
              <img src="assets/airpods-2.png" alt="Flex White" />
            </button>
          </div>
        </div>

        <!-- Quantity Selector (Centered row) -->
        <div id="thQtyWrap">
          <span class="thQtyLabel">Quantity:</span>
          <button type="button" class="thQtyBtn" id="btnQtyDec">−</button>
          <input type="number" id="inputQty" value="1" min="1" max="10" class="thQtyInput" readonly />
          <button type="button" class="thQtyBtn" id="btnQtyInc">+</button>
        </div>

        <!-- Action Buttons -->
        <div class="th-btn-group">
          <button type="button" class="th-add-to-cart-btn" id="btnAddToCart">
            Add to cart
          </button>
          <button type="button" class="th-buy-now-btn" id="btnBuyNow">
            Buy it now
          </button>
        </div>

        <!-- Thin Divider -->
        <div class="hm-custom-divider"></div>

        <!-- In-Page Reviews Slider -->
        <div class="th-jdgm-cards-wrap">
          <div class="th-review-slider" id="inPageReviewSlider">
            <div class="th-review-card">
              <div class="th-review-top">
                <img src="assets/airpods-1.png" alt="ZERONIC Flex" class="th-review-img" />
                <div>
                  <h3>ZERONIC Flex</h3>
                  <div class="th-stars-micro">★★★★★</div>
                  <div class="th-verified-micro">✓ Verified Purchase</div>
                </div>
              </div>
              <p class="th-review-text">"I am very satisfied with these earbuds. The battery backup is excellent, connectivity fast and stable, application also helps customize EQ."</p>
              <div class="th-review-footer">- Anonymous</div>
            </div>
            <div class="th-review-card">
              <div class="th-review-top">
                <img src="assets/airpods-2.png" alt="ZERONIC Flex" class="th-review-img" />
                <div>
                  <h3>ZERONIC Flex</h3>
                  <div class="th-stars-micro">★★★★★</div>
                  <div class="th-verified-micro">✓ Verified Purchase</div>
                </div>
              </div>
              <p class="th-review-text">"Zabardast sound and quality. Really Kuch Naya Dekhne Ko Mila Purane Earbuds Se. Software kafi acha hai."</p>
              <div class="th-review-footer">- Ali Raza</div>
            </div>
            <div class="th-review-card">
              <div class="th-review-top">
                <img src="assets/airpods-1.png" alt="ZERONIC Flex" class="th-review-img" />
                <div>
                  <h3>ZERONIC Flex</h3>
                  <div class="th-stars-micro">★★★★★</div>
                  <div class="th-verified-micro">✓ Verified Purchase</div>
                </div>
              </div>
              <p class="th-review-text">"Battery life is really impressive they easily last max 3 days without needing a recharge."</p>
              <div class="th-review-footer">- Zain</div>
            </div>
          </div>
          <div class="th-inpage-dots">
            <span class="th-inpage-dot active"></span>
            <span class="th-inpage-dot"></span>
            <span class="th-inpage-dot"></span>
          </div>
        </div>
      </div>
    </div>
  </main>
  """

if old_stage_start != -1 and old_stage_end != -1:
    html = html[:old_stage_start] + new_stage_markup + '\n\n  ' + html[old_stage_end:]

# 4. Add JavaScript for the Slide Counter and Image Switcher
slider_js = """
  <script>
    let currentSlide = 1;
    const totalSlides = 4;
    const slideImages = [
      'assets/airpods-1.png',
      'assets/airpods-2.png',
      'assets/airpods-3.png',
      'assets/airpods-4.png'
    ];
    function changeSlide(direction) {
      currentSlide += direction;
      if (currentSlide > totalSlides) currentSlide = 1;
      if (currentSlide < 1) currentSlide = totalSlides;
      
      const counterEl = document.getElementById('slideCounterText');
      if (counterEl) counterEl.textContent = `${currentSlide} / ${totalSlides}`;
      
      const imgEl = document.getElementById('mainGalleryImg');
      if (imgEl) imgEl.src = slideImages[currentSlide - 1];
    }

    // Swatches Click Handler
    document.querySelectorAll('.th-swatch-circle-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        document.querySelectorAll('.th-swatch-circle-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        const color = this.getAttribute('data-color');
        const img = this.getAttribute('data-img');
        const colorNameDisplay = document.getElementById('colorNameDisplay');
        if (colorNameDisplay) colorNameDisplay.textContent = color;
        const mainImg = document.getElementById('mainGalleryImg');
        if (mainImg) mainImg.src = img;
      });
    });
  </script>
"""

html = html.replace('</body>', slider_js + '\n</body>')

with open('product.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Exact Tech Hunk stage transformation applied!")
