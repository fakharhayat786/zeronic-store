with open('product.html', 'r', encoding='utf-8') as f:
    html = f.read()

modal_css = """
/* =========================================================
   REVIEW MODAL (LIGHTBOX OVERLAY - HIDDEN UNTIL CLICKED)
========================================================= */
.th-modal-dialog {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  z-index: 999999;
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
  padding: 26px;
  position: relative;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 0, 0, 0.08);
}
"""

marker = '/* =========================================================\n       MOBILE VIEW REFINEMENTS'
if marker in html:
    html = html.replace(marker, modal_css.strip() + '\n\n' + marker)

with open('product.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Added modal CSS successfully!')
