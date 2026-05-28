import math
import random
import time
import pygame

# ── Palette ──────────────────────────────────────────────────────────────────
BG_NORMAL       = (26,  26,  46)
BG_GOAL         = (13,  33,  55)
BOTTLE_BORDER   = (180, 220, 255)
LIQUID_NORMAL   = (79,  195, 247)
LIQUID_GOAL     = (0,   229, 255)
WAVE_DARK       = (30,  120, 180)
BUBBLE_COLOR    = (200, 240, 255, 120)
FLASH_COLOR     = (220,  50,  50)
TEXT_PRIMARY    = (230, 240, 255)
TEXT_DIM        = (120, 150, 190)
BTN_NORMAL      = (40,  80, 140)
BTN_HOVER       = (60, 110, 180)
BTN_DISABLED    = (50,  55,  70)
BTN_TEXT        = (220, 235, 255)
GOLD            = (255, 215,   0)
INPUT_BG        = (20,  30,  60)
INPUT_BORDER    = (80, 120, 180)
INPUT_ACTIVE    = (100, 160, 240)

WIN_W, WIN_H    = 540, 700
BOTTLE_X        = WIN_W // 2
BOTTLE_TOP      = 120
BOTTLE_H        = 420
BOTTLE_W        = 200
BOTTLE_NECK_H   = 50
BOTTLE_NECK_W   = 80

FONT_BIG   = None
FONT_MED   = None
FONT_SMALL = None


def init_fonts():
    global FONT_BIG, FONT_MED, FONT_SMALL
    FONT_BIG   = pygame.font.SysFont("segoeui", 32, bold=True)
    FONT_MED   = pygame.font.SysFont("segoeui", 22)
    FONT_SMALL = pygame.font.SysFont("segoeui", 17)


# ── Bubble particle ──────────────────────────────────────────────────────────
class Bubble:
    def __init__(self, liquid_top: int, liquid_bottom: int):
        self.x = BOTTLE_X + random.randint(-BOTTLE_W // 2 + 10, BOTTLE_W // 2 - 10)
        self.y = float(random.randint(liquid_top + 10, liquid_bottom))
        self.r = random.randint(3, 8)
        self.speed = random.uniform(0.4, 1.2)
        self.alive = True

    def update(self, liquid_top: int) -> None:
        self.y -= self.speed
        if self.y < liquid_top:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        s = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, BUBBLE_COLOR, (self.r, self.r), self.r)
        surface.blit(s, (int(self.x) - self.r, int(self.y) - self.r))


# ── Gold particle (goal celebration) ─────────────────────────────────────────
class GoldParticle:
    def __init__(self):
        self.x = float(random.randint(50, WIN_W - 50))
        self.y = float(random.randint(50, WIN_H - 50))
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-2.0, -0.5)
        self.life = random.randint(60, 120)
        self.max_life = self.life
        self.r = random.randint(3, 6)

    def update(self) -> None:
        self.x += self.vx
        self.vy += 0.05  # gravity
        self.y += self.vy
        self.life -= 1

    def draw(self, surface: pygame.Surface) -> None:
        alpha = int(255 * self.life / self.max_life)
        s = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
        color = (*GOLD, alpha)
        pygame.draw.circle(s, color, (self.r, self.r), self.r)
        surface.blit(s, (int(self.x) - self.r, int(self.y) - self.r))


# ── Button ───────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, rect: pygame.Rect, label: str):
        self.rect = rect
        self.label = label
        self.hovered = False
        self.disabled = False

    def handle_event(self, event) -> bool:
        if self.disabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

    def draw(self, surface: pygame.Surface) -> None:
        color = BTN_DISABLED if self.disabled else (BTN_HOVER if self.hovered else BTN_NORMAL)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, BOTTLE_BORDER, self.rect, 1, border_radius=8)
        text = FONT_MED.render(self.label, True, BTN_TEXT)
        surface.blit(text, text.get_rect(center=self.rect.center))


