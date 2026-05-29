"""
Contador de Água v4
- Garrafa: Pillow render (fiel ao bottle.jsx, gradiente, wave, clip)
- Ícones: icons.py (Lucide via Pillow 4× supersampling, sem Cairo)
- Week strip: Canvas in-place (sem blink)
- Tema: dark / light toggle
"""
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import math, time

from state import AppState
from timer_manager import TimerManager
from notifier import Notifier
from icons import get_icon, clear_cache

ctk.set_appearance_mode("dark")

# ── Temas ──────────────────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "win_bg":       "#0d1424",
        "titlebar":     "#0c1222",
        "surface":      "#111827",
        "surface2":     "#1a2540",
        "border":       "#1e2d4a",
        "text":         "#eef2fb",
        "muted":        "#8a96ad",
        "faint":        "#5b6478",
        "accent":       "#2563eb",
        "accent2":      "#3b82f6",
        "water_top":    "#38bdf8",
        "water_bot":    "#2563eb",
        "flame":        "#f97316",
        "cap":          "#2a3650",
        "glass_fill":   "#0f1e38",
        "glass_stroke": "#1e3a5c",
        "glass_shine":  "#1c2f4a",
        "ring_track":   "#1e2d4a",
        "input_bg":     "#0f1826",
        "chip_bg":      "#111827",
        "red":          "#ef4444",
        "flame_box":    "#1c1108",
    },
    "light": {
        "win_bg":       "#f7f9fd",
        "titlebar":     "#eef3fb",
        "surface":      "#ffffff",
        "surface2":     "#f1f5fb",
        "border":       "#d1dded",
        "text":         "#0f1b33",
        "muted":        "#64748b",
        "faint":        "#94a3b8",
        "accent":       "#2563eb",
        "accent2":      "#3b82f6",
        "water_top":    "#38bdf8",
        "water_bot":    "#2563eb",
        "flame":        "#f97316",
        "cap":          "#c7d6ee",
        "glass_fill":   "#daeeff",
        "glass_stroke": "#93c5fd",
        "glass_shine":  "#ffffff",
        "ring_track":   "#d1dded",
        "input_bg":     "#ffffff",
        "chip_bg":      "#ffffff",
        "red":          "#ef4444",
        "flame_box":    "#fff4e6",
    },
}

FONT  = "Segoe UI"
CHIPS = [
    {"ml": 200, "label": "Copo",    "icon": "glass-water"},  # copo vazio c/ linha
    {"ml": 250, "label": "Gole",    "icon": "droplet"},       # gota de água
    {"ml": 500, "label": "Dose",    "icon": "cup-filled"},    # copo c/ água visível
    {"ml": 750, "label": "Garrafa", "icon": "bottle-water"},  # garrafa
]


def _rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def _lerp_c(c1, c2, t):
    return tuple(round(c1[i] + (c2[i]-c1[i])*t) for i in range(3))


