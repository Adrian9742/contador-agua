import json
import sys
import time
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path


def _config_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


CONFIG_PATH = _config_dir() / "config.json"

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
    flash_until: float = 0.0
    daily_history: dict = field(default_factory=dict)
    best_streak: int = 0

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

    def close_day(self) -> None:
        today = date.today().isoformat()
        self.daily_history[today] = {
            "consumed": self.consumed_ml,
            "goal": self.goal_ml,
        }
        cutoff = (date.today() - timedelta(days=30)).isoformat()
        self.daily_history = {k: v for k, v in self.daily_history.items() if k >= cutoff}
        s = self.streak()
        if s > self.best_streak:
            self.best_streak = s

    def reset_day(self) -> None:
        self.close_day()
        self.consumed_ml = 0
        self.last_drink_time = time.time()
        self.goal_reached = False

    def percent(self) -> float:
        if self.goal_ml <= 0:
            return 0.0
        return min(1.0, self.consumed_ml / self.goal_ml)

    def streak(self) -> int:
        count = 0
        day = date.today() - timedelta(days=1)
        while True:
            entry = self.daily_history.get(day.isoformat())
            if not entry or entry["consumed"] < entry["goal"]:
                break
            count += 1
            day -= timedelta(days=1)
        if self.goal_reached:
            count += 1
        return count

    def last_7_days(self) -> list[dict]:
        """Returns list of 7 dicts (oldest→newest): {date, label, status}
        status: 'done' | 'failed' | 'today'
        """
        today = date.today()
        result = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            label = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"][d.weekday()]
            if i == 0:
                status = "today"
            else:
                entry = self.daily_history.get(d.isoformat())
                if entry and entry["consumed"] >= entry["goal"]:
                    status = "done"
                else:
                    status = "failed"
            result.append({"date": d, "label": label, "status": status})
        return result

    def register_drink_callback(self, fn) -> None:
        self._on_drink_callbacks.append(fn)

    def save(self) -> None:
        data = {
            "goal_ml": self.goal_ml,
            "interval_min": self.interval_min,
            "default_cup_ml": self.default_cup_ml,
            "best_streak": self.best_streak,
            "daily_history": self.daily_history,
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
                best_streak=int(data.get("best_streak", 0)),
                daily_history=data.get("daily_history", {}),
            )
        except (json.JSONDecodeError, ValueError):
            return cls()
