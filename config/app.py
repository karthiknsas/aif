from dataclasses import dataclass, field
from typing import Dict, Literal, Optional


@dataclass
class AppConfig:
    # inprocess: use local model runner; remote_model: call deployed runner
    mode: Literal["inprocess", "remote_model"] = "inprocess"
    remote_model_url: Optional[str] = None
    log_level: str = "INFO"
    log_dir: str = "logs"  # base folder for app logs
    log_path: Optional[str] = None  # set to a file path to also log to disk
    session_store: str = "data/sessions"  # base folder for session metadata
    guardrail_policy: str = "allow_all"  # placeholder policy name; update when defined
    tracing_enabled: bool = False  # Enable when AI Toolkit tracing is wired
    ui_config: Dict[str, object] = field(
        default_factory=lambda: {
            "show_model": True,
            "allow_param_edit": ["temperature", "max_output_tokens", "max_context"],
        }
    )

    def ui_view(self) -> Dict[str, object]:
        return {
            "mode": self.mode,
            "remote_model_url": self.remote_model_url,
            "log_level": self.log_level,
            "log_dir": self.log_dir,
            "log_path": self.log_path,
            "session_store": self.session_store,
            "guardrail_policy": self.guardrail_policy,
            "tracing_enabled": self.tracing_enabled,
            "ui_config": self.ui_config,
        }
