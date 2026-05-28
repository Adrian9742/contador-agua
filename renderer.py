import math
import random
import time
from datetime import date, timedelta
import pygame

# ── Paleta clara ──────────────────────────────────────────────────────────────
BG              = (235, 245, 255)
BG_GOAL         = (220, 245, 235)
BOTTLE_GLASS    = (210, 232, 252, 60)   # fill vidro (SRCALPHA)
BOTTLE_BORDER   = (140, 190, 235)
BOTTLE_REFLECT  = (255, 255, 255, 90)   # reflexo diagonal
LIQUID          = (79,  179, 247)
LIQUID_GOAL     = (30,  144, 255)
WAVE_LIGHT      = (160, 220, 255, 160)
WAVE_SHADOW     = (50,  130, 200, 120)
BUBBLE_COLOR    = (200, 235, 255, 140)
FLASH_COLOR     = (220,  55,  55)
PROGRESS_BG     = (210, 225, 240)
PROGRESS_FILL   = (30,  144, 255)
PROGRESS_GOAL   = (30,  200, 100)
BADGE_BG        = (30,  144, 255)
BADGE_TEXT      = (255, 255, 255)
TEXT_DARK       = (25,  50,  90)
TEXT_MED        = (80,  120, 165)
TEXT_LIGHT      = (150, 180, 210)
BTN_PRIMARY     = (30,  120, 220)
BTN_PRIMARY_H   = (20,   90, 190)
BTN_SECONDARY   = (255, 255, 255)
BTN_SECONDARY_H = (235, 245, 255)
BTN_BORDER      = (180, 210, 240)
BTN_TEXT_PRI    = (255, 255, 255)
BTN_TEXT_SEC    = (30,  120, 220)
INPUT_BG        = (245, 250, 255)
INPUT_BORDER    = (180, 210, 240)
INPUT_ACTIVE    = (30,  120, 220)
GOLD            = (255, 180,   0)
STREAK_FIRE     = (255, 130,  30)
DAY_DONE        = (30,  144, 255)
DAY_DONE_BG     = (210, 235, 255)
DAY_FAILED      = (200, 215, 230)
DAY_TODAY_BG    = (210, 245, 225)
DAY_TODAY_BORDER= (30,  200, 100)
SHADOW          = (180, 200, 220, 60)

WIN_W, WIN_H    = 540, 800
BOTTLE_CX       = WIN_W // 2 + 20   # deslocado para direita (barra prog à esq)
BOTTLE_TOP      = 130
BOTTLE_H        = 390
BOTTLE_W        = 180
BOTTLE_NECK_H   = 45
BOTTLE_NECK_W   = 72
BOTTLE_CAP_H    = 18
PROG_X          = 52                 # barra de progresso lateral
RULER_X         = BOTTLE_CX + BOTTLE_W // 2 + 12  # régua à direita

FONT_TITLE  = None
FONT_BIG    = None
FONT_MED    = None
FONT_SMALL  = None
FONT_TINY   = None


def init_fonts():
    global FONT_TITLE, FONT_BIG, FONT_MED, FONT_SMALL, FONT_TINY
    FONT_TITLE  = pygame.font.SysFont("segoeui", 36, bold=True)
    FONT_BIG    = pygame.font.SysFont("segoeui", 28, bold=True)
    FONT_MED    = pygame.font.SysFont("segoeui", 20)
    FONT_SMALL  = pygame.font.SysFont("segoeui", 16)
    FONT_TINY   = pygame.font.SysFont("segoeui", 13)


# ── helpers de superfície ────────────────────────────────────────────────────
def _draw_rounded_rect_alpha(surface, color, rect, radius):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(s, color, s.get_rect(), border_radius=radius)
    surface.blit(s, rect.topleft)


def _draw_shadow(surface, rect, radius=16, offset=4):
    sr = pygame.Rect(rect.x + offset, rect.y + offset, rect.width, rect.height)
    _draw_rounded_rect_alpha(surface, (160, 185, 210, 55), sr, radius)