# ── Garrafa (Pillow, fiel ao bottle.jsx) ──────────────────────────────────────
class BottleWidget(tk.Label):
    """
    Garrafa animada renderizada frame-a-frame com Pillow.
    Geometria: viewBox 0 0 220 360, interior x=30 w=160 top=64 bottom=318 rx=34.
    """
    CW, CH = 220, 320   # canvas pixels

    def __init__(self, master, state: AppState, theme_fn, **kw):
        super().__init__(master, bd=0, highlightthickness=0, **kw)
        self._state   = state
        self._theme   = theme_fn
        self._phase   = 0.0
        self._photo   = None
        self._animate()

    def _animate(self):
        self._phase = (self._phase + 0.055) % (2 * math.pi)
        self._render()
        self.after(50, self._animate)

    def _render(self):
        th  = THEMES[self._theme()]
        pct = self._state.percent()
        fls = time.time() < self._state.flash_until
        W, H = self.CW, self.CH

        # Escala do viewBox original (220×360) para o canvas (220×320)
        sx = lambda v: round(v * W / 220)
        sy = lambda v: round(v * H / 360)

        bg = _rgb(th["win_bg"])
        img = Image.new("RGBA", (W, H), (*bg, 255))
        d   = ImageDraw.Draw(img)

        bx1, by1 = sx(30), sy(64)
        bx2, by2 = sx(190), sy(318)
        brx = sx(34)

        # ── tampa ─────────────────────────────────────────────────────────────
        cap_c = _rgb(th["cap"])
        d.rounded_rectangle([sx(92), sy(22), sx(128), sy(44)],
                             radius=sx(6), fill=cap_c)
        d.rounded_rectangle([sx(84), sy(40), sx(136), sy(66)],
                             radius=sx(9), fill=cap_c)

        # ── corpo glass fill ──────────────────────────────────────────────────
        d.rounded_rectangle([bx1, by1, bx2, by2],
                             radius=brx, fill=_rgb(th["glass_fill"]))

        # ── água ──────────────────────────────────────────────────────────────
        if pct > 0.005:
            water_y = by2 - round((by2-by1) * min(1.0, pct))
            amp     = max(3, round((by2-by1) * 0.022))
            freq    = 2*math.pi / max(1, bx2-bx1) * 3

            # Máscara recortada ao rounded rect
            mask = Image.new("L", (W, H), 0)
            ImageDraw.Draw(mask).rounded_rectangle(
                [bx1, by1, bx2, by2], radius=brx, fill=255)

            # Gradiente de água
            wt, wb = _rgb(th["water_top"]), _rgb(th["water_bot"])
            grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            gd   = ImageDraw.Draw(grad)
            total = max(1, by2 - water_y)
            for iy in range(water_y, by2 + 1):
                t = min(1.0, (iy - water_y) / total)
                c = _lerp_c(wt, wb, t)
                gd.line([(bx1, iy), (bx2, iy)], fill=(*c, 255))
            img.paste(grad, mask=mask)

            # Onda 1 (mais clara, na frente)
            wave1 = []
            for x in range(bx1, bx2+1):
                y = water_y + round(amp * math.sin((x-bx1)*freq + self._phase))
                y = max(by1+2, min(by2-2, y))
                wave1.append((x, y))
            wave1 += [(bx2, by2), (bx1, by2)]
            ov1 = Image.new("RGBA", (W, H), (0,0,0,0))
            ImageDraw.Draw(ov1).polygon(wave1, fill=(*wt, 100))
            img.paste(ov1, mask=mask)

            # Onda 2 (mais escura, atrás, desfasada π)
            wave2 = []
            for x in range(bx1, bx2+1):
                y = water_y+2 + round(amp*0.6*math.sin(
                    (x-bx1)*freq + self._phase + math.pi))
                y = max(by1+2, min(by2-2, y))
                wave2.append((x, y))
            wave2 += [(bx2, by2), (bx1, by2)]
            ov2 = Image.new("RGBA", (W, H), (0,0,0,0))
            ImageDraw.Draw(ov2).polygon(wave2, fill=(*_lerp_c(wb,wt,0.3), 80))
            img.paste(ov2, mask=mask)

        # ── shine (reflexo lateral) ───────────────────────────────────────────
        shine_a = 45 if self._theme() == "dark" else 110
        sh = Image.new("RGBA", (W, H), (0,0,0,0))
        ImageDraw.Draw(sh).rounded_rectangle(
            [sx(44), sy(86), sx(58), sy(296)],
            radius=sx(7),
            fill=(*_rgb(th["glass_shine"]), shine_a))
        img.alpha_composite(sh)

        # ── borda do corpo ────────────────────────────────────────────────────
        stroke_c = _rgb(th["red"] if fls else th["glass_stroke"])
        d.rounded_rectangle([bx1, by1, bx2, by2],
                             radius=brx, outline=stroke_c, width=2)

        # ── ticks laterais (texto não suporta font customizada sem PIL.font) ──
        tx = sx(206)
        for frac, label in [(0.0,"0"),(0.5,str(self._state.goal_ml//2)),
                             (1.0,str(self._state.goal_ml))]:
            ty = by2 - round((by2-by1)*frac)
            d.line([(sx(190), ty), (tx, ty)], fill=_rgb(th["faint"]), width=1)
            d.text((tx+3, ty-6), f"{label} ml", fill=_rgb(th["faint"]))

        # ── badge % ───────────────────────────────────────────────────────────
        pct_str = f"{int(pct*100)}%"
        pcx     = W//2
        pcy     = sy(50)
        pill_w, pill_h = 50, 20
        pill = Image.new("RGBA", (W, H), (0,0,0,0))
        pd   = ImageDraw.Draw(pill)
        pd.rounded_rectangle(
            [pcx-pill_w//2, pcy-pill_h//2, pcx+pill_w//2, pcy+pill_h//2],
            radius=pill_h//2, fill=(*bg,230),
            outline=_rgb(th["accent"]), width=2)
        pd.text((pcx-pill_w//2+8, pcy-6), pct_str, fill=_rgb(th["accent"]))
        img.alpha_composite(pill)

        photo = ImageTk.PhotoImage(img)
        self.configure(image=photo, bg=th["win_bg"])
        self._photo = photo


# ── Config Dialog ──────────────────────────────────────────────────────────────
class ConfigDialog(ctk.CTkToplevel):
    FIELDS = [
        ("Meta diaria (ml)",            "goal_ml",       100, 10000),
        ("Intervalo de lembrete (min)", "interval_min",    1,   480),
        ("Volume do copo rapido (ml)",  "default_cup_ml", 50,  2000),
    ]

    def __init__(self, master, state: AppState, th: dict):
        super().__init__(master)
        self._state = state
        self.title("Configuracoes")
        self.geometry("360x320")
        self.resizable(False, False)
        self.configure(fg_color=th["win_bg"])
        self.grab_set()
        self._entries: list[ctk.CTkEntry] = []

        for i, (lbl, attr, lo, hi) in enumerate(self.FIELDS):
            ctk.CTkLabel(self, text=lbl, text_color=th["muted"],
                         font=(FONT,12)).pack(anchor="w", padx=28,
                                              pady=(16 if i==0 else 8, 2))
            e = ctk.CTkEntry(self, width=300,
                             fg_color=th["input_bg"], border_color=th["border"],
                             text_color=th["text"], font=(FONT,14,"bold"))
            e.insert(0, str(getattr(state, attr)))
            e.pack(padx=28)
            self._entries.append(e)

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(pady=20)
        ctk.CTkButton(row, text="Salvar", width=130, corner_radius=10,
                      fg_color=th["accent"], hover_color=th["accent2"],
                      font=(FONT,13,"bold"),
                      command=self._save).pack(side="left", padx=6)
        ctk.CTkButton(row, text="Cancelar", width=130, corner_radius=10,
                      fg_color=th["surface"], border_width=1,
                      border_color=th["border"], hover_color=th["surface2"],
                      text_color=th["muted"], font=(FONT,13),
                      command=self.destroy).pack(side="left", padx=6)

    def _save(self):
        try:
            vals = [int(e.get()) for e in self._entries]
            for (_, attr, lo, hi), v in zip(self.FIELDS, vals):
                if not (lo <= v <= hi): return
                setattr(self._state, attr, v)
            self._state.save()
            self.destroy()
        except ValueError:
            pass


# ── App ────────────────────────────────────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._theme_name  = "dark"
        self._state       = AppState.load()
        self._notifier    = Notifier()
        self._notifier.load_sounds()
        self._timer       = TimerManager(self._state, self._notifier)
        self._prev_goal   = self._state.goal_reached
        self._day_rings:  list[tk.Canvas]    = []
        self._day_labels: list[ctk.CTkLabel] = []
        self._hero_lbl    = self._sub_lbl = self._cd_lbl = None
        self._streak_num  = self._streak_sub = self._best_lbl = None
        self._build()
        self._timer.start()
        self._poll()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _th(self): return THEMES[self._theme_name]
    def _ts(self): return self._theme_name

    # ── build ─────────────────────────────────────────────────────────────────
    def _build(self):
        th = self._th()
        self.title("Contador de Agua")
        self.geometry("440x780")
        self.resizable(False, False)
        self.configure(fg_color=th["win_bg"])
        self._build_titlebar()
        self._scroll = ctk.CTkScrollableFrame(
            self, fg_color=th["win_bg"],
            scrollbar_button_color=th["border"],
            scrollbar_button_hover_color=th["surface2"])
        self._scroll.pack(fill="both", expand=True)
        self._build_hero()
        self._build_bottle()
        self._build_chips()
        self._build_manual()
        self._build_streak()
        self._build_footer()

    def _build_titlebar(self):
        th  = self._th()
        bar = ctk.CTkFrame(self, height=48, fg_color=th["titlebar"],
                           corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        left = ctk.CTkFrame(bar, fg_color="transparent")
        left.pack(side="left", padx=14)
        dot = ctk.CTkFrame(left, width=26, height=26, corner_radius=7,
                           fg_color=th["accent"])
        dot.pack(side="left")
        dot.pack_propagate(False)
        d_ico = get_icon("droplet", 14, "#ffffff")
        d_lbl = ctk.CTkLabel(dot, image=d_ico, text="")
        d_lbl.place(relx=.5, rely=.5, anchor="center")
        d_lbl._img = d_ico
        ctk.CTkLabel(left, text="  Contador de Agua",
                     text_color=th["text"], font=(FONT,13,"bold")).pack(side="left")

        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.pack(side="right", padx=10)

        # Botão tema (sol / lua)
        t_ico_name = "moon" if self._theme_name == "dark" else "sun"
        t_ico = get_icon(t_ico_name, 16, th["muted"])
        self._theme_btn = ctk.CTkButton(
            right, image=t_ico, text="", width=34, height=34,
            corner_radius=10, fg_color=th["surface"],
            border_width=1, border_color=th["border"],
            hover_color=th["surface2"], command=self._toggle_theme)
        self._theme_btn.pack(side="right", padx=3)
        self._theme_btn._img = t_ico

        # Botão config
        c_ico = get_icon("settings", 16, th["muted"])
        c_btn = ctk.CTkButton(
            right, image=c_ico, text="", width=34, height=34,
            corner_radius=10, fg_color=th["surface"],
            border_width=1, border_color=th["border"],
            hover_color=th["surface2"], command=self._open_config)
        c_btn.pack(side="right", padx=3)
        c_btn._img = c_ico

        self._cd_lbl = ctk.CTkLabel(right, text="", text_color=th["faint"],
                                     font=(FONT,11))
        self._cd_lbl.pack(side="right", padx=8)

    def _build_hero(self):
        th = self._th()
        f  = ctk.CTkFrame(self._scroll, fg_color="transparent")
        f.pack(fill="x", padx=24, pady=(18,0))
        self._hero_lbl = ctk.CTkLabel(f, text="0 ml / 0 ml",
                                       text_color=th["text"],
                                       font=(FONT,40,"bold"))
        self._hero_lbl.pack()
        self._sub_lbl = ctk.CTkLabel(f, text="", text_color=th["muted"],
                                      font=(FONT,13))
        self._sub_lbl.pack()

    def _build_bottle(self):
        f = ctk.CTkFrame(self._scroll, fg_color="transparent")
        f.pack(pady=(4,0))
        self._bottle = BottleWidget(f, self._state, self._ts)
        self._bottle.pack()

    def _build_chips(self):
        th = self._th()
        f  = ctk.CTkFrame(self._scroll, fg_color="transparent")
        f.pack(fill="x", padx=24, pady=(12,0))
        for i, chip in enumerate(CHIPS):
            col = ctk.CTkFrame(f, fg_color=th["chip_bg"], corner_radius=14,
                               border_width=1, border_color=th["border"])
            col.grid(row=0, column=i, padx=4, sticky="nsew")
            f.columnconfigure(i, weight=1)
            ico = get_icon(chip["icon"], 20, th["accent"])
            il  = ctk.CTkLabel(col, image=ico, text="")
            il.pack(pady=(10,2))
            il._img = ico
            ctk.CTkLabel(col, text=chip["label"], text_color=th["text"],
                         font=(FONT,11,"bold")).pack()
            ctk.CTkLabel(col, text=f'+{chip["ml"]} ml',
                         text_color=th["muted"], font=(FONT,10)).pack(pady=(0,8))
            ml = chip["ml"]
            for w in [col]+list(col.winfo_children()):
                w.bind("<Button-1>", lambda e, v=ml: self._add_water(v))
                w.bind("<Enter>",   lambda e, c=col: c.configure(border_color=th["accent"]))
                w.bind("<Leave>",   lambda e, c=col: c.configure(border_color=th["border"]))

    def _build_manual(self):
        th = self._th()
        f  = ctk.CTkFrame(self._scroll, fg_color="transparent")
        f.pack(fill="x", padx=24, pady=(12,0))
        inp = ctk.CTkFrame(f, fg_color=th["input_bg"], corner_radius=13,
                           border_width=1, border_color=th["border"])
        inp.pack(side="left", fill="x", expand=True)
        di  = get_icon("droplet", 14, th["faint"])
        dl  = ctk.CTkLabel(inp, image=di, text="", fg_color="transparent")
        dl.pack(side="left", padx=(12,4))
        dl._img = di
        self._manual_entry = ctk.CTkEntry(
            inp, placeholder_text="Quantidade",
            fg_color="transparent", border_width=0,
            text_color=th["text"], placeholder_text_color=th["faint"],
            font=(FONT,14,"bold"), width=160)
        self._manual_entry.pack(side="left", ipady=6)
        ctk.CTkLabel(inp, text="ml", text_color=th["muted"],
                     font=(FONT,12,"bold")).pack(side="right", padx=12)
        ai  = get_icon("droplet", 14, "#ffffff")
        ab  = ctk.CTkButton(f, text="Adicionar", image=ai, compound="left",
                             width=110, height=44, corner_radius=13,
                             fg_color=th["accent"], hover_color=th["accent2"],
                             font=(FONT,13,"bold"), command=self._add_manual)
        ab.pack(side="left", padx=(10,0))
        ab._img = ai
        self._manual_entry.bind("<Return>", lambda e: self._add_manual())

    def _build_streak(self):
        th   = self._th()
        card = ctk.CTkFrame(self._scroll, fg_color=th["surface"],
                             corner_radius=18, border_width=1,
                             border_color=th["border"])
        card.pack(fill="x", padx=24, pady=(14,0))

        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=16, pady=(14,8))

        fb  = ctk.CTkFrame(head, width=40, height=40, corner_radius=12,
                           fg_color=th["flame_box"])
        fb.pack(side="left")
        fb.pack_propagate(False)
        fi  = get_icon("flame", 22, th["flame"])
        fl  = ctk.CTkLabel(fb, image=fi, text="")
        fl.place(relx=.5, rely=.5, anchor="center")
        fl._img = fi

        tc = ctk.CTkFrame(head, fg_color="transparent")
        tc.pack(side="left", padx=(12,0))
        self._streak_num = ctk.CTkLabel(tc, text="0", text_color=th["text"],
                                         font=(FONT,16,"bold"))
        self._streak_num.pack(anchor="w")
        self._streak_sub = ctk.CTkLabel(tc, text="dias seguidos",
                                         text_color=th["muted"], font=(FONT,11))
        self._streak_sub.pack(anchor="w")
        self._best_lbl = ctk.CTkLabel(head, text="", text_color=th["faint"],
                                       font=(FONT,10))
        self._best_lbl.pack(side="right")

        # 7 círculos criados UMA VEZ
        wf = ctk.CTkFrame(card, fg_color="transparent")
        wf.pack(fill="x", padx=16, pady=(0,14))
        self._day_rings  = []
        self._day_labels = []
        for i in range(7):
            col = ctk.CTkFrame(wf, fg_color="transparent")
            col.grid(row=0, column=i, padx=4)
            wf.columnconfigure(i, weight=1)
            ring = tk.Canvas(col, width=36, height=36,
                             bg=th["surface"], highlightthickness=0)
            ring.pack()
            self._day_rings.append(ring)
            lbl = ctk.CTkLabel(col, text="", text_color=th["muted"],
                               font=(FONT,10,"bold"))
            lbl.pack(pady=(2,0))
            self._day_labels.append(lbl)

    def _build_footer(self):
        th  = self._th()
        f   = ctk.CTkFrame(self._scroll, fg_color="transparent")
        f.pack(pady=(10,18))
        ri  = get_icon("refresh-ccw", 13, th["faint"])
        btn = ctk.CTkButton(f, text="Resetar dia", image=ri, compound="left",
                             fg_color="transparent", hover_color=th["surface"],
                             text_color=th["faint"], font=(FONT,12,"bold"),
                             corner_radius=8, command=self._reset_day)
        btn.pack()
        btn._img = ri

    # ── poll (400ms, sem destruir widgets) ────────────────────────────────────
    def _poll(self):
        s  = self._state
        th = self._th()
        if not self._hero_lbl:
            self.after(400, self._poll)
            return

        self._hero_lbl.configure(text=f"{s.consumed_ml} ml / {s.goal_ml} ml")
        pct = int(s.percent() * 100)
        if s.goal_reached:
            self._sub_lbl.configure(text="Meta diaria atingida!",
                                    text_color=th["accent"])
        else:
            rem = max(0, s.goal_ml - s.consumed_ml)
            self._sub_lbl.configure(
                text=f"{pct}% da meta diaria  ·  faltam {rem} ml",
                text_color=th["muted"])

        rem_s = self._timer.time_remaining()
        m, sc = divmod(rem_s, 60)
        if s.goal_reached:
            cd_t, cd_c = "Meta atingida!", th["accent"]
        else:
            cd_t = f"Proximo lembrete: {m:02d}:{sc:02d}"
            cd_c = th["red"] if rem_s < 60 else th["faint"]
        self._cd_lbl.configure(text=cd_t, text_color=cd_c)

        streak = s.streak()
        best   = max(s.best_streak, streak)
        self._streak_num.configure(text=str(streak))
        self._best_lbl.configure(text=f"Recorde: {best} dias")

        self._update_week(s, th)

        if s.goal_reached and not self._prev_goal:
            self._notifier.fire_success(s)
        self._prev_goal = s.goal_reached

        self.after(500, self._poll)

    def _update_week(self, s: AppState, th: dict):
        days = s.last_7_days()
        for i, day in enumerate(days):
            if i >= len(self._day_rings):
                break
            ring  = self._day_rings[i]
            label = self._day_labels[i]
            st    = day["status"]

            ring.delete("all")
            ring.configure(bg=th["surface"])
            label.configure(text=day["label"])

            if st == "done":
                ring.create_oval(2,2,34,34,
                                 fill=th["accent"], outline=th["accent2"], width=2)
                chk = get_icon("check", 14, "#ffffff", for_canvas=True)
                ring.create_image(18, 18, image=chk)
                ring._chk = chk
                label.configure(text_color=th["accent"])
            elif st == "today":
                ring_c = "#1ec864" if s.goal_reached else th["accent"]
                ring.create_oval(2,2,34,34,
                                 fill=th["surface2"], outline=ring_c, width=2)
                ring.create_text(18, 18,
                                 text=f"{int(s.percent()*100)}%",
                                 fill=ring_c, font=(FONT,8,"bold"))
                label.configure(text_color=th["accent"])
            else:
                ring.create_oval(2,2,34,34,
                                 fill=th["surface"], outline=th["ring_track"], width=1)
                ring.create_text(18, 18, text="·",
                                 fill=th["faint"], font=(FONT,16))
                label.configure(text_color=th["muted"])

    # ── tema ──────────────────────────────────────────────────────────────────
    def _toggle_theme(self):
        self._theme_name = "light" if self._theme_name == "dark" else "dark"
        ctk.set_appearance_mode(self._theme_name)
        clear_cache()
        for w in self.winfo_children():
            w.destroy()
        self._day_rings  = []
        self._day_labels = []
        self._build()
        self._poll()

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
        ConfigDialog(self, self._state, self._th())

    def _on_close(self):
        self._timer.stop()
        self._state.save()
        self.destroy()

    def run(self):
        self.mainloop()
