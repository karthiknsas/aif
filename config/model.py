from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ModelConfig:
    # Paths to model artifacts
    model_path: str = "Models/model.onnx"
    tokenizer_path: str = "Models/tokenizer.json"
    added_tokens_path: Optional[str] = "Models/added_tokens.json"
    config_path: Optional[str] = "Models/inference_model.json"

    # Runtime and sampling
    max_context: int = 4096
    max_output_tokens: int = 512
    temperature: float = 0.2
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.05
    streaming: bool = True

    # ONNX Runtime tuning for CPU
    provider: str = "CPUExecutionProvider"
    num_threads: int = 0  # 0 lets ORT choose; override to pin
    graph_optimization: str = "ORT_ENABLE_ALL"

    def ui_view(self) -> Dict[str, object]:
        return {
            "model_path": self.model_path,
            "tokenizer_path": self.tokenizer_path,
            "max_context": self.max_context,
            "max_output_tokens": self.max_output_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repetition_penalty": self.repetition_penalty,
            "streaming": self.streaming,
        }