# ── Bubble ───────────────────────────────────────────────────────────────────
class Bubble:
    def __init__(self, liq_top, liq_bottom):
        hw = BOTTLE_W // 2 - 12
        self.x = BOTTLE_CX + random.randint(-hw, hw)
        self.y = float(random.randint(liq_top + 8, liq_bottom))
        self.r = random.randint(3, 7)
        self.speed = random.uniform(0.4, 1.1)
        self.alive = True

    def update(self, liq_top):
        self.y -= self.speed
        if self.y < liq_top:
            self.alive = False

    def draw(self, surface):
        s = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, BUBBLE_COLOR, (self.r, self.r), self.r)
        surface.blit(s, (int(self.x) - self.r, int(self.y) - self.r))


# ── GoldParticle ─────────────────────────────────────────────────────────────
class GoldParticle:
    def __init__(self):
        self.x = float(random.randint(60, WIN_W - 60))
        self.y = float(random.randint(60, WIN_H - 60))
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-2.0, -0.5)
        self.life = random.randint(60, 120)
        self.max_life = self.life
        self.r = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.vy += 0.05
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        alpha = int(255 * self.life / self.max_life)
        s = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*GOLD, alpha), (self.r, self.r), self.r)
        surface.blit(s, (int(self.x) - self.r, int(self.y) - self.r))


# ── Button ───────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, rect, label, primary=True, icon=""):
        self.rect = rect
        self.label = label
        self.icon = icon
        self.primary = primary
        self.hovered = False
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
        if self.disabled:
            bg = (200, 215, 230)
            tc = (160, 175, 195)
            border = (185, 200, 220)
        elif self.primary:
            bg = BTN_PRIMARY_H if self.hovered else BTN_PRIMARY
            tc = BTN_TEXT_PRI
            border = bg
        else:
            bg = BTN_SECONDARY_H if self.hovered else BTN_SECONDARY
            tc = BTN_TEXT_SEC
            border = BTN_BORDER

        if not self.disabled:
            _draw_shadow(surface, self.rect, radius=14, offset=3)
        pygame.draw.rect(surface, bg, self.rect, border_radius=14)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=14)

        full_label = f"{self.icon}  {self.label}" if self.icon else self.label
        txt = FONT_MED.render(full_label, True, tc)
        surface.blit(txt, txt.get_rect(center=self.rect.center))


# ── TextInput ────────────────────────────────────────────────────────────────
class TextInput:
    def __init__(self, rect, placeholder="ml"):
        self.rect = rect
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self._cursor_timer = 0

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
        self._cursor_timer += 1
        if self._cursor_timer >= 30:
            self._cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, surface):
        border = INPUT_ACTIVE if self.active else INPUT_BORDER
        _draw_shadow(surface, self.rect, radius=10, offset=2)
        pygame.draw.rect(surface, INPUT_BG, self.rect, border_radius=10)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=10)
        display = self.text if self.text else self.placeholder
        color = TEXT_DARK if self.text else TEXT_LIGHT
        if self.active and self.cursor_visible and self.text:
            display = self.text + "|"
        txt = FONT_SMALL.render(display, True, color)
        surface.blit(txt, txt.get_rect(center=self.rect.center))


