# 《钱是万恶之根吗？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：管家的四个用处 ----------------
def four():
    W, H = 400, 300
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="mnf1t mnf1d">',
           '<title id="mnf1t">管家的四个用处</title>',
           '<desc id="mnf1d">中间是：我是管家，一切都是主的（诗24:1）。四周是钱的四个用处：养家（提前5:8）、不欠债（罗13:8）、'
           '十分之一归给上帝（玛3:10）、施舍帮助人（弗4:28）。下面写着：知足（来13:5）。</desc>']
    boxes = [(20, 20, 'f1', '养活家人', '提前5:8'), (220, 20, 'f3', '不欠不该欠的债', '罗13:8'),
             (20, 196, 'f4', '十分之一归给上帝', '玛3:10'), (220, 196, 'f6', '施舍，帮助人', '弗4:28')]
    for x, y, c, t, r in boxes:
        out.append(f'<rect x="{x}" y="{y}" width="160" height="56" rx="12" class="{c} fillc"/>')
        out.append(text(x + 80, y + 25, t, 'tnode2', 'middle'))
        out.append(text(x + 80, y + 43, r, 'tnode2', 'middle'))
    out.append('<path d="M100 76 L170 122 M300 76 L230 122 M100 196 L170 166 M300 196 L230 166" class="flow"/>')
    out.append('<rect x="120" y="112" width="160" height="64" rx="32" class="box"/>')
    out.append(text(200, 139, '我是管家', 'tn hi', 'middle'))
    out.append(text(200, 158, '一切都是主的（诗24:1）', 'ts', 'middle'))
    out.append(text(200, 280, '底下的地基：知足——“我总不撇下你，也不丢弃你”（来13:5）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
