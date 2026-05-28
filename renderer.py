import math
import random
import time
from datetime import date, timedelta
import pygame

# ── Paleta ────────────────────────────────────────────────────────────────────
BG              = (232, 243, 255)
BG_GOAL         = (220, 245, 232)
BOTTLE_BG       = (210, 230, 248)       # tint de vidro vazio
BOTTLE_BORDER   = (100, 155, 210)
BOTTLE_FILL     = (55,  150, 230)       # agua normal
BOTTLE_FILL_G   = (30,  190, 110)       # agua meta atingida
WAVE_TOP        = (130, 200, 245)
WAVE_BOT        = (35,  120, 200)
REFLECT_COLOR   = (255, 255, 255, 100)
BUBBLE_C        = (200, 235, 255, 150)
FLASH_COLOR     = (210,  45,  45)

PROG_TRACK      = (200, 220, 240)
PROG_FILL       = (55,  150, 230)
PROG_GOAL       = (30,  190, 110)
BADGE_BG        = (55,  150, 230)
BADGE_GOAL_BG   = (30,  190, 110)
BADGE_TEXT      = (255, 255, 255)

TEXT_HEAD       = (20,  45,  85)
TEXT_BODY       = (65,  105, 150)
TEXT_DIM        = (145, 175, 205)

CARD_BG         = (255, 255, 255)
CARD_BORDER     = (210, 225, 240)
SHADOW_C        = (170, 195, 220, 50)

BTN_BLUE        = (40,  120, 220)
BTN_BLUE_H      = (25,   95, 185)
BTN_WHITE       = (255, 255, 255)
BTN_WHITE_H     = (235, 245, 255)
BTN_BORDER      = (185, 210, 238)

INPUT_BG        = (245, 250, 255)
INPUT_BORDER    = (190, 215, 240)
INPUT_ACTIVE    = (40,  120, 220)

GOLD            = (245, 170,  30)
STREAK_C        = (230, 100,  20)
DAY_DONE        = (55,  150, 230)
DAY_DONE_RING   = (30,  110, 190)
DAY_TODAY_BG    = (220, 245, 225)
DAY_TODAY_RING  = (30,  180, 100)
DAY_FAIL        = (210, 220, 232)
DAY_FAIL_RING   = (180, 200, 220)

# ── Layout ────────────────────────────────────────────────────────────────────
WIN_W     = 480
WIN_H     = 800

BCX       = WIN_W // 2 + 18     # centro X da garrafa (desloca para dar espaço à barra)
B_TOP     = 128
B_H       = 390
B_W       = 170
NECK_H    = 40
NECK_W    = 68
CAP_H     = 16

PROG_X    = 28
RULER_X   = BCX + B_W // 2 + 14

FONT_TITLE = FONT_BIG = FONT_MED = FONT_SMALL = FONT_TINY = None


def init_fonts():
    global FONT_TITLE, FONT_BIG, FONT_MED, FONT_SMALL, FONT_TINY
    FONT_TITLE = pygame.font.SysFont("segoeui", 34, bold=True)
    FONT_BIG   = pygame.font.SysFont("segoeui", 26, bold=True)
    FONT_MED   = pygame.font.SysFont("segoeui", 19)
    FONT_SMALL = pygame.font.SysFont("segoeui", 15)
    FONT_TINY  = pygame.font.SysFont("segoeui", 12)


# ── Utilitários de desenho ───────────────────────────────────────────────────
def _surf_rect(color, rect, radius):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(s, color, s.get_rect(), border_radius=radius)
    return s


def _shadow(surface, rect, radius=14, ox=3, oy=4):
    sr = pygame.Rect(rect.x + ox, rect.y + oy, rect.width, rect.height)
    surface.blit(_surf_rect(SHADOW_C, sr, radius), sr.topleft)


