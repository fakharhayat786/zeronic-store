with open('product.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Also update the statement ticker in product.html if it has the statement class
old_prod_statement = """/* =========================================================
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
}"""

new_prod_statement = """/* =========================================================
   STATEMENT BAR (Option B: Refined Minimal Marquee)
========================================================= */
.statement {
  padding: 13px 0;
  background: #f8fafc;
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
  color: #0f172a;
  animation: dynamic-marquee-fast 10s linear infinite;
  will-change: transform;
}

.statement-dot {
  align-self: center;
  width: 5px;
  height: 5px;
  background: #0062d8;
  border-radius: 50%;
  opacity: 0.9;
  flex-shrink: 0;
}"""

if old_prod_statement in html:
    html = html.replace(old_prod_statement, new_prod_statement)
    print("Replaced in product.html")
    with open('product.html', 'w', encoding='utf-8') as f:
        f.write(html)
else:
    print("Old prod statement not identical, checking...")
