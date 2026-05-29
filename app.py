"""
Contador de Água — UI em CustomTkinter + Pillow.
Fiel ao design: dark navy, garrafa animada em Canvas, chips de atalho,
streak card com 7 dias e ícones renderizados com anti-alias via Pillow.
"""
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageDraw
import math, time
from state import AppState
from timer_manager import TimerManager
from notifier import Notifier

ctk.set_appearance_mode("dark")

# ── Paleta (design tokens) ─────────────────────────────────────────────────────
W  = "#0d1424"   # window bg
S  = "#111827"   # surface (cards)
S2 = "#1a2540"   # surface hover
BD = "#1e2d4a"   # border
T  = "#eef2fb"   # text
M  = "#8a96ad"   # muted
FA = "#5b6478"   # faint
AC = "#2563eb"   # accent
A2 = "#3b82f6"   # accent-2
WH = "#38bdf8"   # water highlight
WL = "#1d4ed8"   # water low
FL = "#f97316"   # flame
IN = "#0f1826"   # input bg
RE = "#ef4444"   # red / flash

FONT = "Segoe UI"

CHIPS = [
    {"ml": 150, "label": "Pequeno", "kind": "s"},
    {"ml": 200, "label": "Copo",    "kind": "m"},
    {"ml": 350, "label": "Grande",  "kind": "l"},
    {"ml": 500, "label": "Garrafa", "kind": "b"},
]


# ── Utilitários Pillow ─────────────────────────────────────────────────────────
def _rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _icon(fn, w: int, h: int) -> ctk.CTkImage:
    """Renderiza a 2× e reduz (anti-alias barato)."""
    img = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    fn(ImageDraw.Draw(img), w * 2, h * 2)
    img = img.resize((w, h), Image.LANCZOS)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(w, h))


def ico_drop(size=18, color=A2):
    def fn(d, w, h):
        c = _rgb(color)
        r = w * 0.30
        cx, cy = w / 2, h * 0.64
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
        d.polygon([(cx, h * 0.06), (cx - r * 1.2, cy + 2), (cx + r * 1.2, cy + 2)], fill=c)
    return _icon(fn, size, size)


def ico_flame(size=20, color=FL):
    def fn(d, w, h):
        c = _rgb(color)
        pts = [(w*.50,h*.04),(w*.82,h*.36),(w*.78,h*.58),(w*.60,h*.46),
               (w*.70,h*.70),(w*.50,h*.96),(w*.30,h*.70),(w*.40,h*.46),
               (w*.22,h*.58),(w*.18,h*.36)]
        d.polygon([(int(x),int(y)) for x,y in pts], fill=c)
        ci = _rgb("#ffedd5")
        d.ellipse([w*.36,h*.56,w*.64,h*.84], fill=(*ci, 160))
    return _icon(fn, size, size)


def ico_gear(size=18, color=M):
    def fn(d, w, h):
        c = _rgb(color)
        bg = _rgb(W)
        cx, cy = w / 2, h / 2
        R, r, hole = w*.42, w*.22, w*.15
        # dentes
        for i in range(8):
            a = math.radians(i * 45)
            x1 = cx + (R - w*.12) * math.cos(a)
            y1 = cy + (R - w*.12) * math.sin(a)
            x2 = cx + (R + w*.10) * math.cos(a)
            y2 = cy + (R + w*.10) * math.sin(a)
            d.line([(x1, y1), (x2, y2)], fill=c, width=max(2, int(w*.18)))
        # disco
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=c)
        # furo
        d.ellipse([cx-hole, cy-hole, cx+hole, cy+hole], fill=bg)
    return _icon(fn, size, size)


