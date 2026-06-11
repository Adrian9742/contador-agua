"""
Ícones Lucide renderizados em Pillow com 4× supersampling + LANCZOS.
Geometria fiel às paths do app.jsx de referência (viewBox 0 0 24 24).
"""
import math
from PIL import Image, ImageDraw
import customtkinter as ctk
from PIL import ImageTk

_CACHE: dict = {}


# ── Bezier helpers ─────────────────────────────────────────────────────────────
def _bez3(p0, p1, p2, p3, n=28):
    pts = []
    for i in range(n + 1):
        t = i / n
        c = 1 - t
        x = c**3*p0[0] + 3*c**2*t*p1[0] + 3*c*t**2*p2[0] + t**3*p3[0]
        y = c**3*p0[1] + 3*c**2*t*p1[1] + 3*c*t**2*p2[1] + t**3*p3[1]
        pts.append((x, y))
    return pts

def _arc_pts(cx, cy, rx, ry, a0_deg, a1_deg, n=32):
    pts = []
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    for i in range(n + 1):
        t = a0 + (a1 - a0) * i / n
        pts.append((cx + rx * math.cos(t), cy + ry * math.sin(t)))
    return pts


# ── Renderer base ──────────────────────────────────────────────────────────────
def _render(draw_fn, size: int, color: str) -> Image.Image:
    S = 4
    s = size * S
    k = s / 24
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    t = max(2, round(k * 1.8 * 24 / (size * S)))   # stroke width
    draw_fn(d, k, color, t)
    return img.resize((size, size), Image.LANCZOS)

def _rgba(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)

def _stroke(d, pts, color, t):
    if len(pts) >= 2:
        d.line(pts, fill=color, width=t)
    # cap dots
    r = t // 2
    for x, y in [pts[0], pts[-1]]:
        d.ellipse([x-r, y-r, x+r, y+r], fill=color)


# ── Ícones individuais ─────────────────────────────────────────────────────────
def _glass_water(d, k, color, t):
    c = _rgba(color)
    # trapézio
    poly = [(6*k, 3*k), (18*k, 3*k), (16.8*k, 19.2*k), (7.2*k, 19.2*k)]
    for i in range(len(poly)):
        p0, p1 = poly[i], poly[(i+1) % len(poly)]
        d.line([p0, p1], fill=c, width=t)
    # linha de água (M 6.6 9 h 10.8)
    d.line([(6.6*k, 9*k), (17.4*k, 9*k)], fill=c, width=t)


def _droplet(d, k, color, t):
    c = _rgba(color)
    # Lucide path: M12 3 s6 6.5 6 11  a6 6 0 0 1 -12 0  c0 -4.5 6 -11 6 -11 z
    # lado direito: smooth-cubic de (12,3)→(18,14), ctrl1=(12,3) ctrl2=(18,9.5)
    right = _bez3((12*k, 3*k), (12*k, 3*k), (18*k, 9.5*k), (18*k, 14*k))
    # arco inferior: de (18,14) até (6,14) passando por (12,20), sentido horário
    arc = _arc_pts(12*k, 14*k, 6*k, 6*k, 0, 180, n=28)
    # lado esquerdo: cubic de (6,14)→(12,3), ctrl1=(6,9.5) ctrl2=(12,3)
    left = _bez3((6*k, 14*k), (6*k, 9.5*k), (12*k, 3*k), (12*k, 3*k))
    # stroke puro — usa line, não polygon
    pts = right + arc[1:] + left[1:]
    d.line(pts, fill=c, width=t)
    # caps arredondados no início e fim
    r = max(1, t // 2)
    for px, py in [pts[0], pts[-1]]:
        d.ellipse([px-r, py-r, px+r, py+r], fill=c)


def _cup_filled(d, k, color, t):
    """Copo com água visível — para 'Dose'."""
    c = _rgba(color)
    # Trapézio (mesmas proporções de glass-water)
    tl, tr = 6*k,  18*k
    bl, br = 7.2*k, 16.8*k
    ty, by = 3*k,  19.2*k

    # Linha de nível da água a 62% de altura (de baixo para cima)
    wfrac   = 0.38                # 38% do topo = 62% cheio
    wy      = ty + (by - ty) * wfrac
    wl      = tl + (bl - tl) * wfrac
    wr      = tr + (br - tr) * wfrac

    # Fill de água (semi-transparente)
    water   = [(wl, wy), (wr, wy), (br, by), (bl, by)]
    d.polygon(water, fill=(*c[:3], 70))

    # Contorno do copo
    poly = [(tl, ty), (tr, ty), (br, by), (bl, by)]
    for i in range(len(poly)):
        d.line([poly[i], poly[(i+1) % len(poly)]], fill=c, width=t)

    # Linha do nível da água
    d.line([(wl, wy), (wr, wy)], fill=c, width=t)


def _bottle_water(d, k, color, t):
    c = _rgba(color)
    # M10 2h4v3l1 2v13a2 2 0 0 1-2 2h-2a2 2 0 0 1-2-2V7l1-2V2z
    body = [(10*k,2*k),(14*k,2*k),(14*k,5*k),(15*k,7*k),
            (15*k,20*k),(9*k,20*k),(9*k,7*k),(10*k,5*k)]
    for i in range(len(body)):
        d.line([body[i], body[(i+1) % len(body)]], fill=c, width=t)
    # linha horizontal M9 12h6
    d.line([(9*k,12*k),(15*k,12*k)], fill=c, width=t)


def _flame(d, k, color, t):
    c = _rgba(color)
    # Polígono da chama (forma aproximada do path M12 2 … 5a5 … z)
    pts = _bez3((12*k,2*k),  (15*k,4*k),  (14*k,7*k),  (14*k,8.5*k)) + \
          _bez3((14*k,8.5*k),(17*k,10*k), (17*k,13*k), (17*k,15*k))  + \
          _arc_pts(12*k,15*k, 5*k,5*k, 0, 180) + \
          _bez3((7*k,15*k),  (7*k,12*k),  (9.5*k,10*k),(9.5*k,8.5*k)) + \
          _bez3((9.5*k,8.5*k),(10*k,7*k),(9*k,4*k),   (12*k,2*k))
    d.polygon(pts, fill=c)
    # brilho interno
    inner = _arc_pts(12*k, 15*k, 2.5*k, 2.5*k, 0, 180)
    inner += [(12*k, 13*k)]
    d.polygon(inner, fill=(*_rgba("#ffedd5")[:3], 160))


def _sun(d, k, color, t):
    c = _rgba(color)
    # círculo central r=4.2
    cx, cy, r = 12*k, 12*k, 4.2*k
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=c, width=t)
    # 8 raios
    for i in range(8):
        a = math.radians(i * 45)
        r1, r2 = 6*k, 7.5*k
        x1, y1 = cx + r1*math.cos(a), cy + r1*math.sin(a)
        x2, y2 = cx + r2*math.cos(a), cy + r2*math.sin(a)
        d.line([(x1,y1),(x2,y2)], fill=c, width=t)


