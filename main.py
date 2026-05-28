import sys
import time
import pygame

from state import AppState
from notifier import Notifier
from timer_manager import TimerManager
from renderer import Renderer, WIN_W, WIN_H, init_fonts
from config_screen import ConfigScreen


FPS = 60
WINDOW_TITLE = "Contador de Água 💧"


def _midnight_reset_check(state: AppState) -> None:
    """Zero the day if the date changed since last drink."""
    from datetime import datetime, date
    last = datetime.fromtimestamp(state.last_drink_time).date()
    if last < date.today():
        state.reset_day()


def main() -> None:
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption(WINDOW_TITLE)
    surface = pygame.display.set_mode((WIN_W, WIN_H))
    clock = pygame.time.Clock()
    init_fonts()

    state    = AppState.load()
    notifier = Notifier()
    notifier.load_sounds()
    timer    = TimerManager(state, notifier)
    renderer = Renderer()
    config   = ConfigScreen()

    timer.start()

    show_config = False
    prev_goal_reached = state.goal_reached
    midnight_check_timer = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if show_config:
                result = config.handle_event(event, state)
                if result in ("saved", "cancelled"):
                    show_config = False
                    if result == "saved":
                        timer._on_drink()  # reset timer with new interval
            else:
                action = renderer.handle_event(event, state, timer)
                if action == "drink_quick":
                    state.add_water(state.default_cup_ml)
                elif action and action.startswith("drink_manual:"):
                    ml = int(action.split(":")[1])
                    state.add_water(ml)
                elif action == "reset":
                    state.reset_day()
                elif action == "config":
                    show_config = True
                    config.open(state)

        # detect goal reached for the first time this session
        if state.goal_reached and not prev_goal_reached:
            notifier.fire_success(state)
        prev_goal_reached = state.goal_reached

        # midnight auto-reset (check every ~60s)
        midnight_check_timer += 1
        if midnight_check_timer >= FPS * 60:
            midnight_check_timer = 0
            _midnight_reset_check(state)

        renderer.draw(surface, state, timer.time_remaining())
        if show_config:
            config.draw(surface)

        pygame.display.flip()
        clock.tick(FPS)

    timer.stop()
    state.save()
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