def ico_check(size=14, color="#ffffff"):
    def fn(d, w, h):
        c = _rgb(color)
        t = max(2, w // 8)
        pts = [(int(w*.15),int(h*.50)), (int(w*.42),int(h*.78)), (int(w*.85),int(h*.22))]
        d.line(pts, fill=c, width=t)
    return _icon(fn, size, size)


def ico_cup(size=22, kind="m", color=A2):
    """kind: s=small, m=medium, l=large, b=bottle"""
    def fn(d, w, h):
        c = _rgb(color)
        t = max(2, w // 12)
        if kind == "b":
            nw, bw = int(w*.30), int(w*.52)
            nh, bh = int(h*.22), int(h*.60)
            nx = (w - nw) // 2
            ny = int(h * .08)
            bx = (w - bw) // 2
            by = ny + nh
            d.rectangle([nx, ny, nx+nw, by], outline=c, width=t)
            d.rectangle([bx, by, bx+bw, by+bh], outline=c, width=t)
            fh = int(bh * .55)
            d.rectangle([bx+t*2, by+bh-fh, bx+bw-t*2, by+bh-t], fill=(*c, 140))
        else:
            scale = {"s": 0.75, "m": 0.90, "l": 1.08}[kind]
            cw = int(w * .70 * scale)
            ch = int(h * .58 * scale)
            shrink = int(cw * .10)
            ox = (w - cw) // 2
            oy = (h - ch) // 2 + int(h * .04)
            pts = [(ox, oy), (ox+cw, oy), (ox+cw-shrink, oy+ch), (ox+shrink, oy+ch)]
            d.polygon(pts, outline=c, width=t)
            fill_pct = {"s": .35, "m": .50, "l": .65}[kind]
            fh = int(ch * fill_pct)
            r2 = shrink * (1 - fh/ch)
            wp = [(int(ox+r2+t), oy+ch-fh),
                  (int(ox+cw-r2-t), oy+ch-fh),
                  (ox+cw-shrink-t, oy+ch-t),
                  (ox+shrink+t, oy+ch-t)]
            d.polygon(wp, fill=(*c, 130))
    return _icon(fn, size, size)


def ico_reset(size=16, color=FA):
    def fn(d, w, h):
        c = _rgb(color)
        t = max(2, w // 10)
        r = w * .36
        cx, cy = w/2, h/2
        bb = [cx-r, cy-r, cx+r, cy+r]
        d.arc(bb, start=45, end=315, fill=c, width=t)
        ax = cx + r * math.cos(math.radians(45))
        ay = cy - r * math.sin(math.radians(45))
        sz = w * .14
        d.polygon([(ax-sz, ay-sz), (ax+sz, ay), (ax+sz*0.2, ay-sz*2.2)], fill=c)
    return _icon(fn, size, size)


# ── Garrafa animada (Canvas tk) ────────────────────────────────────────────────
class BottleCanvas(tk.Canvas):
    W, H = 300, 260

    # geometria da garrafa (relativo ao canvas)
    CAP_X, CAP_Y, CAP_W, CAP_H   = 120,  10, 60, 14
    NECK_X, NECK_Y, NECK_W, NECK_H = 106, 24, 88, 34
    BODY_X, BODY_Y, BODY_W, BODY_H =  76, 58, 148, 185

    def __init__(self, master, state: AppState, **kw):
        super().__init__(master, width=self.W, height=self.H,
                         bg=W, highlightthickness=0, **kw)
        self._state = state
        self._phase = 0.0
        self._animate()

    def _animate(self):
        self._phase += 0.06
        self._draw()
        self.after(50, self._animate)

    # ── rounded polygon helper ────────────────────────────────────────────────
    def _rrect(self, x1, y1, x2, y2, r=10, **kw):
        pts = [
            x1+r, y1,  x2-r, y1,
            x2,   y1+r, x2, y2-r,
            x2-r, y2,  x1+r, y2,
            x1,   y2-r, x1, y1+r,
        ]
        return self.create_polygon(pts, smooth=True, **kw)

    def _draw(self):
        self.delete("all")
        s   = self._state
        pct = s.percent()
        flash = time.time() < s.flash_until

        bx  = self.BODY_X
        by  = self.BODY_Y
        bw  = self.BODY_W
        bh  = self.BODY_H
        bx2 = bx + bw
        by2 = by + bh

        border_c = RE if flash else "#1e3a5c"

        # ── garrafa: fundo de vidro ───────────────────────────────────────────
        self._rrect(bx, by, bx2, by2, r=18,
                    fill="#0f1e38", outline=border_c, width=1)

        # ── gargalo ───────────────────────────────────────────────────────────
        nx, ny = self.NECK_X, self.NECK_Y
        nw, nh = self.NECK_W, self.NECK_H
        self._rrect(nx, ny, nx+nw, ny+nh, r=8,
                    fill="#0f1e38", outline=border_c, width=1)

        # ── tampa ─────────────────────────────────────────────────────────────
        cx2 = self.CAP_X
        cy2 = self.CAP_Y
        cw2 = self.CAP_W
        ch2 = self.CAP_H
        self._rrect(cx2, cy2, cx2+cw2, cy2+ch2, r=5,
                    fill="#2a3650", outline=border_c, width=1)

        # ── água ──────────────────────────────────────────────────────────────
        if pct > 0.005:
            fill_h   = int(bh * pct)
            water_y  = by2 - fill_h
            water_c  = _rgb(WH) if s.goal_reached else _rgb(A2)
            wave_amp = 4 if not s.goal_reached else 7
            freq     = 0.055

            # polígono de onda
            wave_pts = []
            for i in range(bw + 1):
                x = bx + i
                y = water_y + wave_amp * math.sin(i * freq + self._phase)
                wave_pts.extend([x, y])
            wave_pts.extend([bx2 - 2, by2 - 2, bx + 2, by2 - 2])
            self.create_polygon(wave_pts, fill=_rgb_css(water_c), outline="",
                                smooth=False)

            # segunda onda mais escura
            wave_pts2 = []
            wc2 = _rgb(WL) if not s.goal_reached else _rgb("#0ea5e9")
            for i in range(bw + 1):
                x = bx + i
                y = water_y + 3 + wave_amp * math.sin(i * freq + self._phase + math.pi)
                wave_pts2.extend([x, y])
            wave_pts2.extend([bx2 - 2, by2 - 2, bx + 2, by2 - 2])
            self.create_polygon(wave_pts2, fill=_rgb_css(wc2), outline="",
                                smooth=False)

        # ── bordas da garrafa (por cima da água) ──────────────────────────────
        self._rrect(bx, by, bx2, by2, r=18,
                    fill="", outline=border_c, width=2)
        self._rrect(nx, ny, nx+nw, ny+nh, r=8,
                    fill="", outline=border_c, width=2)
        self._rrect(cx2, cy2, cx2+cw2, cy2+ch2, r=5,
                    fill="", outline=border_c, width=2)

        # ── reflexo diagonal ──────────────────────────────────────────────────
        ri = self.create_polygon(
            [bx+14, by+8, bx+30, by+8, bx+14, by+bh-16, bx+4, by+bh-16],
            fill="#ffffff", outline="", smooth=True
        )
        self.itemconfig(ri, stipple="gray25")

        # ── régua lateral ─────────────────────────────────────────────────────
        rx = bx2 + 8
        for frac, label in [(0, "0"), (0.5, str(s.goal_ml // 2)), (1.0, str(s.goal_ml))]:
            ty = by2 - int(bh * frac)
            self.create_line(rx, ty, rx + 7, ty, fill=FA, width=1)
            self.create_text(rx + 10, ty, text=f"{label}", fill=FA,
                             font=(FONT, 8), anchor="w")

        # ── badge % (pill acima da garrafa) ───────────────────────────────────
        pct_str = f"{int(pct * 100)}%"
        pill_cx = self.W // 2
        pill_cy = 4
        pill_w, pill_h = 52, 20
        self._rrect(pill_cx - pill_w//2, pill_cy,
                    pill_cx + pill_w//2, pill_cy + pill_h,
                    r=10, fill="#0d1424", outline=AC, width=2)
        self.create_text(pill_cx, pill_cy + pill_h//2, text=pct_str,
                         fill=AC, font=(FONT, 10, "bold"))


def _rgb_css(t: tuple) -> str:
    return f"#{t[0]:02x}{t[1]:02x}{t[2]:02x}"


# ── Configurações (diálogo CTkToplevel) ────────────────────────────────────────
class ConfigDialog(ctk.CTkToplevel):
    FIELDS = [
        ("Meta diaria (ml)",              "goal_ml",        100, 10000),
        ("Intervalo de lembrete (min)",   "interval_min",     1,   480),
        ("Volume do copo rapido (ml)",    "default_cup_ml",  50,  2000),
    ]

    def __init__(self, master, state: AppState):
        super().__init__(master)
        self._state = state
        self.title("Configuracoes")
        self.geometry("360x320")
        self.resizable(False, False)
        self.configure(fg_color=W)
        self.grab_set()

        self._entries: list[ctk.CTkEntry] = []
        for i, (label, attr, lo, hi) in enumerate(self.FIELDS):
            ctk.CTkLabel(self, text=label, text_color=M,
                         font=(FONT, 12)).pack(anchor="w", padx=28, pady=(16 if i==0 else 8, 2))
            e = ctk.CTkEntry(self, width=300, fg_color=IN, border_color=BD,
                             text_color=T, font=(FONT, 14, "bold"))
            e.insert(0, str(getattr(state, attr)))
            e.pack(padx=28)
            self._entries.append(e)

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(pady=20)
        ctk.CTkButton(row, text="Salvar", width=130, corner_radius=10,
                      fg_color=AC, hover_color=A2, font=(FONT, 13, "bold"),
                      command=self._save).pack(side="left", padx=6)
        ctk.CTkButton(row, text="Cancelar", width=130, corner_radius=10,
                      fg_color=S, border_width=1, border_color=BD,
                      hover_color=S2, text_color=M, font=(FONT, 13),
                      command=self.destroy).pack(side="left", padx=6)

    def _save(self):
        try:
            vals = [int(e.get()) for e in self._entries]
            for (_, attr, lo, hi), v in zip(self.FIELDS, vals):
                if not (lo <= v <= hi):
                    return
                setattr(self._state, attr, v)
            self._state.save()
            self.destroy()
        except ValueError:
            pass


# ── App principal ─────────────────────────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Contador de Agua")
        self.geometry("440x760")
        self.resizable(False, False)
        self.configure(fg_color=W)

        self._state    = AppState.load()
        self._notifier = Notifier()
        self._notifier.load_sounds()
        self._timer    = TimerManager(self._state, self._notifier)

        self._prev_goal = self._state.goal_reached
        self._flash_lbl: ctk.CTkLabel | None = None
        self._streak_circles: list[tk.Canvas] = []
        self._streak_num_lbl: ctk.CTkLabel | None = None
        self._hero_lbl: ctk.CTkLabel | None = None
        self._sub_lbl:  ctk.CTkLabel | None = None
        self._cd_lbl:   ctk.CTkLabel | None = None

        self._build()
        self._timer.start()
        self._poll()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── construção da UI ──────────────────────────────────────────────────────
    def _build(self):
        self._titlebar()

        scroll = ctk.CTkScrollableFrame(self, fg_color=W, scrollbar_button_color=BD,
                                        scrollbar_button_hover_color=S2)
        scroll.pack(fill="both", expand=True)
        self._content = scroll
        self._hero()
        self._bottle_section()
        self._chips()
        self._manual_row()
        self._streak_card()
        self._footer()

    def _titlebar(self):
        bar = ctk.CTkFrame(self, height=48, fg_color="#0c1222",
                           corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        left = ctk.CTkFrame(bar, fg_color="transparent")
        left.pack(side="left", padx=14)

        # ícone gota azul no quadrado arredondado
        dot_c = tk.Canvas(left, width=26, height=26, bg="#2563eb",
                          highlightthickness=0)
        dot_c.pack(side="left")
        # round corners trick via tag
        dot_c.configure(bg="#2563eb")
        dot_img = ico_drop(14, "#ffffff")
        dot_c.create_image(13, 13, image=dot_img)
        dot_c._img = dot_img

        ctk.CTkLabel(left, text="  Contador de Agua", text_color=T,
                     font=(FONT, 13, "bold")).pack(side="left")

        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.pack(side="right", padx=10)

        gear_img = ico_gear(16, M)
        btn_cfg = ctk.CTkButton(right, image=gear_img, text="", width=34, height=34,
                                corner_radius=10, fg_color=S, border_width=1,
                                border_color=BD, hover_color=S2,
                                command=self._open_config)
        btn_cfg.pack(side="right", padx=3)
        btn_cfg._img = gear_img

        # countdown label no title bar
        self._cd_lbl = ctk.CTkLabel(right, text="", text_color=FA,
                                     font=(FONT, 11))
        self._cd_lbl.pack(side="right", padx=8)

    def _hero(self):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        f.pack(fill="x", padx=24, pady=(18, 0))

        self._hero_lbl = ctk.CTkLabel(f, text="", text_color=T,
                                       font=(FONT, 40, "bold"))
        self._hero_lbl.pack()
        self._sub_lbl = ctk.CTkLabel(f, text="", text_color=M,
                                      font=(FONT, 13))
        self._sub_lbl.pack()

    def _bottle_section(self):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        f.pack(pady=(6, 0))
        self._bottle = BottleCanvas(f, self._state)
        self._bottle.pack()

    def _chips(self):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        f.pack(fill="x", padx=24, pady=(12, 0))

        for i, chip in enumerate(CHIPS):
            col = ctk.CTkFrame(f, fg_color=S, corner_radius=14,
                               border_width=1, border_color=BD)
            col.grid(row=0, column=i, padx=5, sticky="nsew")
            f.columnconfigure(i, weight=1)

            ico = ico_cup(22, chip["kind"], A2)
            ic_lbl = ctk.CTkLabel(col, image=ico, text="")
            ic_lbl.pack(pady=(10, 2))
            ic_lbl._img = ico

            ctk.CTkLabel(col, text=chip["label"], text_color=T,
                         font=(FONT, 11, "bold")).pack()
            ctk.CTkLabel(col, text=f"{chip['ml']} ml", text_color=M,
                         font=(FONT, 10)).pack(pady=(0, 8))

            # bind click
            ml_val = chip["ml"]
            for w2 in [col] + col.winfo_children():
                w2.bind("<Button-1>", lambda e, ml=ml_val: self._add_water(ml))
                w2.bind("<Enter>",    lambda e, c=col: c.configure(border_color=AC))
                w2.bind("<Leave>",    lambda e, c=col: c.configure(border_color=BD))

    def _manual_row(self):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        f.pack(fill="x", padx=24, pady=(12, 0))

        inp_frame = ctk.CTkFrame(f, fg_color=IN, corner_radius=13,
                                  border_width=1, border_color=BD)
        inp_frame.pack(side="left", fill="x", expand=True)

        drop_img = ico_drop(16, FA)
        drop_lbl = ctk.CTkLabel(inp_frame, image=drop_img, text="",
                                 fg_color="transparent")
        drop_lbl.pack(side="left", padx=(12, 4))
        drop_lbl._img = drop_img

        self._manual_entry = ctk.CTkEntry(inp_frame, placeholder_text="quantidade em ml",
                                           fg_color="transparent", border_width=0,
                                           text_color=T, placeholder_text_color=FA,
                                           font=(FONT, 14, "bold"), width=160)
        self._manual_entry.pack(side="left", ipady=6)

        ctk.CTkLabel(inp_frame, text="ml", text_color=M,
                     font=(FONT, 12, "bold")).pack(side="right", padx=12)

        add_img = ico_drop(14, "#ffffff")
        add_btn = ctk.CTkButton(f, text="Adicionar", image=add_img, compound="left",
                                 width=110, height=44, corner_radius=13,
                                 fg_color=AC, hover_color=A2,
                                 font=(FONT, 13, "bold"),
                                 command=self._add_manual)
        add_btn.pack(side="left", padx=(10, 0))
        add_btn._img = add_img
        self._manual_entry.bind("<Return>", lambda e: self._add_manual())

    def _streak_card(self):
        card = ctk.CTkFrame(self._content, fg_color=S, corner_radius=18,
                             border_width=1, border_color=BD)
        card.pack(fill="x", padx=24, pady=(14, 0))

        # cabeçalho
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=16, pady=(14, 8))

        flame_box = ctk.CTkFrame(head, width=40, height=40, corner_radius=12,
                                  fg_color="#1c1108")
        flame_box.pack(side="left")
        flame_box.pack_propagate(False)
        fl_img = ico_flame(22, FL)
        fl_lbl = ctk.CTkLabel(flame_box, image=fl_img, text="")
        fl_lbl.place(relx=.5, rely=.5, anchor="center")
        fl_lbl._img = fl_img

        txt_col = ctk.CTkFrame(head, fg_color="transparent")
        txt_col.pack(side="left", padx=(12, 0))
        self._streak_num_lbl = ctk.CTkLabel(txt_col, text="", text_color=T,
                                             font=(FONT, 16, "bold"))
        self._streak_num_lbl.pack(anchor="w")
        self._streak_sub_lbl = ctk.CTkLabel(txt_col, text="dias seguidos",
                                             text_color=M, font=(FONT, 11))
        self._streak_sub_lbl.pack(anchor="w")

        self._best_lbl = ctk.CTkLabel(head, text="", text_color=FA,
                                       font=(FONT, 10))
        self._best_lbl.pack(side="right")

        # faixa dos 7 dias
        week_f = ctk.CTkFrame(card, fg_color="transparent")
        week_f.pack(fill="x", padx=16, pady=(0, 14))
        self._week_frame = week_f

    def _footer(self):
        f = ctk.CTkFrame(self._content, fg_color="transparent")
        f.pack(pady=(10, 18))
        rst_img = ico_reset(14, FA)
        btn = ctk.CTkButton(f, text="Resetar dia", image=rst_img, compound="left",
                             fg_color="transparent", hover_color=S,
                             text_color=FA, font=(FONT, 12, "bold"),
                             corner_radius=8, command=self._reset_day)
        btn.pack()
        btn._img = rst_img

    # ── actions ───────────────────────────────────────────────────────────────
    def _add_water(self, ml: int):
        self._state.add_water(ml)

    def _add_manual(self):
        raw = self._manual_entry.get().strip()
        try:
            ml = max(1, min(9999, int(raw)))
            self._state.add_water(ml)
            self._manual_entry.delete(0, "end")
        except ValueError:
            pass

    def _reset_day(self):
        self._state.reset_day()

    def _open_config(self):
        ConfigDialog(self, self._state)

    # ── poll loop ─────────────────────────────────────────────────────────────
    def _poll(self):
        s = self._state

        # hero
        self._hero_lbl.configure(text=f"{s.consumed_ml} ml / {s.goal_ml} ml")
        pct = int(s.percent() * 100)
        self._sub_lbl.configure(
            text="Meta diaria atingida!" if s.goal_reached
            else f"{pct}% da meta diaria"
        )

        # countdown no titlebar
        rem = self._timer.time_remaining()
        m, sec = divmod(rem, 60)
        cd_col = RE if rem < 60 and not s.goal_reached else FA
        cd_txt = "Meta atingida!" if s.goal_reached else f"Proximo lembrete: {m:02d}:{sec:02d}"
        self._cd_lbl.configure(text=cd_txt, text_color=cd_col)

        # streak
        streak = s.streak()
        self._streak_num_lbl.configure(text=str(streak))
        best = max(s.best_streak, streak)
        self._best_lbl.configure(text=f"Recorde: {best} dias")

        # 7 círculos
        self._rebuild_week(s)

        # celebração ao atingir meta
        if s.goal_reached and not self._prev_goal:
            self._notifier.fire_success(s)
        self._prev_goal = s.goal_reached

        self.after(400, self._poll)

    def _rebuild_week(self, s: AppState):
        for w in self._week_frame.winfo_children():
            w.destroy()

        days = s.last_7_days()
        for i, d in enumerate(days):
            col = ctk.CTkFrame(self._week_frame, fg_color="transparent")
            col.grid(row=0, column=i, padx=4)
            self._week_frame.columnconfigure(i, weight=1)

            status = d["status"]
            c_bg, c_ring, c_txt = self._day_colors(status, s)

            ring_cv = tk.Canvas(col, width=36, height=36, bg=_rgb_css(_rgb(S)),
                                highlightthickness=0)
            ring_cv.pack()
            ring_cv.create_oval(2, 2, 34, 34, fill=c_bg, outline=c_ring, width=2)

            if status == "done":
                chk = ico_check(12, "#ffffff")
                ring_cv.create_image(18, 18, image=chk)
                ring_cv._img = chk
            elif status == "today":
                p = int(s.percent() * 100)
                ring_cv.create_text(18, 18, text=f"{p}%", fill=c_txt,
                                    font=(FONT, 8, "bold"))
            else:
                ring_cv.create_text(18, 18, text="·", fill=c_txt,
                                    font=(FONT, 16))

            ctk.CTkLabel(col, text=d["label"], text_color=M,
                         font=(FONT, 10, "bold")).pack(pady=(2, 0))

    def _day_colors(self, status: str, s: AppState):
        if status == "done":
            return AC, A2, "#ffffff"
        elif status == "today":
            ring = (30, 200, 100) if s.goal_reached else AC
            return S2, _rgb_css(ring), A2
        else:
            return S, BD, FA

    def _on_close(self):
        self._timer.stop()
        self._state.save()
        self.destroy()

    def run(self):
        self.mainloop()