# ── TextInput ─────────────────────────────────────────────────────────────────
class TextInput:
    def __init__(self, rect: pygame.Rect, placeholder: str = "ml"):
        self.rect = rect
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self._cursor_timer = 0

    def handle_event(self, event) -> bool:
        """Returns True if Enter was pressed with a valid value."""
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

    def get_value(self) -> int:
        try:
            return max(1, min(9999, int(self.text)))
        except ValueError:
            return 0

    def clear(self) -> None:
        self.text = ""

    def update(self) -> None:
        self._cursor_timer += 1
        if self._cursor_timer >= 30:
            self._cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, surface: pygame.Surface) -> None:
        border = INPUT_ACTIVE if self.active else INPUT_BORDER
        pygame.draw.rect(surface, INPUT_BG, self.rect, border_radius=6)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=6)
        display = self.text if self.text else self.placeholder
        color = TEXT_PRIMARY if self.text else TEXT_DIM
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
        self._goal_celebrated = False

        self.btn_drink  = Button(pygame.Rect(WIN_W // 2 - 130, 590, 120, 44), "Bebi!")
        self.btn_reset  = Button(pygame.Rect(WIN_W // 2 + 10,  590, 120, 44), "Resetar")
        self.btn_config = Button(pygame.Rect(WIN_W - 110, 16, 95, 34), "⚙ Config")
        self.input_ml   = TextInput(pygame.Rect(WIN_W // 2 - 60, 645, 120, 36), "ml manual")

        # expose for main.py
        self.all_buttons = [self.btn_drink, self.btn_reset, self.btn_config]
        self.text_inputs  = [self.input_ml]

    # ── geometry helpers ──────────────────────────────────────────────────────
    def _bottle_rect(self) -> pygame.Rect:
        return pygame.Rect(
            BOTTLE_X - BOTTLE_W // 2,
            BOTTLE_TOP + BOTTLE_NECK_H,
            BOTTLE_W,
            BOTTLE_H - BOTTLE_NECK_H,
        )

    def _liquid_top(self, pct: float) -> int:
        body_bottom = BOTTLE_TOP + BOTTLE_H
        body_height = BOTTLE_H - BOTTLE_NECK_H
        fill_h = int(body_height * pct)
        return body_bottom - fill_h

    # ── draw helpers ──────────────────────────────────────────────────────────
    def _draw_bottle_outline(self, surface: pygame.Surface, flash: bool) -> None:
        color = FLASH_COLOR if flash else BOTTLE_BORDER
        body = self._bottle_rect()
        pygame.draw.rect(surface, color, body, 3, border_radius=12)
        neck_rect = pygame.Rect(
            BOTTLE_X - BOTTLE_NECK_W // 2,
            BOTTLE_TOP,
            BOTTLE_NECK_W,
            BOTTLE_NECK_H + 4,
        )
        pygame.draw.rect(surface, color, neck_rect, 3, border_radius=6)

    def _draw_liquid(self, surface: pygame.Surface, pct: float, goal: bool) -> None:
        if pct <= 0:
            return
        body = self._bottle_rect()
        liq_color = LIQUID_GOAL if goal else LIQUID_NORMAL
        liquid_top = self._liquid_top(pct)
        fill_rect = pygame.Rect(body.x + 3, liquid_top, body.width - 6,
                                body.bottom - liquid_top - 3)
        if fill_rect.height <= 0:
            return
        pygame.draw.rect(surface, liq_color, fill_rect, border_radius=8)

        # wave overlay
        wave_surf = pygame.Surface((fill_rect.width, 20), pygame.SRCALPHA)
        amplitude = 4 if not goal else 7
        freq = 0.04
        for x in range(fill_rect.width):
            y1 = int(10 + amplitude * math.sin(x * freq + self._wave_offset))
            y2 = int(10 + amplitude * math.sin(x * freq + self._wave_offset + math.pi))
            pygame.draw.line(wave_surf, (*WAVE_DARK, 180), (x, y1), (x, 20))
            pygame.draw.line(wave_surf, (*liq_color, 80), (x, y2), (x, 20))
        surface.blit(wave_surf, (fill_rect.x, liquid_top - 8))

    def _update_particles(self, pct: float, goal: bool) -> None:
        self._wave_offset += 0.04 if not goal else 0.08
        # bubbles
        self._bubble_timer += 1
        spawn_rate = 6 if not goal else 3
        if self._bubble_timer >= spawn_rate and pct > 0.05:
            self._bubble_timer = 0
            liq_top = self._liquid_top(pct)
            body_bottom = BOTTLE_TOP + BOTTLE_H
            self._bubbles.append(Bubble(liq_top, body_bottom))
        for b in self._bubbles:
            b.update(self._liquid_top(pct))
        self._bubbles = [b for b in self._bubbles if b.alive]
        # gold particles
        if goal:
            if random.random() < 0.3:
                self._gold_particles.append(GoldParticle())
        for p in self._gold_particles:
            p.update()
        self._gold_particles = [p for p in self._gold_particles if p.life > 0]

    def _draw_particles(self, surface: pygame.Surface) -> None:
        for b in self._bubbles:
            b.draw(surface)
        for p in self._gold_particles:
            p.draw(surface)

    def _draw_hud(self, surface: pygame.Surface, state, timer_remaining: int) -> None:
        # ml / goal text
        ml_text = FONT_BIG.render(
            f"{state.consumed_ml} ml / {state.goal_ml} ml", True, TEXT_PRIMARY
        )
        surface.blit(ml_text, ml_text.get_rect(centerx=WIN_W // 2, y=68))

        # percent
        pct_text = FONT_SMALL.render(
            f"{int(state.percent() * 100)}%", True, TEXT_DIM
        )
        surface.blit(pct_text, pct_text.get_rect(centerx=WIN_W // 2, y=100))

        # countdown
        if state.goal_reached:
            cd_label = "Meta atingida! 🎉"
            cd_color = LIQUID_GOAL
        else:
            mins, secs = divmod(timer_remaining, 60)
            cd_label = f"Próximo lembrete: {mins:02d}:{secs:02d}"
            cd_color = TEXT_DIM if timer_remaining > 60 else FLASH_COLOR
        cd_text = FONT_SMALL.render(cd_label, True, cd_color)
        surface.blit(cd_text, (12, 20))

        # goal reached message
        if state.goal_reached:
            msg = FONT_BIG.render("Parabéns! Meta batida!", True, GOLD)
            surface.blit(msg, msg.get_rect(centerx=WIN_W // 2, y=560))

    # ── public API ────────────────────────────────────────────────────────────
    def handle_event(self, event, state, timer_manager) -> str | None:
        """
        Returns an action string or None:
          'drink_quick', 'drink_manual:<ml>', 'reset', 'config'
        """
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

        # background
        surface.fill(BG_GOAL if goal else BG_NORMAL)

        # update + draw particles
        self._update_particles(state.percent(), goal)
        self._draw_liquid(surface, state.percent(), goal)
        self._draw_particles(surface)
        self._draw_bottle_outline(surface, flash)
        self._draw_hud(surface, state, timer_remaining)

        # buttons
        self.btn_drink.disabled  = goal
        self.input_ml.update()
        for btn in self.all_buttons:
            btn.draw(surface)
        for inp in self.text_inputs:
            inp.draw(surface)

        # manual ml label
        lbl = FONT_SMALL.render("ou digite:", True, TEXT_DIM)
        surface.blit(lbl, (WIN_W // 2 - 160, 653))
