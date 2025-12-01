from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class IRISConfig:
    enabled: bool = False
    host: str = "localhost"
    port: int = 1972
    username: str = "superuser"
    password: str = "****"  # keep masked; do not expose raw value to UI
    namespace: str = "IRISAPP"
    schema_source: Optional[str] = None  # e.g., SQL query or file path
    cache_path: str = "data/cache/iris_schema.json"
    preload: bool = False  # controls whether schema is preloaded at startup
    ui_exposed_fields: Dict[str, object] = field(
        default_factory=lambda: {
            "host": True,
            "port": True,
            "namespace": True,
            "schema_source": True,
            # secrets remain masked; password never surfaced
        }
    )

    def ui_view(self) -> Dict[str, object]:
        view = {}
        for key, allowed in self.ui_exposed_fields.items():
            if allowed and hasattr(self, key):
                view[key] = getattr(self, key)
        view["password"] = "****"
        view["preload"] = self.preload
        return view