def _moon(d, k, color, t):
    c = _rgba(color)
    # crescente: círculo grande menos um círculo offset
    R = 8.5*k
    cx, cy = 12*k, 12*k
    # arco da lua (220° de arco)
    pts = _arc_pts(cx, cy, R, R, 155, 375, n=40)
    # corte côncavo com bezier
    pts += _bez3(pts[-1], (cx+2*k, cy-5*k), (cx-4*k, cy-8*k), pts[0])
    d.polygon(pts, fill=c)


def _settings(d, k, color, t):
    c = _rgba(color)
    cx, cy = 12*k, 12*k
    # círculo interno
    d.ellipse([cx-3*k, cy-3*k, cx+3*k, cy+3*k], outline=c, width=t)
    # 8 dentes
    for i in range(8):
        a = math.radians(i * 45)
        r1, r2 = 4.5*k, 6*k
        x1, y1 = cx + r1*math.cos(a), cy + r1*math.sin(a)
        x2, y2 = cx + r2*math.cos(a), cy + r2*math.sin(a)
        d.line([(x1,y1),(x2,y2)], fill=c, width=max(t, round(k*1.2)))
    # anel externo
    d.ellipse([cx-5.5*k, cy-5.5*k, cx+5.5*k, cy+5.5*k], outline=c, width=t)


def _check(d, k, color, t):
    c = _rgba(color)
    d.line([(5*k,13*k),(9*k,17*k),(19*k,7*k)], fill=c, width=max(t, round(k*2.5)))


def _bar_chart(d, k, color, t):
    c = _rgba(color)
    bars = [
        (4*k, 15*k, 8*k, 21*k),
        (9*k, 10*k, 13*k, 21*k),
        (14*k, 5*k, 18*k, 21*k),
    ]
    for x1, y1, x2, y2 in bars:
        d.rectangle([x1, y1, x2, y2], outline=c, width=t)
    d.line([(3*k, 21*k), (19*k, 21*k)], fill=c, width=t)


def _refresh_ccw(d, k, color, t):
    c = _rgba(color)
    # arco superior: de (3.5,8) rotacionando pelo centro (12,12)
    arc1 = _arc_pts(12*k, 12*k, 9*k, 9*k, 210, 360+30, n=28)
    _stroke(d, arc1, c, t)
    # arco inferior
    arc2 = _arc_pts(12*k, 12*k, 9*k, 9*k, 30, 210, n=28)
    _stroke(d, arc2, c, t)
    # seta superior (ponta em arc1[-1])
    ax, ay = arc1[-1]
    d.polygon([(ax, ay-t*2),(ax+t*2, ay+t),(ax-t*2, ay+t)], fill=c)
    # seta inferior
    bx, by = arc2[-1]
    d.polygon([(bx, by+t*2),(bx+t*2, by-t),(bx-t*2, by-t)], fill=c)


# ── Mapa de ícones ─────────────────────────────────────────────────────────────
_DRAW_FNS = {
    "glass-water":  _glass_water,
    "droplet":      _droplet,
    "cup-filled":   _cup_filled,
    "bottle-water": _bottle_water,
    "flame":        _flame,
    "sun":          _sun,
    "moon":         _moon,
    "settings":     _settings,
    "check":        _check,
    "bar-chart":    _bar_chart,
    "refresh-ccw":  _refresh_ccw,
}


# ── API pública ────────────────────────────────────────────────────────────────
def get_icon(name: str, size: int, color: str,
             for_canvas: bool = False) -> "ctk.CTkImage | ImageTk.PhotoImage":
    """
    Retorna CTkImage (para CTkLabel/CTkButton) ou ImageTk.PhotoImage (para Canvas).
    Resultados são cacheados.
    """
    key = (name, size, color, for_canvas)
    if key in _CACHE:
        return _CACHE[key]

    fn = _DRAW_FNS.get(name)
    if fn is None:
        # Fallback: ponto colorido
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse([2, 2, size-2, size-2],
                                    fill=(*[int(color.lstrip("#")[i:i+2], 16)
                                           for i in (0,2,4)], 255))
    else:
        img = _render(fn, size, color)

    result = (ImageTk.PhotoImage(img) if for_canvas
              else ctk.CTkImage(light_image=img, dark_image=img, size=(size, size)))
    _CACHE[key] = result
    return result


def clear_cache():
    _CACHE.clear()
