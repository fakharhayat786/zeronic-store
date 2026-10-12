with open('product.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
skip_level = 0
skip_type = None

i = 0
while i < len(lines):
    line = lines[i]
    # Check if this line starts a review card or full review article with Zeeshan or Ahwazazeem
    if '<article class="th-full-rev-card">' in line:
        # Check next 20 lines to see if it belongs to Zeeshan or Ahwazazeem
        block = ''.join(lines[i:min(len(lines), i+25)])
        if 'Zeeshan' in block or 'Ahwazazeem' in block:
            # Skip until </article>
            while i < len(lines) and '</article>' not in lines[i]:
                i += 1
            i += 1 # skip </article> line
            continue
    elif '<div class="th-review-card">' in line:
        block = ''.join(lines[i:min(len(lines), i+25)])
        if 'Zeeshan' in block or 'Ahwazazeem' in block:
            # Skip until closing card: find - Zeeshan or - Ahwazazeem then 2 closing </div>s
            while i < len(lines) and ('- Zeeshan' not in lines[i] and '- Ahwazazeem' not in lines[i]):
                i += 1
            if i < len(lines):
                i += 1 # skip the footer line
                # skip next closing div
                while i < len(lines) and '</div>' not in lines[i]:
                    i += 1
                i += 1
            continue

    new_lines.append(line)
    i += 1

with open('product.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Exact line filter finished!')
