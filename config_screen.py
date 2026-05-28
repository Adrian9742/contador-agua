import pygame

# ── Paleta clara (espelha renderer) ──────────────────────────────────────────
BG_OVERLAY  = (30,  60, 100, 160)
PANEL_BG    = (250, 253, 255)
PANEL_BORDER= (200, 220, 240)
FIELD_BG    = (242, 248, 255)
FIELD_BORDER= (185, 210, 238)
FIELD_ACTIVE= (30,  120, 220)
FIELD_ERROR = (210,  55,  55)
TEXT_DARK   = (25,   50,  90)
TEXT_MED    = (90,  125, 165)
TEXT_LIGHT  = (155, 180, 210)
BTN_SAVE    = (30,  120, 220)
BTN_CANCEL  = (245, 248, 252)
BTN_CANCEL_B= (185, 210, 238)
ICON_BG     = (225, 238, 255)
ICON_COLOR  = (30,  120, 220)

WIN_W, WIN_H   = 540, 800
PANEL_W        = 380
PANEL_H        = 340
PANEL_X        = (WIN_W - PANEL_W) // 2
PANEL_Y        = (WIN_H - PANEL_H) // 2

FIELD_CONFIGS = [
    {"icon": "🎯", "label": "Meta diária (ml)",
     "hint": "Quantidade de água que deseja beber por dia.",
     "attr": "goal_ml",       "min": 100,  "max": 10000},
    {"icon": "⏱",  "label": "Intervalo de lembrete (min)",
     "hint": "Tempo entre os lembretes para beber água.",
     "attr": "interval_min",  "min": 1,    "max": 480},
    {"icon": "💧", "label": "Volume do copo rápido (ml)",
     "hint": 'Quantidade adicionada ao clicar em "Bebi!".',
     "attr": "default_cup_ml","min": 50,   "max": 2000},
]


