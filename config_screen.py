import pygame

BG_OVERLAY = (10, 15, 35, 210)
PANEL_BG   = (20, 30, 60)
BORDER     = (80, 120, 180)
ACTIVE     = (100, 160, 240)
TEXT       = (220, 235, 255)
TEXT_DIM   = (120, 150, 190)
ERROR      = (220, 60, 60)
BTN_OK     = (40, 130, 80)
BTN_CANCEL = (100, 40, 40)

WIN_W, WIN_H = 540, 700
PANEL_W, PANEL_H = 360, 310
PANEL_X = (WIN_W - PANEL_W) // 2
PANEL_Y = (WIN_H - PANEL_H) // 2


class _Field:
    def __init__(self, label: str, rect: pygame.Rect, value: int,
                 min_val: int, max_val: int):
        self.label = label
        self.rect = rect
        self.text = str(value)
        self.active = False
        self.min_val = min_val
        self.max_val = max_val
        self.error = False

    def handle_event(self, event) -> bool:
        """Returns True if Tab/Enter pressed (move focus)."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_TAB, pygame.K_RETURN):
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit() and len(self.text) < 6:
                self.text += event.unicode
        return False

    def get_value(self) -> int | None:
        try:
            v = int(self.text)
            if self.min_val <= v <= self.max_val:
                self.error = False
                return v
            self.error = True
            return None
        except ValueError:
            self.error = True
            return None

    def draw(self, surface: pygame.Surface, font_lbl, font_inp) -> None:
        lbl = font_lbl.render(self.label, True, TEXT_DIM)
        surface.blit(lbl, (self.rect.x, self.rect.y - 22))
        border = ERROR if self.error else (ACTIVE if self.active else BORDER)
        pygame.draw.rect(surface, PANEL_BG, self.rect, border_radius=6)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=6)
        txt = font_inp.render(self.text or "", True, TEXT)
        surface.blit(txt, txt.get_rect(midleft=(self.rect.x + 10, self.rect.centery)))
        if self.error:
            hint = font_lbl.render(f"{self.min_val}–{self.max_val}", True, ERROR)
            surface.blit(hint, (self.rect.right + 6, self.rect.centery - 8))


class ConfigScreen:
    def __init__(self):
        self._font_lbl  = None
        self._font_inp  = None
        self._font_title = None
        self._fields: list[_Field] = []
        self._btn_ok = pygame.Rect(0, 0, 120, 40)
        self._btn_cancel = pygame.Rect(0, 0, 120, 40)
        self._active_idx = 0

    def _init_fonts(self):
        self._font_lbl   = pygame.font.SysFont("segoeui", 15)
        self._font_inp   = pygame.font.SysFont("segoeui", 20)
        self._font_title = pygame.font.SysFont("segoeui", 24, bold=True)

    def open(self, state) -> None:
        self._init_fonts()
        ox = PANEL_X + 40
        self._fields = [
            _Field("Meta diária (ml):",
                   pygame.Rect(ox, PANEL_Y + 70, PANEL_W - 80, 40),
                   state.goal_ml, 100, 10000),
            _Field("Intervalo de lembrete (min):",
                   pygame.Rect(ox, PANEL_Y + 145, PANEL_W - 80, 40),
                   state.interval_min, 1, 480),
            _Field("Volume do copo rápido (ml):",
                   pygame.Rect(ox, PANEL_Y + 220, PANEL_W - 80, 40),
                   state.default_cup_ml, 50, 2000),
        ]
        self._fields[0].active = True
        self._active_idx = 0
        bx = PANEL_X + PANEL_W // 2
        by = PANEL_Y + PANEL_H - 50
        self._btn_ok     = pygame.Rect(bx - 130, by, 110, 36)
        self._btn_cancel = pygame.Rect(bx + 20, by, 110, 36)

    def handle_event(self, event, state) -> str | None:
        """
        Returns: 'saved', 'cancelled', or None.
        """
        for i, field in enumerate(self._fields):
            if field.handle_event(event):
                self._active_idx = (i + 1) % len(self._fields)
                for j, f in enumerate(self._fields):
                    f.active = (j == self._active_idx)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "cancelled"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._btn_ok.collidepoint(event.pos):
                return self._try_save(state)
            if self._btn_cancel.collidepoint(event.pos):
                return "cancelled"
        return None

    def _try_save(self, state) -> str | None:
        values = [f.get_value() for f in self._fields]
        if None in values:
            return None  # validation errors shown inline
        state.goal_ml        = values[0]
        state.interval_min   = values[1]
        state.default_cup_ml = values[2]
        state.save()
        return "saved"

    def draw(self, surface: pygame.Surface) -> None:
        # semi-transparent overlay
        overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        overlay.fill(BG_OVERLAY)
        surface.blit(overlay, (0, 0))

        # panel
        panel = pygame.Rect(PANEL_X, PANEL_Y, PANEL_W, PANEL_H)
        pygame.draw.rect(surface, PANEL_BG, panel, border_radius=14)
        pygame.draw.rect(surface, BORDER, panel, 2, border_radius=14)

        title = self._font_title.render("Configurações", True, TEXT)
        surface.blit(title, title.get_rect(centerx=WIN_W // 2, y=PANEL_Y + 16))

        for field in self._fields:
            field.draw(surface, self._font_lbl, self._font_inp)

        # buttons
        pygame.draw.rect(surface, BTN_OK, self._btn_ok, border_radius=8)
        pygame.draw.rect(surface, BTN_CANCEL, self._btn_cancel, border_radius=8)
        ok_lbl = self._font_inp.render("Salvar", True, (220, 255, 220))
        cancel_lbl = self._font_inp.render("Cancelar", True, (255, 200, 200))
        surface.blit(ok_lbl, ok_lbl.get_rect(center=self._btn_ok.center))
        surface.blit(cancel_lbl, cancel_lbl.get_rect(center=self._btn_cancel.center))
