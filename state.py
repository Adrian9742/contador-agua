import json
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

DEFAULTS = {
    "goal_ml": 2000,
    "interval_min": 30,
    "default_cup_ml": 200,
}


@dataclass
class AppState:
    goal_ml: int = 2000
    interval_min: int = 30
    default_cup_ml: int = 200
    consumed_ml: int = 0
    last_drink_time: float = field(default_factory=time.time)
    goal_reached: bool = False

    # set by notifier so renderer can read it
    flash_until: float = 0.0

    _on_drink_callbacks: list = field(default_factory=list, repr=False, compare=False)

    def add_water(self, ml: int) -> None:
        if self.goal_reached:
            return
        self.consumed_ml += max(0, ml)
        self.last_drink_time = time.time()
        if self.consumed_ml >= self.goal_ml:
            self.consumed_ml = self.goal_ml
            self.goal_reached = True
        for cb in self._on_drink_callbacks:
            cb()

    def reset_day(self) -> None:
        self.consumed_ml = 0
        self.last_drink_time = time.time()
        self.goal_reached = False

    def percent(self) -> float:
        if self.goal_ml <= 0:
            return 0.0
        return min(1.0, self.consumed_ml / self.goal_ml)

    def register_drink_callback(self, fn) -> None:
        self._on_drink_callbacks.append(fn)

    def save(self) -> None:
        data = {
            "goal_ml": self.goal_ml,
            "interval_min": self.interval_min,
            "default_cup_ml": self.default_cup_ml,
        }
        CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls) -> "AppState":
        if not CONFIG_PATH.exists():
            return cls()
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return cls(
                goal_ml=int(data.get("goal_ml", DEFAULTS["goal_ml"])),
                interval_min=int(data.get("interval_min", DEFAULTS["interval_min"])),
                default_cup_ml=int(data.get("default_cup_ml", DEFAULTS["default_cup_ml"])),
            )
        except (json.JSONDecodeError, ValueError):
            return cls()
