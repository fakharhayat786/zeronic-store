with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update .hero-mobile-title and desktop .hero-title color
# Ensure color is exact #0062d8 matching Sound. in THE AUDIO EXPERIENCE
# And make sure .hero-mobile-title has the exact color #0062d8
html = html.replace(
    '.hero-mobile-title {\n        font-family: "Manrope", sans-serif;\n        font-size: 36px;\n        line-height: 1.08;\n        letter-spacing: -0.04em;\n        font-weight: 800;\n        color: #0062d8 !important;\n      }',
    '.hero-mobile-title {\n        font-family: "Manrope", sans-serif;\n        font-size: 36px;\n        line-height: 1.08;\n        letter-spacing: -0.04em;\n        font-weight: 800;\n        color: #0062d8 !important; /* Exact match with Sound. (#0062d8) */\n      }'
)

# 2. Refine the VIEW COLLECTION button in hero mobile:
# It stays the focal vibrant electric blue #0062d8 with luxury pill styling
# And adjust statement bar:
old_statement_css = """/* =========================================================
       STATEMENT BAR (Custom Electric Blue & Fast Ticker)
    ========================================================= */
.statement {
  padding: 14px 0; /* Padding thodi kam ki hai taake section sleek lage */
  background: linear-gradient(135deg, #0062d8 0%, #004eb0 100%); /* Aapki site ka native blue layout code sy match kiya */
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden; /* Screen se bahar jane wale extra texts ko hide karne k liye */
  position: relative;
  display: flex;
  align-items: center;
}

.statement-track {
  display: flex;
  white-space: nowrap; /* Text ko doosri line mein break hone se rokta hai */
  gap: 40px; /* Words ke darmiyan ka perfect distance */
  font-family: "Poppins", "Inter", sans-serif;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #ffffff; /* Blue background par pure high-contrast white text */
  /* Speed Fix: Pehle 15s-20s tha, isko 8s (8 seconds) kiya hai taake speed tez aur smooth ho */
  animation: dynamic-marquee-fast 8s linear infinite; 
  will-change: transform;
}

.statement-dot {
  align-self: center;
  width: 5px;
  height: 5px;
  background: #ffffff; /* Dot ko bhi white kiya taake layout unified lage */
  border-radius: 50%;
  opacity: 0.7;
  flex-shrink: 0;
}"""

new_statement_css = """/* =========================================================
       STATEMENT BAR (Option B: Refined Minimal Marquee - Balances Blue Hero Button)
    ========================================================= */
.statement {
  padding: 13px 0;
  background: #f8fafc; /* Clean, premium off-white canvas so View Collection button stands out */
  border-top: 1px solid #e2e8f0;
  border-bottom: 1px solid #e2e8f0;
  overflow: hidden;
  position: relative;
  display: flex;
  align-items: center;
}

.statement-track {
  display: flex;
  white-space: nowrap;
  gap: 44px;
  font-family: "Poppins", "Inter", sans-serif;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #0f172a; /* Sophisticated dark typography */
  animation: dynamic-marquee-fast 10s linear infinite;
  will-change: transform;
}

.statement-dot {
  align-self: center;
  width: 5px;
  height: 5px;
  background: #0062d8; /* Signature electric blue accent dot matching website branding */
  border-radius: 50%;
  opacity: 0.9;
  flex-shrink: 0;
}"""

if old_statement_css in html:
    html = html.replace(old_statement_css, new_statement_css)
    print("Replaced old statement CSS with refined Option B styling")
else:
    print("Could not find exact old statement CSS string, searching with regex...")
    import re
    html = re.sub(
        r'/\* ==+[^=]+STATEMENT BAR[^=]+==+ \*/\s*\.statement\s*\{[^}]*\}\s*\.statement-track\s*\{[^}]*\}\s*\.statement-dot\s*\{[^}]*\}',
        new_statement_css.strip(),
        html
    )
    print("Replaced with regex!")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated successfully!")
