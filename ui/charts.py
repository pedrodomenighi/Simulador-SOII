from typing import Dict, Optional
import hashlib

def _color_for_pid(pid: Optional[int]) -> str:
    """Gera cor hex estável por PID; livre = cinza."""
    if pid is None:
        return "#E0E0E0"
    h = hashlib.md5(str(pid).encode()).hexdigest()
    return f"#{h[:6]}"

def memory_bar_html(total: int, segments) -> str:
    """
    total: tamanho total (KB)
    segments: lista de objetos (pid, inicio, tamanho)
    Renderiza uma barra 'total' células (capado a 200 para caber na tela).
    """
    max_cells = min(total, 200)
    scale = total / max_cells if total > 0 else 1
    cells = [{"pid": None} for _ in range(max_cells)]
    for seg in segments:
        start = int(seg.inicio / scale)
        length = max(1, int(seg.tamanho / scale))
        for i in range(start, min(start + length, max_cells)):
            cells[i]["pid"] = seg.pid

    boxes = []
    for c in cells:
        color = _color_for_pid(c["pid"])
        label = "" if c["pid"] is None else f"P{c['pid']}"
        boxes.append(
            f'<div class="cell" title="{label}" style="background:{color}"></div>'
        )

    style = """
    <style>
      .membar {display:flex; gap:2px; flex-wrap:wrap; max-width:920px}
      .membar .cell {width:16px; height:16px; border:1px solid #aaa; box-sizing:border-box;}
      .legend {display:flex; flex-wrap:wrap; gap:8px; margin-top:6px;}
      .legend .item {display:flex; align-items:center; gap:6px;}
      .legend .sw {width:14px; height:14px; border:1px solid #aaa;}
    </style>
    """
    html = f'{style}<div class="membar">{"".join(boxes)}</div>'
    return html

def frames_grid_html(frames, cols: int = 8) -> str:
    """
    frames: lista de objetos com .idx, .pid, .pagina
    cols: nº de colunas na grade
    """
    rows = (len(frames) + cols - 1) // cols
    # CSS grid:
    style = f"""
    <style>
      .grid {{
        display:grid;
        grid-template-columns: repeat({cols}, 1fr);
        gap:6px;
        max-width: 900px;
      }}
      .frame {{
        border:1px solid #aaa; border-radius:6px; padding:6px; height:56px;
        display:flex; flex-direction:column; justify-content:center; align-items:center;
        font-size:12px; text-align:center;
      }}
      .pid {{ font-weight:600; }}
      .muted {{ color:#444; font-size:11px; }}
    </style>
    """
    cards = []
    for f in frames:
        color = _color_for_pid(f.pid)
        if f.pid is None:
            body = f'<div class="muted">[{f.idx:02d}] livre</div>'
        else:
            body = (f'<div class="pid" style="color:{color}">P{f.pid}</div>'
                    f'<div class="muted">pg {f.pagina} · fr {f.idx}</div>')
        cards.append(f'<div class="frame">{body}</div>')
    html = f'{style}<div class="grid">{"".join(cards)}</div>'
    return html