# ── Main Renderer ─────────────────────────────────────────────────────────────
class Renderer:
    def __init__(self):
        self._wave_offset = 0.0
        self._bubbles: list[Bubble] = []
        self._gold_particles: list[GoldParticle] = []
        self._bubble_timer = 0

        bw = WIN_W // 2 - 20
        self.btn_drink  = Button(pygame.Rect(30,        672, bw, 52), "Bebi!", primary=True,  icon="💧")
        self.btn_reset  = Button(pygame.Rect(30 + bw + 12, 672, bw, 52), "Resetar", primary=False, icon="↺")
        self.btn_config = Button(pygame.Rect(WIN_W - 140, 14, 122, 36), "Configurações", primary=False, icon="⚙")
        self.input_ml   = TextInput(pygame.Rect(WIN_W // 2 - 55, 738, 110, 36), "ml manual")

        self.all_buttons = [self.btn_drink, self.btn_reset, self.btn_config]
        self.text_inputs  = [self.input_ml]

    # ── geometry ─────────────────────────────────────────────────────────────
    def _body_rect(self):
        return pygame.Rect(
            BOTTLE_CX - BOTTLE_W // 2,
            BOTTLE_TOP + BOTTLE_NECK_H + BOTTLE_CAP_H,
            BOTTLE_W,
            BOTTLE_H - BOTTLE_NECK_H - BOTTLE_CAP_H,
        )

    def _liquid_top(self, pct):
        body = self._body_rect()
        fill_h = int(body.height * pct)
        return body.bottom - fill_h

    # ── bottle ────────────────────────────────────────────────────────────────
    def _draw_bottle(self, surface, pct, goal, flash):
        body = self._body_rect()
        neck = pygame.Rect(BOTTLE_CX - BOTTLE_NECK_W // 2,
                           BOTTLE_TOP + BOTTLE_CAP_H,
                           BOTTLE_NECK_W, BOTTLE_NECK_H + 4)
        cap  = pygame.Rect(BOTTLE_CX - BOTTLE_NECK_W // 2 + 8,
                           BOTTLE_TOP,
                           BOTTLE_NECK_W - 16, BOTTLE_CAP_H + 4)

        border_color = FLASH_COLOR if flash else BOTTLE_BORDER

        # sombra
        _draw_shadow(surface, body.inflate(4, 4), radius=28, offset=5)

        # fill de vidro (corpo)
        _draw_rounded_rect_alpha(surface, BOTTLE_GLASS, body, 24)
        pygame.draw.rect(surface, border_color, body, 2, border_radius=24)

        # gargalo
        _draw_rounded_rect_alpha(surface, BOTTLE_GLASS, neck, 10)
        pygame.draw.rect(surface, border_color, neck, 2, border_radius=10)

        # tampa
        pygame.draw.rect(surface, border_color, cap, border_radius=6)
        pygame.draw.rect(surface, border_color, cap, 2, border_radius=6)

        # líquido
        if pct > 0:
            liq_top = self._liquid_top(pct)
            fill = pygame.Rect(body.x + 3, liq_top, body.width - 6,
                               body.bottom - liq_top - 3)
            if fill.height > 0:
                liq_color = LIQUID_GOAL if goal else LIQUID
                pygame.draw.rect(surface, liq_color, fill, border_radius=20)
                self._draw_wave(surface, fill, goal)

        # reflexo diagonal (efeito vidro)
        ref_surf = pygame.Surface((body.width, body.height), pygame.SRCALPHA)
        pts = [(16, 8), (40, 8), (24, body.height - 20), (0, body.height - 20)]
        pygame.draw.polygon(ref_surf, BOTTLE_REFLECT, pts)
        surface.blit(ref_surf, body.topleft)

        # redesenha a borda por cima do reflexo
        pygame.draw.rect(surface, border_color, body, 2, border_radius=24)
        pygame.draw.rect(surface, border_color, neck, 2, border_radius=10)

    def _draw_wave(self, surface, fill_rect, goal):
        wave_surf = pygame.Surface((fill_rect.width, 22), pygame.SRCALPHA)
        amp = 5 if not goal else 8
        freq = 0.045
        for x in range(fill_rect.width):
            y1 = int(11 + amp * math.sin(x * freq + self._wave_offset))
            y2 = int(11 + amp * math.sin(x * freq + self._wave_offset + math.pi))
            pygame.draw.line(wave_surf, WAVE_SHADOW, (x, y1), (x, 22))
            pygame.draw.line(wave_surf, WAVE_LIGHT,  (x, y2), (x, 22))
        surface.blit(wave_surf, (fill_rect.x, fill_rect.y - 10))

    # ── barra de progresso lateral ────────────────────────────────────────────
    def _draw_progress_bar(self, surface, pct, goal):
        bar_h = BOTTLE_H - BOTTLE_NECK_H
        bar_top = BOTTLE_TOP + BOTTLE_NECK_H + BOTTLE_CAP_H
        bar_rect = pygame.Rect(PROG_X, bar_top, 10, bar_h)

        pygame.draw.rect(surface, PROGRESS_BG, bar_rect, border_radius=5)
        fill_h = int(bar_h * pct)
        if fill_h > 0:
            fill_color = PROGRESS_GOAL if goal else PROGRESS_FILL
            fill_rect = pygame.Rect(PROG_X, bar_top + bar_h - fill_h, 10, fill_h)
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=5)

        # badge com %
        badge_r = 20
        badge_y = bar_top + bar_h - fill_h
        badge_y = max(bar_top + badge_r, min(bar_top + bar_h - badge_r, badge_y))
        pygame.draw.circle(surface, BADGE_BG if not goal else PROGRESS_GOAL,
                           (PROG_X + 5, badge_y), badge_r)
        pct_lbl = FONT_TINY.render(f"{int(pct * 100)}%", True, BADGE_TEXT)
        surface.blit(pct_lbl, pct_lbl.get_rect(center=(PROG_X + 5, badge_y)))

    # ── régua lateral ─────────────────────────────────────────────────────────
    def _draw_ruler(self, surface, goal_ml):
        body = self._body_rect()
        marks = [
            (0,          "0"),
            (goal_ml // 2, f"{goal_ml // 2}"),
            (goal_ml,    f"{goal_ml}"),
        ]
        for ml, label in marks:
            pct = ml / goal_ml if goal_ml > 0 else 0
            y = body.bottom - int(body.height * pct)
            pygame.draw.line(surface, TEXT_LIGHT, (RULER_X, y), (RULER_X + 6, y), 1)
            lbl = FONT_TINY.render(f"{label} ml", True, TEXT_LIGHT)
            surface.blit(lbl, (RULER_X + 10, y - 7))

    # ── HUD ───────────────────────────────────────────────────────────────────
    def _draw_hud(self, surface, state, timer_remaining):
        # ml / meta
        ml_txt = FONT_TITLE.render(
            f"{state.consumed_ml} ml / {state.goal_ml} ml", True, TEXT_DARK
        )
        surface.blit(ml_txt, ml_txt.get_rect(centerx=WIN_W // 2, y=72))

        sub_txt = FONT_SMALL.render(
            f"{int(state.percent() * 100)}% da meta diária", True, TEXT_MED
        )
        surface.blit(sub_txt, sub_txt.get_rect(centerx=WIN_W // 2, y=112))

        # countdown
        if state.goal_reached:
            cd_label = "Meta atingida! 🎉"
            cd_color = (30, 180, 80)
        else:
            mins, secs = divmod(timer_remaining, 60)
            cd_label = f"⏱  Próximo lembrete: {mins:02d}:{secs:02d}"
            cd_color = TEXT_MED if timer_remaining > 60 else FLASH_COLOR
        cd_txt = FONT_SMALL.render(cd_label, True, cd_color)
        surface.blit(cd_txt, (16, 22))

        if state.goal_reached:
            msg = FONT_BIG.render("Parabéns! Meta batida! 🎉", True, (30, 160, 80))
            surface.blit(msg, msg.get_rect(centerx=WIN_W // 2, y=640))

    # ── streak + 7 círculos ───────────────────────────────────────────────────
    def _draw_streak_panel(self, surface, state):
        panel = pygame.Rect(20, 548, WIN_W - 40, 110)
        _draw_shadow(surface, panel, radius=14, offset=3)
        pygame.draw.rect(surface, (255, 255, 255), panel, border_radius=14)
        pygame.draw.rect(surface, BTN_BORDER, panel, 1, border_radius=14)

        streak = state.streak()
        best   = state.best_streak

        # streak em destaque
        fire_txt = FONT_BIG.render(f"🔥 {streak} dias seguidos", True, STREAK_FIRE)
        surface.blit(fire_txt, fire_txt.get_rect(x=panel.x + 16, y=panel.y + 10))

        best_txt = FONT_TINY.render(f"Recorde: {best} dias", True, TEXT_LIGHT)
        surface.blit(best_txt, best_txt.get_rect(right=panel.right - 14, y=panel.y + 16))

        # 7 círculos
        days = state.last_7_days()
        n = len(days)
        spacing = (panel.width - 28) // n
        cx_start = panel.x + 14 + spacing // 2
        cy = panel.y + 76

        for i, d in enumerate(days):
            cx = cx_start + i * spacing
            status = d["status"]

            if status == "done":
                pygame.draw.circle(surface, DAY_DONE_BG, (cx, cy), 18)
                pygame.draw.circle(surface, DAY_DONE, (cx, cy), 18, 2)
                dot = FONT_SMALL.render("✓", True, DAY_DONE)
            elif status == "today":
                color = (30, 200, 100) if state.goal_reached else (30, 144, 255)
                pygame.draw.circle(surface, DAY_TODAY_BG, (cx, cy), 18)
                pygame.draw.circle(surface, color, (cx, cy), 18, 2)
                pct_label = f"{int(state.percent() * 100)}%"
                dot = FONT_TINY.render(pct_label, True, color)
            else:
                pygame.draw.circle(surface, DAY_FAILED, (cx, cy), 18)
                dot = FONT_SMALL.render("·", True, (180, 200, 220))

            surface.blit(dot, dot.get_rect(center=(cx, cy)))

            # label do dia
            lbl = FONT_TINY.render(d["label"], True, TEXT_MED)
            surface.blit(lbl, lbl.get_rect(centerx=cx, y=cy + 22))

    # ── partículas ────────────────────────────────────────────────────────────
    def _update_particles(self, pct, goal):
        self._wave_offset += 0.045 if not goal else 0.09
        self._bubble_timer += 1
        rate = 7 if not goal else 3
        if self._bubble_timer >= rate and pct > 0.05:
            self._bubble_timer = 0
            liq_top = self._liquid_top(pct)
            self._bubbles.append(Bubble(liq_top, self._body_rect().bottom))
        for b in self._bubbles:
            b.update(self._liquid_top(pct))
        self._bubbles = [b for b in self._bubbles if b.alive]
        if goal and random.random() < 0.25:
            self._gold_particles.append(GoldParticle())
        for p in self._gold_particles:
            p.update()
        self._gold_particles = [p for p in self._gold_particles if p.life > 0]

    def _draw_particles(self, surface):
        for b in self._bubbles:
            b.draw(surface)
        for p in self._gold_particles:
            p.draw(surface)

    # ── input manual label ────────────────────────────────────────────────────
    def _draw_input_row(self, surface):
        lbl = FONT_SMALL.render("ou digite:", True, TEXT_MED)
        surface.blit(lbl, (WIN_W // 2 - 170, 747))
        ml_lbl = FONT_SMALL.render("ml", True, TEXT_MED)
        surface.blit(ml_lbl, (WIN_W // 2 + 62, 747))

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

    def draw(self, surface: pygame.Surface, state, timer_remaining: int) -> None:
        flash = time.time() < state.flash_until
        goal  = state.goal_reached
        pct   = state.percent()

        surface.fill(BG_GOAL if goal else BG)

        self._update_particles(pct, goal)
        self._draw_progress_bar(surface, pct, goal)
        self._draw_bottle(surface, pct, goal, flash)
        self._draw_particles(surface)
        self._draw_ruler(surface, state.goal_ml)
        self._draw_hud(surface, state, timer_remaining)
        self._draw_streak_panel(surface, state)

        self.btn_drink.disabled = goal
        self.input_ml.update()
        for btn in self.all_buttons:
            btn.draw(surface)
        for inp in self.text_inputs:
            inp.draw(surface)
        self._draw_input_row(surface)
