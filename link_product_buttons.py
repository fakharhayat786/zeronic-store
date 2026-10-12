with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Product 1 (ZERONIC Flex Earbuds) "Buy Now" button -> product.html
old_p1_btn = """      <button
        class="th-buy-btn"
        onclick="addToCart('ZERONIC Flex Earbuds')"
        aria-label="Buy ZERONIC Flex Earbuds"
      >
        Buy Now
      </button>"""

new_p1_btn = """      <a
        href="product.html"
        class="th-buy-btn"
        style="text-decoration: none; display: inline-flex; align-items: center; justify-content: center;"
        aria-label="Buy ZERONIC Flex Earbuds"
      >
        Buy Now
      </a>"""

if old_p1_btn in html:
    html = html.replace(old_p1_btn, new_p1_btn)
    print("Linked Product 1 Buy Now button to product.html")

# 2. Also link product title & image of ZERONIC Flex Earbuds so clicking them leads to product.html
old_p1_title = '<h3 class="th-product-title">ZERONIC Flex Earbuds</h3>'
new_p1_title = '<h3 class="th-product-title"><a href="product.html" style="color: inherit; text-decoration: none;">ZERONIC Flex Earbuds</a></h3>'

if old_p1_title in html:
    html = html.replace(old_p1_title, new_p1_title)
    print("Linked Product 1 Title to product.html")

# 3. Interactive slider "Shop Now" link (thfs-cta)
old_thfs_cta = """                    <a class="thfs-cta" href="#earbuds" aria-label="Shop AirPods Pro 2">
                      <span>Shop Now</span>"""
new_thfs_cta = """                    <a class="thfs-cta" href="product.html" aria-label="Shop AirPods Pro 2">
                      <span>Shop Now</span>"""

if old_thfs_cta in html:
    html = html.replace(old_thfs_cta, new_thfs_cta)
    print("Linked 3D Slider Shop Now button to product.html")

# 4. In Footer SHOP accordion:
# Change <a href="#earbuds">Earbuds</a> -> <a href="product.html">Earbuds</a>
# (Leaving other links intact)
old_footer_earbuds = '<div class="th-links">\n            <a href="#earbuds">Earbuds</a>'
new_footer_earbuds = '<div class="th-links">\n            <a href="product.html">Earbuds</a>'
if old_footer_earbuds in html:
    html = html.replace(old_footer_earbuds, new_footer_earbuds)
    print("Linked Footer Earbuds link to product.html")

# 5. In Side Menu Drawer:
# Change <a href="#earbuds"> ... Earbuds ... </a> -> href="product.html"
old_side_earbuds = '<a href="#earbuds">\n        <span class="menu-item-text">Earbuds</span>'
new_side_earbuds = '<a href="product.html">\n        <span class="menu-item-text">Earbuds</span>'
if old_side_earbuds in html:
    html = html.replace(old_side_earbuds, new_side_earbuds)
    print("Linked Side Menu Earbuds link to product.html")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Homepage link updates completed!")
