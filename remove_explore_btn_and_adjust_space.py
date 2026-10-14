with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove the "Explore Earbuds" button from .experience-copy
old_btn_block = """            <div class="experience-action">
              <a
                href="#earbuds"
                class="btn btn-white"
                style="background: #0062d8; color: #ffffff;"
              >
                Explore Earbuds
              </a>
            </div>"""

if old_btn_block in html:
    html = html.replace(old_btn_block, '')
    print("Removed Explore Earbuds button markup!")
else:
    # Try finding with regex or flexible whitespace
    import re
    html = re.sub(
        r'<div class="experience-action">\s*<a[^>]*>\s*Explore Earbuds\s*</a>\s*</div>',
        '',
        html
    )
    print("Removed Explore Earbuds button via regex!")

# 2. Update CSS for .experience-grid and mobile margins so .experience-image-area moves up nicely:
# In desktop:
# .experience-description margin-top: 24px; and no extra bottom margin needed
# In mobile:
# Decrease padding of .experience and make .experience-image-area seamlessly flow right under the description
update_css = """
    .experience {
      background: #ffffff;
      color: #111111;
      padding: 70px 0 35px;
      border-top: 1px solid var(--border-dark);
    }
    .experience-grid {
      display: grid;
      grid-template-columns: 0.85fr 1.15fr;
      gap: 60px;
      align-items: center;
    }
    .experience-title {
      font-family: "Manrope", sans-serif;
      font-size: clamp(42px, 5.5vw, 76px);
      line-height: 0.98;
      letter-spacing: -0.05em;
      font-weight: 800;
      color: #0062d8;
    }
    .experience-title .experience-sound {
      color: #0062d8;
    }
    .experience-title span:not(.experience-sound) {
      color: var(--secondary-gray);
      font-weight: 400;
    }
    .experience-description {
      margin-top: 22px;
      max-width: 500px;
      color: var(--secondary-gray);
      line-height: 1.8;
      font-size: 15px;
    }
    .experience-image-area {
      position: relative;
      min-height: 470px;
      border-radius: 28px;
      overflow: hidden;
      background: #ffffff;
      border: 1px solid var(--border-dark);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 36px 20px 28px;
      box-shadow: 0 10px 32px rgba(0, 0, 0, 0.04);
    }
"""

old_exp_start = html.find('/* =========================================================\n       EXPERIENCE / STORYTELLING')
old_exp_end = html.find('/* =========================================================\n       UPGRADE YOUR EVERYDAY CTA', old_exp_start)

if old_exp_start != -1 and old_exp_end != -1:
    html = html[:old_exp_start] + "/* =========================================================\n       EXPERIENCE / STORYTELLING\n    ========================================================= */" + update_css + "\n    " + html[old_exp_end:]
    print("Updated desktop experience CSS!")

# 3. In mobile media queries:
# For max-width: 850px and 650px:
# Reduce experience-copy bottom margin so moving buds area sits directly under text:
mobile_exp_patch = """
      .experience {
        padding: 40px 0 20px;
      }
      .experience-grid {
        grid-template-columns: 1fr;
        gap: 20px;
      }
      .experience-copy {
        margin-bottom: 0;
      }
      .experience-description {
        margin-top: 14px;
        margin-bottom: 4px;
        line-height: 1.6;
      }
      .experience-image-area {
        min-height: 400px;
        padding: 24px 14px 20px;
        margin-top: 6px;
      }
"""

import re
html = re.sub(
    r'\.experience\s*\{\s*padding:\s*50px 0 24px;\s*\}\s*\.experience-grid\s*\{\s*grid-template-columns:\s*1fr;\s*\}\s*\.experience-image-area\s*\{[^}]*\}',
    mobile_exp_patch.strip(),
    html
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html successfully updated!")
