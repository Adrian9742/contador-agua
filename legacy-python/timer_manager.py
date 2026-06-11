import threading
import time


class TimerManager:
    def __init__(self, state, notifier):
        self._state = state
        self._notifier = notifier
        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        state.register_drink_callback(self._on_drink)

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _on_drink(self) -> None:
        # last_drink_time already updated in AppState.add_water
        pass

    def time_remaining(self) -> int:
        elapsed = time.time() - self._state.last_drink_time
        remaining = self._state.interval_min * 60 - elapsed
        return max(0, int(remaining))

    def _loop(self) -> None:
        while self._running:
            time.sleep(1)
            if self._state.goal_reached:
                continue
            elapsed = time.time() - self._state.last_drink_time
            interval_s = self._state.interval_min * 60
            if elapsed >= interval_s:
                self._notifier.fire_all(self._state)
                # advance last_drink_time by one interval so it doesn't spam
                self._state.last_drink_time = time.time()
