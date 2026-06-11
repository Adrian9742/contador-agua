"""
Histórico visual dos últimos 30 dias — gráfico de barras renderizado com Pillow
"""
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk
from datetime import date, timedelta
from state import AppState

FONT = "Segoe UI"

_PIL_FONT_CACHE: dict = {}


def _pil_font(size: int) -> ImageFont.FreeTypeFont:
    if size not in _PIL_FONT_CACHE:
        for path in [
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]:
            try:
                _PIL_FONT_CACHE[size] = ImageFont.truetype(path, size)
                break
            except Exception:
                pass
        else:
            _PIL_FONT_CACHE[size] = ImageFont.load_default()
    return _PIL_FONT_CACHE[size]


def _rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


class HistoryDialog(ctk.CTkToplevel):
    CW, CH = 650, 285  # dimensões da imagem do gráfico

    def __init__(self, master, state: AppState, th: dict):
        super().__init__(master)
        self._state = state
        self._th = th
        self.title("Histórico de Hidratação")
        self.geometry("720x570")
        self.resizable(False, False)
        self.configure(fg_color=th["win_bg"])
        self.grab_set()
        self._build()

    # ── Layout principal ──────────────────────────────────────────────────────
    def _build(self):
        th = self._th

        ctk.CTkLabel(
            self, text="Histórico — Últimos 30 Dias",
            text_color=th["text"], font=(FONT, 18, "bold"),
        ).pack(pady=(22, 2))
        ctk.CTkLabel(
            self, text="Consumo diário de água vs meta",
            text_color=th["muted"], font=(FONT, 12),
        ).pack(pady=(0, 12))

        chart_img = self._render_chart()
        chart_lbl = tk.Label(
            self, image=chart_img, bd=0, highlightthickness=0,
            bg=th["win_bg"],
        )
        chart_lbl.pack(padx=30)
        chart_lbl._img = chart_img

        self._build_legend()
        self._build_stats()

        ctk.CTkButton(
            self, text="Fechar", width=120, corner_radius=10,
            fg_color=th["surface"], border_width=1, border_color=th["border"],
            text_color=th["muted"], hover_color=th["surface2"],
            font=(FONT, 13), command=self.destroy,
        ).pack(pady=(6, 18))

    # ── Legenda ───────────────────────────────────────────────────────────────
    def _build_legend(self):
        th = self._th
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(pady=(6, 0))
        for color, label in [
            (th["accent"], "Meta atingida"),
            (th["flame"],  "Parcial"),
            (th["faint"],  "Sem dados"),
        ]:
            dot = ctk.CTkFrame(row, width=12, height=12,
                               corner_radius=3, fg_color=color)
            dot.pack(side="left", padx=(14, 4))
            ctk.CTkLabel(row, text=label, text_color=th["muted"],
                         font=(FONT, 11)).pack(side="left", padx=(0, 8))

    # ── Cards de estatísticas ─────────────────────────────────────────────────
    def _build_stats(self):
        th = self._th
        s  = self._state
        days_data      = self._get_30_days()
        days_with_data = [d for d in days_data if d["consumed"] > 0]
        days_goal_met  = sum(1 for d in days_data
                             if d["consumed"] >= d["goal"])
        avg = int(
            sum(d["consumed"] for d in days_with_data)
            / max(1, len(days_with_data))
        )
        streak = s.streak()
        best   = max(s.best_streak, streak)

        stats = [
            ("Meta atingida", f"{days_goal_met}/30 dias"),
            ("Média diária",  f"{avg} ml"),
            ("Streak atual",  f"{streak} dias"),
            ("Melhor streak", f"{best} dias"),
        ]
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=28, pady=(10, 0))
        for i, (label, value) in enumerate(stats):
            card = ctk.CTkFrame(row, fg_color=th["surface"],
                               corner_radius=12, border_width=1,
                               border_color=th["border"])
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            row.columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=value, text_color=th["text"],
                        font=(FONT, 15, "bold")).pack(pady=(12, 2))
            ctk.CTkLabel(card, text=label, text_color=th["muted"],
                        font=(FONT, 10)).pack(pady=(0, 10))

    # ── Dados dos 30 dias ─────────────────────────────────────────────────────
    def _get_30_days(self) -> list:
        s     = self._state
        today = date.today()
        result = []
        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            if i == 0:
                result.append({
                    "date": d, "consumed": s.consumed_ml,
                    "goal": s.goal_ml, "is_today": True,
                })
            else:
                entry = s.daily_history.get(d.isoformat())
                if entry:
                    result.append({
                        "date": d, "consumed": entry["consumed"],
                        "goal": entry["goal"], "is_today": False,
                    })
                else:
                    result.append({
                        "date": d, "consumed": 0,
                        "goal": s.goal_ml, "is_today": False,
                    })
        return result

    # ── Renderização do gráfico com Pillow ────────────────────────────────────
    def _render_chart(self) -> ImageTk.PhotoImage:
        th = self._th
        f9  = _pil_font(9)
        f10 = _pil_font(10)

        W, H     = self.CW, self.CH
        ML, MR   = 56, 50   # margem esquerda (labels eixo y) e direita (label meta)
        MT, MB   = 16, 42   # margem superior e inferior (labels eixo x)
        cx1, cx2 = ML, W - MR
        cy1, cy2 = MT, H - MB
        cw       = cx2 - cx1
        ch       = cy2 - cy1

        bg  = _rgb(th["win_bg"])
        img = Image.new("RGBA", (W, H), (*bg, 255))
        d   = ImageDraw.Draw(img)

        days  = self._get_30_days()
        goals = [dd["goal"] for dd in days]
        cons  = [dd["consumed"] for dd in days]
        y_max = max(max(goals, default=2000), max(cons, default=0)) * 1.2

        def y_px(ml: float) -> int:
            return cy2 - round(ml / y_max * ch)

        border_c = _rgb(th["border"])
        faint_c  = _rgb(th["faint"])
        acc_c    = _rgb(th["accent"])
        flame_c  = _rgb(th["flame"])

        # grade horizontal + labels eixo y
        for frac in (0.25, 0.5, 0.75, 1.0):
            gy  = y_px(y_max * frac)
            lbl = f"{int(y_max * frac)}"
            d.line([(cx1, gy), (cx2, gy)], fill=(*border_c, 70), width=1)
            d.text((cx1 - 4, gy), lbl, fill=faint_c, font=f9, anchor="rm")

        # linha de meta tracejada
        goal_y = y_px(days[-1]["goal"])
        for x in range(cx1, cx2, 8):
            d.line([(x, goal_y), (min(x + 5, cx2), goal_y)],
                   fill=(*acc_c, 180), width=1)
        d.text((cx2 + 4, goal_y), "Meta", fill=acc_c, font=f9, anchor="lm")

        # barras
        slot = cw / len(days)
        gap  = max(1, round(slot * 0.20))
        bw   = max(2, round(slot - gap))

        for i, dd in enumerate(days):
            bx1 = cx1 + round(i * slot) + gap // 2
            bx2 = bx1 + bw
            mid = (bx1 + bx2) // 2

            if dd["consumed"] == 0:
                d.rectangle([bx1, cy2 - 3, bx2, cy2], fill=(*faint_c, 90))
            else:
                top_y = y_px(dd["consumed"])
                color = acc_c if dd["consumed"] >= dd["goal"] else flame_c
                d.rectangle([bx1, top_y + 3, bx2, cy2], fill=(*color, 210))
                d.ellipse([bx1, top_y, bx2, top_y + 7], fill=(*color, 210))

            # label eixo x
            if dd["is_today"]:
                d.text((mid, cy2 + 6), "Hoje", fill=acc_c, font=f9, anchor="mt")
            elif i % 5 == 0:
                d.text((mid, cy2 + 6), dd["date"].strftime("%d/%m"),
                       fill=faint_c, font=f9, anchor="mt")

        # eixos
        d.line([(cx1, cy1), (cx1, cy2)], fill=border_c, width=1)
        d.line([(cx1, cy2), (cx2, cy2)], fill=border_c, width=1)

        return ImageTk.PhotoImage(img)
