"""
Centralized configuration loader for model, app, and IRIS settings.

All configuration stays in-process but is structured so the model runner
can be moved out-of-process later without changing callers.
"""

from dataclasses import dataclass, field
from typing import Dict

from .app import AppConfig
from .iris import IRISConfig
from .model import ModelConfig


@dataclass
class Settings:
    app: AppConfig = field(default_factory=AppConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    iris: IRISConfig = field(default_factory=IRISConfig)

    def ui_safe_view(self) -> Dict[str, object]:
        """
        Expose only UI-safe fields; secrets remain masked/omitted.
        """
        ui = {
            "app": self.app.ui_view(),
            "model": self.model.ui_view(),
            "iris": self.iris.ui_view(),
        }
        return ui


# A singleton-style settings object for easy import.
settings = Settings()