class _Field:
    def __init__(self, cfg: dict, rect: pygame.Rect, value: int):
        self.cfg   = cfg
        self.rect  = rect
        self.text  = str(value)
        self.active = False
        self.error  = False

    def handle_event(self, event) -> bool:
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
            lo, hi = self.cfg["min"], self.cfg["max"]
            if lo <= v <= hi:
                self.error = False
                return v
            self.error = True
            return None
        except ValueError:
            self.error = True
            return None

    def draw(self, surface, font_lbl, font_hint, font_inp):
        cfg  = self.cfg
        rect = self.rect

        # ícone
        icon_rect = pygame.Rect(rect.x - 42, rect.y + (rect.height - 32) // 2, 32, 32)
        pygame.draw.circle(surface, ICON_BG,
                           icon_rect.center, 16)
        icon_txt = font_lbl.render(cfg["icon"], True, ICON_COLOR)
        surface.blit(icon_txt, icon_txt.get_rect(center=icon_rect.center))

        # label
        lbl = font_lbl.render(cfg["label"], True, TEXT_DARK)
        surface.blit(lbl, (rect.x, rect.y - 20))

        # input
        border = FIELD_ERROR if self.error else (FIELD_ACTIVE if self.active else FIELD_BORDER)
        pygame.draw.rect(surface, FIELD_BG, rect, border_radius=10)
        pygame.draw.rect(surface, border, rect, 2, border_radius=10)
        inp_txt = font_inp.render(self.text or "", True, TEXT_DARK)
        surface.blit(inp_txt, inp_txt.get_rect(midleft=(rect.x + 12, rect.centery)))

        if self.error:
            err = font_hint.render(
                f"Entre {cfg['min']} e {cfg['max']}", True, FIELD_ERROR
            )
            surface.blit(err, (rect.right + 8, rect.centery - 7))

        # hint
        hint = font_hint.render(cfg["hint"], True, TEXT_LIGHT)
        surface.blit(hint, (rect.x, rect.bottom + 3))


class ConfigScreen:
    def __init__(self):
        self._font_title = None
        self._font_lbl   = None
        self._font_hint  = None
        self._font_inp   = None
        self._fields: list[_Field] = []
        self._btn_save   = pygame.Rect(0, 0, 0, 0)
        self._btn_cancel = pygame.Rect(0, 0, 0, 0)
        self._active_idx = 0

    def _init_fonts(self):
        self._font_title = pygame.font.SysFont("segoeui", 22, bold=True)
        self._font_lbl   = pygame.font.SysFont("segoeui", 15, bold=True)
        self._font_hint  = pygame.font.SysFont("segoeui", 13)
        self._font_inp   = pygame.font.SysFont("segoeui", 20)

    def open(self, state) -> None:
        self._init_fonts()
        ox = PANEL_X + 58
        fw = PANEL_W - 80

        row_h = 88
        y0 = PANEL_Y + 58
        self._fields = [
            _Field(FIELD_CONFIGS[i],
                   pygame.Rect(ox, y0 + i * row_h + 20, fw, 38),
                   getattr(state, FIELD_CONFIGS[i]["attr"]))
            for i in range(3)
        ]
        self._fields[0].active = True
        self._active_idx = 0

        by = PANEL_Y + PANEL_H - 52
        bx = PANEL_X + 20
        bw = (PANEL_W - 48) // 2
        self._btn_save   = pygame.Rect(bx,          by, bw, 38)
        self._btn_cancel = pygame.Rect(bx + bw + 8, by, bw, 38)

    def handle_event(self, event, state) -> str | None:
        for i, field in enumerate(self._fields):
            if field.handle_event(event):
                self._active_idx = (i + 1) % len(self._fields)
                for j, f in enumerate(self._fields):
                    f.active = (j == self._active_idx)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "cancelled"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._btn_save.collidepoint(event.pos):
                return self._try_save(state)
            if self._btn_cancel.collidepoint(event.pos):
                return "cancelled"
        return None

    def _try_save(self, state) -> str | None:
        values = [f.get_value() for f in self._fields]
        if None in values:
            return None
        for i, cfg in enumerate(FIELD_CONFIGS):
            setattr(state, cfg["attr"], values[i])
        state.save()
        return "saved"

    def draw(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        overlay.fill(BG_OVERLAY)
        surface.blit(overlay, (0, 0))

        # sombra do painel
        sr = pygame.Rect(PANEL_X + 5, PANEL_Y + 5, PANEL_W, PANEL_H)
        sh = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
        pygame.draw.rect(sh, (120, 150, 190, 50), sh.get_rect(), border_radius=20)
        surface.blit(sh, sr.topleft)

        # painel
        panel = pygame.Rect(PANEL_X, PANEL_Y, PANEL_W, PANEL_H)
        pygame.draw.rect(surface, PANEL_BG, panel, border_radius=20)
        pygame.draw.rect(surface, PANEL_BORDER, panel, 1, border_radius=20)

        # título com ícone de gota
        title = self._font_title.render("💧  Configurações", True, TEXT_DARK)
        surface.blit(title, title.get_rect(centerx=WIN_W // 2, y=PANEL_Y + 16))

        # linha separadora
        pygame.draw.line(surface, PANEL_BORDER,
                         (PANEL_X + 20, PANEL_Y + 50),
                         (PANEL_X + PANEL_W - 20, PANEL_Y + 50), 1)

        # campos
        for field in self._fields:
            field.draw(surface, self._font_lbl, self._font_hint, self._font_inp)

        # botão Salvar
        pygame.draw.rect(surface, BTN_SAVE, self._btn_save, border_radius=10)
        save_lbl = self._font_lbl.render("✓  Salvar alterações", True, (255, 255, 255))
        surface.blit(save_lbl, save_lbl.get_rect(center=self._btn_save.center))

        # botão Cancelar
        pygame.draw.rect(surface, BTN_CANCEL, self._btn_cancel, border_radius=10)
        pygame.draw.rect(surface, BTN_CANCEL_B, self._btn_cancel, 1, border_radius=10)
        cancel_lbl = self._font_lbl.render("✕  Cancelar", True, TEXT_MED)
        surface.blit(cancel_lbl, cancel_lbl.get_rect(center=self._btn_cancel.center))
