with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update HTML of the CTA section:
# Change:
# <h2 class="cta-title">
#   Your day.<br />
#   <span>Your sound.</span>
# </h2>
# to:
# <h2 class="cta-title">
#   <span class="cta-day">Your day.</span><br />
#   <span>Your sound.</span>
# </h2>

old_cta_html = """    <!-- UPGRADE YOUR EVERYDAY CTA -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-card">
          <div class="cta-content">
            <div class="eyebrow">
              UPGRADE YOUR EVERYDAY
            </div>
            <h2 class="cta-title">
              Your day.<br />
              <span>Your sound.</span>
            </h2>
            <p class="cta-description">
              Elevate your daily rhythm with personal audio designed for seamless listening, distinct clarity, and timeless aesthetic.
            </p>
          </div>
          <img
            class="cta-image"
            src="assets/airpods-1.png"
            alt="ZERONIC Premium Wireless Earbuds"
          />
          <div class="cta-actions">
            <a
              href="#earbuds"
              class="btn btn-white"
            >
              View Collection
            </a>
          </div>
        </div>
      </div>
    </section>"""

new_cta_html = """    <!-- UPGRADE YOUR EVERYDAY CTA -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-card">
          <div class="cta-content">
            <div class="eyebrow">
              UPGRADE YOUR EVERYDAY
            </div>
            <h2 class="cta-title">
              <span class="cta-day">Your day.</span><br />
              <span>Your sound.</span>
            </h2>
            <p class="cta-description">
              Elevate your daily rhythm with personal audio designed for seamless listening, distinct clarity, and timeless aesthetic.
            </p>
          </div>
          <img
            class="cta-image"
            src="assets/airpods-1.png"
            alt="ZERONIC Premium Wireless Earbuds"
          />
          <div class="cta-actions">
            <a
              href="#earbuds"
              class="btn btn-blue"
            >
              View Collection
            </a>
          </div>
        </div>
      </div>
    </section>"""

if old_cta_html in html:
    html = html.replace(old_cta_html, new_cta_html)
    print("Updated cta section HTML!")
else:
    print("Could not find exact old_cta_html, trying targeted replace...")
    html = html.replace(
        '<h2 class="cta-title">\n              Your day.<br />\n              <span>Your sound.</span>\n            </h2>',
        '<h2 class="cta-title">\n              <span class="cta-day">Your day.</span><br />\n              <span>Your sound.</span>\n            </h2>'
    )
    html = html.replace('class="btn btn-white">\n              View Collection', 'class="btn btn-blue">\n              View Collection')

# 2. Update CSS for .cta-section and .cta-card:
# Match the background with website/experience section (#ffffff or subtle elegant light container)
# cta-day in electric blue (#0062d8) like sound.
# "Your sound." in secondary-gray (#64748b) like the rest of the site
# Eyebrow in secondary-gray uppercase
# Description in secondary-gray (#64748b)
# Button in #0062d8 with white text, just like experience-action and header

old_css_start = html.find('/* =========================================================\n       UPGRADE YOUR EVERYDAY CTA')
old_css_end = html.find('/* =========================================================\n       FOOTER', old_css_start)

new_cta_css = """/* =========================================================
       UPGRADE YOUR EVERYDAY CTA (Consistent Minimal Aesthetic)
    ========================================================= */
    .cta-section {
      padding: 40px 0 80px;
      background: #ffffff;
    }

    .cta-card {
      position: relative;
      overflow: hidden;
      border-radius: 28px;
      min-height: 480px;
      background: #ffffff;
      border: 1px solid var(--border-dark);
      box-shadow: 0 10px 32px rgba(0, 0, 0, 0.04);
      display: flex;
      align-items: center;
    }

    .cta-card .eyebrow {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: var(--secondary-gray);
      margin-bottom: 12px;
    }

    .cta-content {
      position: relative;
      z-index: 2;
      width: 55%;
      padding: 70px 80px;
      display: flex;
      flex-direction: column;
    }

    .cta-title {
      font-family: "Manrope", sans-serif;
      font-size: clamp(38px, 4.5vw, 64px);
      line-height: 1.02;
      letter-spacing: -0.05em;
      font-weight: 800;
      color: var(--secondary-gray);
    }

    .cta-title .cta-day {
      color: #0062d8; /* Exact match with Sound. (#0062d8) */
      font-weight: 800;
    }

    .cta-title span:not(.cta-day) {
      color: var(--secondary-gray);
      font-weight: 400;
    }

    .cta-description {
      max-width: 480px;
      margin-top: 22px;
      color: var(--secondary-gray);
      line-height: 1.75;
      font-size: 15px;
    }

    .cta-actions {
      margin-top: 36px;
    }

    .cta-card .btn-blue,
    .cta-actions .btn {
      background: #0062d8 !important;
      color: #ffffff !important;
      border: none !important;
      font-family: "Manrope", sans-serif;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      padding: 12px 28px;
      border-radius: 999px;
      box-shadow: 0 4px 16px rgba(0, 98, 216, 0.28);
      transition: background 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
    }

    .cta-card .btn-blue:hover,
    .cta-actions .btn:hover {
      background: #004eb0 !important;
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0, 98, 216, 0.4);
    }

    .cta-image {
      position: absolute;
      right: 6%;
      top: 50%;
      transform: translateY(-50%);
      width: 40%;
      max-height: 82%;
      object-fit: contain;
      filter: drop-shadow(0 15px 30px rgba(0, 0, 0, 0.08));
    }
"""

if old_css_start != -1 and old_css_end != -1:
    html = html[:old_css_start] + new_cta_css.strip() + '\n\n    ' + html[old_css_end:]
    print("Replaced main CTA CSS block!")

# 3. Also check mobile responsive adjustments for cta-card:
# Ensure mobile background is also white, border clean, image cleanly scaled
mobile_cta_patch = """
      .cta-section {
        padding: 24px 0 36px;
        background: #ffffff;
      }
      .cta-card {
        min-height: auto;
        flex-direction: column;
        align-items: center;
        background: #ffffff !important;
        border: 1px solid var(--border-dark) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04) !important;
      }
      .cta-content {
        width: 100%;
        padding: 36px 20px 20px;
        text-align: center;
      }
      .cta-title {
        font-size: 34px !important;
        line-height: 1.08 !important;
      }
      .cta-image {
        position: relative;
        right: auto;
        top: auto;
        bottom: auto;
        transform: none;
        width: 86%;
        max-width: 320px;
        max-height: 240px;
        margin: 10px auto 20px;
        filter: drop-shadow(0 10px 25px rgba(0, 0, 0, 0.08)) !important;
      }
      .cta-actions {
        margin-top: 0;
        margin-bottom: 24px;
        display: flex;
        justify-content: center;
      }
      .cta-actions .btn {
        width: auto !important;
        min-width: 180px;
      }
"""

# Replace in media queries
import re
html = re.sub(
    r'\.cta-section\s*\{\s*padding:\s*24px 0 36px;\s*\}\s*\.cta-card\s*\{[^}]*\}\s*\.cta-content\s*\{[^}]*\}\s*\.cta-image\s*\{[^}]*\}\s*\.cta-actions\s*\{[^}]*\}',
    mobile_cta_patch.strip(),
    html
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html fully updated!")
