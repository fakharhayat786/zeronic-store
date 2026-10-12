with open('product.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Exact modern crisp stroke SVG icons matching screenshot 6:
# 1. ANC: Sound wave / acoustic bars
# 2. EQ: Slider controls
# 3. GAMING: Game controller gamepad
# 4. LEATHER: Mesh / woven lattice texture

old_fstrip_start = html.find('<!-- 4-Column Feature Strip (Tech Hunk Exact) -->')
old_fstrip_end = html.find('<!-- Color Variant Swatches (Tech Hunk Exact) -->', old_fstrip_start)

new_fstrip_html = """<!-- 4-Column Feature Strip (Tech Hunk Exact) -->
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
        """

if old_fstrip_start != -1 and old_fstrip_end != -1:
    html = html[:old_fstrip_start] + new_fstrip_html + html[old_fstrip_end:]

with open('product.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated fstrip icons to match Screenshot 6!')
