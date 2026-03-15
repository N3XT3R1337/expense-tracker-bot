import os
from dataclasses import dataclass, field


@dataclass
class Config:
    bot_token: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", ""))
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite+aiosqlite:///expenses.db"))
    default_currency: str = field(default_factory=lambda: os.getenv("DEFAULT_CURRENCY", "USD"))
    timezone: str = field(default_factory=lambda: os.getenv("TIMEZONE", "UTC"))
    max_categories_per_user: int = 20
    budget_alert_threshold: float = 0.8
    report_dir: str = field(default_factory=lambda: os.getenv("REPORT_DIR", "reports"))


def load_config() -> Config:
    return Config()
