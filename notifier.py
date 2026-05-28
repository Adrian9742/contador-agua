import time
import threading

try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False

try:
    from plyer import notification as _plyer_notification
    _PLYER_AVAILABLE = True
except ImportError:
    _PLYER_AVAILABLE = False

FLASH_DURATION = 3.0  # seconds


class Notifier:
    def __init__(self):
        self._alert_sound = None
        self._success_sound = None
        self._sounds_loaded = False

    def load_sounds(self) -> None:
        if not _PYGAME_AVAILABLE or self._sounds_loaded:
            return
        try:
            from pathlib import Path
            assets = Path(__file__).parent / "assets"
            alert_path = assets / "alert.wav"
            success_path = assets / "success.wav"
            if alert_path.exists():
                self._alert_sound = pygame.mixer.Sound(str(alert_path))
            if success_path.exists():
                self._success_sound = pygame.mixer.Sound(str(success_path))
            self._sounds_loaded = True
        except Exception:
            pass

    def fire_all(self, state) -> None:
        threading.Thread(target=self._fire_toast, daemon=True).start()
        self._fire_sound(success=False)
        self._fire_flash(state)

    def fire_success(self, state) -> None:
        threading.Thread(target=self._fire_toast_success, daemon=True).start()
        self._fire_sound(success=True)
        self._fire_flash(state, duration=5.0)

    def _fire_toast(self) -> None:
        if not _PLYER_AVAILABLE:
            return
        try:
            _plyer_notification.notify(
                title="Hora de beber água! 💧",
                message="Você não bebeu água nos últimos minutos. Beba agora!",
                timeout=5,
                app_name="Contador de Água",
            )
        except Exception:
            pass

    def _fire_toast_success(self) -> None:
        if not _PLYER_AVAILABLE:
            return
        try:
            _plyer_notification.notify(
                title="Meta atingida! 🎉",
                message="Parabéns! Você bateu sua meta diária de hidratação!",
                timeout=8,
                app_name="Contador de Água",
            )
        except Exception:
            pass

    def _fire_sound(self, success: bool) -> None:
        if not _PYGAME_AVAILABLE:
            return
        try:
            sound = self._success_sound if success else self._alert_sound
            if sound:
                sound.play()
            else:
                # fallback: system beep via winsound if available
                try:
                    import winsound
                    freq = 880 if success else 440
                    winsound.Beep(freq, 400)
                except Exception:
                    pass
        except Exception:
            pass

    def _fire_flash(self, state, duration: float = FLASH_DURATION) -> None:
        state.flash_until = time.time() + duration