def _draw_drop(surface, cx, cy, size, color):
    """Desenha uma gota de água usando polígono."""
    pts = []
    for i in range(20):
        a = math.pi * 2 * i / 20
        r = size * (0.85 + 0.15 * math.cos(a * 2))
        x = cx + r * math.sin(a)
        y = cy + r * math.cos(a) - size * 0.25
        pts.append((x, y))
    # ponta da gota no topo
    pts.append((cx, cy - size * 1.2))
    pygame.draw.polygon(surface, color, pts)


def _draw_refresh(surface, cx, cy, size, color, width=2):
    """Desenha um arco de refresh (↺)."""
    rect = pygame.Rect(cx - size, cy - size, size * 2, size * 2)
    pygame.draw.arc(surface, color, rect, math.radians(30), math.radians(330), width)
    # setinha
    ax = cx + size * math.cos(math.radians(30))
    ay = cy - size * math.sin(math.radians(30))
    pygame.draw.polygon(surface, color, [
        (ax, ay), (ax - 5, ay - 5), (ax + 5, ay - 5)
    ])


def _draw_gear(surface, cx, cy, size, color):
    """Desenha uma engrenagem simples."""
    pygame.draw.circle(surface, color, (cx, cy), size - 2, 2)
    pygame.draw.circle(surface, color, (cx, cy), size // 2)
    for i in range(6):
        a = math.radians(i * 60)
        x1 = cx + (size - 3) * math.cos(a)
        y1 = cy + (size - 3) * math.sin(a)
        x2 = cx + (size + 3) * math.cos(a)
        y2 = cy + (size + 3) * math.sin(a)
        pygame.draw.line(surface, color, (int(x1), int(y1)), (int(x2), int(y2)), 3)


def _draw_check(surface, cx, cy, size, color, width=2):
    p1 = (cx - size * 0.45, cy)
    p2 = (cx - size * 0.05, cy + size * 0.45)
    p3 = (cx + size * 0.55, cy - size * 0.45)
    pygame.draw.lines(surface, color, False, [p1, p2, p3], width)


# ── Partículas ────────────────────────────────────────────────────────────────
class Bubble:
    def __init__(self, liq_top, liq_bot):
        hw = B_W // 2 - 12
        self.x = BCX + random.randint(-hw, hw)
        self.y = float(random.randint(liq_top + 6, liq_bot))
        self.r = random.randint(2, 6)
        self.speed = random.uniform(0.3, 1.0)
        self.alive = True

    def update(self, liq_top):
        self.y -= self.speed
        if self.y < liq_top:
            self.alive = False

    def draw(self, surface):
        s = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, BUBBLE_C, (self.r, self.r), self.r)
        surface.blit(s, (int(self.x) - self.r, int(self.y) - self.r))


class Spark:
    def __init__(self):
        self.x = float(random.randint(40, WIN_W - 40))
        self.y = float(random.randint(40, WIN_H - 40))
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-2.0, -0.4)
        self.life = random.randint(50, 100)
        self.max_life = self.life
        self.r = random.randint(3, 5)

    def update(self):
        self.x += self.vx
        self.vy += 0.06
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * self.life / self.max_life)
        s = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*GOLD, alpha), (self.r, self.r), self.r)
        surface.blit(s, (int(self.x) - self.r, int(self.y) - self.r))


# ── Button ────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, rect, label, primary=True):
        self.rect     = rect
        self.label    = label
        self.primary  = primary
        self.hovered  = False
        self.disabled = False

    def handle_event(self, event):
        if self.disabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

    def draw(self, surface):
        r = self.rect
        if self.disabled:
            bg, tc, bc = (200, 215, 230), (155, 175, 200), (185, 200, 218)
        elif self.primary:
            bg = BTN_BLUE_H if self.hovered else BTN_BLUE
            tc, bc = (255, 255, 255), bg
        else:
            bg = BTN_WHITE_H if self.hovered else BTN_WHITE
            tc, bc = BTN_BLUE, BTN_BORDER

        _shadow(surface, r, radius=14)
        pygame.draw.rect(surface, bg, r, border_radius=14)
        pygame.draw.rect(surface, bc, r, 2, border_radius=14)

        txt = FONT_MED.render(self.label, True, tc)
        tr  = txt.get_rect(center=r.center)

        if self.primary and not self.disabled:
            # ícone gota à esquerda do texto
            icon_x = tr.left - 22
            _draw_drop(surface, icon_x, r.centery + 1, 8, (200, 235, 255))
        elif not self.primary:
            # ícone refresh à esquerda
            _draw_refresh(surface, tr.left - 20, r.centery, 8, BTN_BLUE)

        surface.blit(txt, tr)


# ── TextInput ─────────────────────────────────────────────────────────────────
class TextInput:
    def __init__(self, rect, placeholder="ml"):
        self.rect        = rect
        self.placeholder = placeholder
        self.text        = ""
        self.active      = False
        self._cur_timer  = 0
        self._cur_vis    = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit() and len(self.text) < 5:
                self.text += event.unicode
        return False

    def get_value(self):
        try:
            return max(1, min(9999, int(self.text)))
        except ValueError:
            return 0

    def clear(self):
        self.text = ""

    def update(self):
        self._cur_timer += 1
        if self._cur_timer >= 30:
            self._cur_timer = 0
            self._cur_vis = not self._cur_vis

    def draw(self, surface):
        border = INPUT_ACTIVE if self.active else INPUT_BORDER
        _shadow(surface, self.rect, radius=8, oy=2)
        pygame.draw.rect(surface, INPUT_BG, self.rect, border_radius=8)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=8)
        display = self.text if self.text else self.placeholder
        color   = TEXT_HEAD if self.text else TEXT_DIM
        if self.active and self._cur_vis and self.text:
            display += "|"
        t = FONT_SMALL.render(display, True, color)
        surface.blit(t, t.get_rect(center=self.rect.center))


# ── Renderer principal ────────────────────────────────────────────────────────
class Renderer:
    def __init__(self):
        self._wave   = 0.0
        self._bubbles: list[Bubble] = []
        self._sparks:  list[Spark]  = []
        self._btimer  = 0

        bw2 = (WIN_W - 28) // 2 - 6
        self.btn_drink  = Button(pygame.Rect(14,         670, bw2, 50), "Bebi!",       primary=True)
        self.btn_reset  = Button(pygame.Rect(14 + bw2 + 12, 670, bw2, 50), "Resetar", primary=False)
        self.btn_config = Button(pygame.Rect(WIN_W - 130, 14, 116, 34), "Config",      primary=False)
        self.input_ml   = TextInput(pygame.Rect(WIN_W // 2 - 50, 735, 100, 34), "ml manual")

        self.all_buttons = [self.btn_drink, self.btn_reset, self.btn_config]
        self.text_inputs  = [self.input_ml]

    # ── geometria ────────────────────────────────────────────────────────────
    def _body(self):
        return pygame.Rect(BCX - B_W // 2,
                           B_TOP + NECK_H + CAP_H,
                           B_W,
                           B_H - NECK_H - CAP_H)

    def _neck(self):
        return pygame.Rect(BCX - NECK_W // 2,
                           B_TOP + CAP_H,
                           NECK_W, NECK_H + 4)

    def _cap(self):
        return pygame.Rect(BCX - NECK_W // 2 + 8,
                           B_TOP,
                           NECK_W - 16, CAP_H + 4)

    def _liq_top(self, pct):
        body = self._body()
        return body.bottom - int(body.height * pct)

    # ── garrafa ───────────────────────────────────────────────────────────────
    def _draw_bottle(self, surface, pct, goal, flash):
        body = self._body()
        neck = self._neck()
        cap  = self._cap()
        bc   = FLASH_COLOR if flash else BOTTLE_BORDER

        # sombra
        _shadow(surface, body.inflate(6, 6), radius=28, oy=6)

        # ── fundo de vidro (sempre visível) ──
        pygame.draw.rect(surface, BOTTLE_BG, body, border_radius=24)
        pygame.draw.rect(surface, BOTTLE_BG, neck, border_radius=10)

        # ── água ─────────────────────────────────────────────────────────────
        if pct > 0.005:
            liq_top  = self._liq_top(pct)
            fill_c   = BOTTLE_FILL_G if goal else BOTTLE_FILL
            fill     = pygame.Rect(body.x + 3, liq_top,
                                   body.width - 6, body.bottom - liq_top - 3)
            if fill.height > 0:
                pygame.draw.rect(surface, fill_c, fill, border_radius=18)
                self._draw_wave(surface, fill, goal)

        # ── reflexo ──────────────────────────────────────────────────────────
        ref = pygame.Surface((body.width, body.height), pygame.SRCALPHA)
        pts = [(14, 6), (36, 6), (20, body.height - 16), (0, body.height - 16)]
        pygame.draw.polygon(ref, REFLECT_COLOR, pts)
        surface.blit(ref, body.topleft)

        # ── bordas (por cima de tudo) ─────────────────────────────────────────
        pygame.draw.rect(surface, bc,  body, 2, border_radius=24)
        pygame.draw.rect(surface, bc,  neck, 2, border_radius=10)
        pygame.draw.rect(surface, bc,  cap,  border_radius=7)
        pygame.draw.rect(surface, bc,  cap,  2, border_radius=7)

        # linhas horizontais sutis na garrafa (textura leve)
        for i in range(1, 4):
            y = body.y + body.height * i // 4
            pygame.draw.line(surface, (*BOTTLE_BG, 80),
                             (body.x + 6, y), (body.right - 6, y), 1)

    def _draw_wave(self, surface, fill, goal):
        ws = pygame.Surface((fill.width, 20), pygame.SRCALPHA)
        amp  = 4 if not goal else 7
        freq = 0.048
        for x in range(fill.width):
            y1 = int(10 + amp * math.sin(x * freq + self._wave))
            y2 = int(10 + amp * math.sin(x * freq + self._wave + math.pi))
            pygame.draw.line(ws, (*WAVE_BOT, 140), (x, y1), (x, 20))
            pygame.draw.line(ws, (*WAVE_TOP, 100), (x, y2), (x, 20))
        surface.blit(ws, (fill.x, fill.y - 8))

    # ── barra de progresso ───────────────────────────────────────────────────
    def _draw_progress(self, surface, pct, goal):
        body   = self._body()
        bh     = body.height
        by     = body.y
        bar    = pygame.Rect(PROG_X, by, 8, bh)
        fill_h = int(bh * pct)

        pygame.draw.rect(surface, PROG_TRACK, bar, border_radius=4)
        if fill_h > 0:
            fr = pygame.Rect(PROG_X, by + bh - fill_h, 8, fill_h)
            pygame.draw.rect(surface, PROG_GOAL if goal else PROG_FILL, fr, border_radius=4)

        # badge — fixo no topo da barra preenchida, nunca sai do bar
        badge_y = by + bh - max(fill_h, 0)
        badge_y = max(by + 16, min(by + bh - 16, badge_y))
        badge_c = BADGE_GOAL_BG if goal else BADGE_BG
        pygame.draw.circle(surface, badge_c, (PROG_X + 4, badge_y), 16)
        lbl = FONT_TINY.render(f"{int(pct * 100)}%", True, BADGE_TEXT)
        surface.blit(lbl, lbl.get_rect(center=(PROG_X + 4, badge_y)))

    # ── régua ────────────────────────────────────────────────────────────────
    def _draw_ruler(self, surface, goal_ml):
        body = self._body()
        for ml in [0, goal_ml // 2, goal_ml]:
            pct  = ml / goal_ml if goal_ml else 0
            y    = body.bottom - int(body.height * pct)
            pygame.draw.line(surface, TEXT_DIM,
                             (RULER_X, y), (RULER_X + 5, y), 1)
            lbl = FONT_TINY.render(f"- {ml} ml", True, TEXT_DIM)
            surface.blit(lbl, (RULER_X + 8, y - 7))

    # ── HUD ──────────────────────────────────────────────────────────────────
    def _draw_hud(self, surface, state, timer_rem):
        # ml / meta
        title = FONT_TITLE.render(
            f"{state.consumed_ml} ml / {state.goal_ml} ml", True, TEXT_HEAD
        )
        surface.blit(title, title.get_rect(centerx=WIN_W // 2, y=70))

        sub = FONT_SMALL.render(
            f"{int(state.percent() * 100)}% da meta diaria", True, TEXT_BODY
        )
        surface.blit(sub, sub.get_rect(centerx=WIN_W // 2, y=108))

        # countdown
        if state.goal_reached:
            cd_txt = "Meta atingida!"
            cd_col = (30, 175, 90)
        else:
            m, s = divmod(timer_rem, 60)
            cd_txt = f"Proximo lembrete: {m:02d}:{s:02d}"
            cd_col = TEXT_BODY if timer_rem > 60 else FLASH_COLOR

        # ícone de relógio desenhado
        pygame.draw.circle(surface, cd_col, (20, 22), 9, 2)
        pygame.draw.line(surface, cd_col, (20, 22), (20, 16), 2)
        pygame.draw.line(surface, cd_col, (20, 22), (25, 22), 2)

        cd = FONT_SMALL.render(cd_txt, True, cd_col)
        surface.blit(cd, (34, 14))

        if state.goal_reached:
            msg = FONT_BIG.render("Parabens! Meta batida!", True, (30, 160, 80))
            surface.blit(msg, msg.get_rect(centerx=WIN_W // 2, y=630))

    # ── painel streak + 7 dias ───────────────────────────────────────────────
    def _draw_streak_panel(self, surface, state):
        panel = pygame.Rect(14, 548, WIN_W - 28, 110)
        _shadow(surface, panel, radius=14)
        pygame.draw.rect(surface, CARD_BG, panel, border_radius=14)
        pygame.draw.rect(surface, CARD_BORDER, panel, 1, border_radius=14)

        streak = state.streak()
        best   = state.best_streak

        # ícone de fogo desenhado (chamas simples)
        fx, fy = panel.x + 20, panel.y + 14
        for i, (ox, oy, r, c) in enumerate([
            (0,  0, 9, (230, 90, 30)),
            (-4, 3, 6, (245, 145, 30)),
            (4,  3, 6, (245, 145, 30)),
        ]):
            pygame.draw.ellipse(surface, c,
                                pygame.Rect(fx + ox - r // 2, fy + oy - r,
                                            r + 2, r * 2))

        # texto de streak
        s_txt = FONT_BIG.render(f"{streak} dias seguidos", True, STREAK_C)
        surface.blit(s_txt, (fx + 22, panel.y + 8))

        # recorde
        b_txt = FONT_TINY.render(f"Recorde: {best} dias", True, TEXT_DIM)
        surface.blit(b_txt, b_txt.get_rect(right=panel.right - 14, y=panel.y + 14))

        # 7 círculos
        days    = state.last_7_days()
        n       = len(days)
        pad     = 20
        spacing = (panel.width - pad * 2) // n
        cx0     = panel.x + pad + spacing // 2
        cy      = panel.y + 78

        for i, d in enumerate(days):
            cx  = cx0 + i * spacing
            st  = d["status"]
            lbl = d["label"]

            if st == "done":
                pygame.draw.circle(surface, DAY_DONE, (cx, cy), 16)
                pygame.draw.circle(surface, DAY_DONE_RING, (cx, cy), 16, 2)
                _draw_check(surface, cx, cy, 12, (255, 255, 255), 2)

            elif st == "today":
                ring_c = DAY_TODAY_RING if state.goal_reached else DAY_DONE
                pygame.draw.circle(surface, DAY_TODAY_BG, (cx, cy), 16)
                pygame.draw.circle(surface, ring_c, (cx, cy), 16, 2)
                pct_lbl = FONT_TINY.render(f"{int(state.percent() * 100)}%",
                                           True, ring_c)
                surface.blit(pct_lbl, pct_lbl.get_rect(center=(cx, cy)))

            else:
                pygame.draw.circle(surface, DAY_FAIL, (cx, cy), 16)
                pygame.draw.circle(surface, DAY_FAIL_RING, (cx, cy), 16, 1)
                # X
                d_off = 5
                pygame.draw.line(surface, DAY_FAIL_RING,
                                 (cx - d_off, cy - d_off),
                                 (cx + d_off, cy + d_off), 2)
                pygame.draw.line(surface, DAY_FAIL_RING,
                                 (cx + d_off, cy - d_off),
                                 (cx - d_off, cy + d_off), 2)

            day_lbl = FONT_TINY.render(lbl, True, TEXT_DIM)
            surface.blit(day_lbl, day_lbl.get_rect(centerx=cx, y=cy + 20))

    # ── partículas ────────────────────────────────────────────────────────────
    def _update_particles(self, pct, goal):
        self._wave += 0.045 if not goal else 0.09
        self._btimer += 1
        rate = 8 if not goal else 4
        if self._btimer >= rate and pct > 0.04:
            self._btimer = 0
            body = self._body()
            self._bubbles.append(Bubble(self._liq_top(pct), body.bottom))
        liq_top = self._liq_top(pct)
        for b in self._bubbles:
            b.update(liq_top)
        self._bubbles = [b for b in self._bubbles if b.alive]

        if goal and random.random() < 0.2:
            self._sparks.append(Spark())
        for sp in self._sparks:
            sp.update()
        self._sparks = [sp for sp in self._sparks if sp.life > 0]

    def _draw_particles(self, surface):
        for b in self._bubbles:
            b.draw(surface)
        for sp in self._sparks:
            sp.draw(surface)

    # ── API pública ───────────────────────────────────────────────────────────
    def handle_event(self, event, state, timer_manager) -> str | None:
        for inp in self.text_inputs:
            if inp.handle_event(event) and inp == self.input_ml:
                val = inp.get_value()
                if val > 0:
                    inp.clear()
                    return f"drink_manual:{val}"
        if self.btn_drink.handle_event(event):
            return "drink_quick"
        if self.btn_reset.handle_event(event):
            return "reset"
        if self.btn_config.handle_event(event):
            return "config"
        return None

    def draw(self, surface: pygame.Surface, state, timer_rem: int) -> None:
        pct   = state.percent()
        goal  = state.goal_reached
        flash = time.time() < state.flash_until

        surface.fill(BG_GOAL if goal else BG)

        self._update_particles(pct, goal)
        self._draw_progress(surface, pct, goal)
        self._draw_bottle(surface, pct, goal, flash)
        self._draw_particles(surface)
        self._draw_ruler(surface, state.goal_ml)
        self._draw_hud(surface, state, timer_rem)
        self._draw_streak_panel(surface, state)

        # config icon (engrenagem desenhada)
        _draw_gear(surface,
                   self.btn_config.rect.x + 16,
                   self.btn_config.rect.centery, 7,
                   BTN_BLUE)

        self.btn_drink.disabled = goal
        self.input_ml.update()
        for btn in self.all_buttons:
            btn.draw(surface)
        for inp in self.text_inputs:
            inp.draw(surface)

        # label do input manual
        ou = FONT_SMALL.render("ou digite:", True, TEXT_BODY)
        ml = FONT_SMALL.render("ml", True, TEXT_BODY)
        surface.blit(ou, (WIN_W // 2 - 158, 745))
        surface.blit(ml, (WIN_W // 2 + 58,  745))
