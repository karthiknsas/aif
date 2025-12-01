"""
ONNX Runtime-based model runner with greedy decoding.

Assumes a decoder-only model that accepts input_ids/attention_mask (and optional
position_ids). Uses transformers AutoTokenizer for encoding/decoding.
"""

import logging
from typing import Dict, Iterable, List, Optional

import numpy as np

from config.model import ModelConfig


class ModelRunner:
    def __init__(self, config: ModelConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.session = None
        self.tokenizer = None
        self.input_names = set()
        self._init_session()
        self._init_tokenizer()

    def _init_session(self):
        try:
            import onnxruntime as ort
        except ImportError:
            self.logger.warning(
                "onnxruntime not installed; model runner is inactive. "
                "Install onnxruntime to enable local inference."
            )
            return

        opts = ort.SessionOptions()
        opts.graph_optimization_level = getattr(
            ort.GraphOptimizationLevel,
            self.config.graph_optimization,
            ort.GraphOptimizationLevel.ORT_ENABLE_ALL,
        )
        if self.config.num_threads and self.config.num_threads > 0:
            opts.intra_op_num_threads = self.config.num_threads

        self.session = ort.InferenceSession(
            self.config.model_path,
            sess_options=opts,
            providers=[self.config.provider],
        )
        self.input_names = {i.name for i in self.session.get_inputs()}
        self.logger.info(
            "Initialized ONNXRuntime session",
            extra={
                "provider": self.config.provider,
                "threads": self.config.num_threads,
                "inputs": list(self.input_names),
            },
        )

    def _init_tokenizer(self):
        try:
            from transformers import AutoTokenizer
        except ImportError:
            self.logger.warning("transformers not installed; cannot tokenize for ONNX runner.")
            return
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.tokenizer_path,
                local_files_only=True,
                trust_remote_code=True,
            )
            # Ensure pad token exists to build attention masks cleanly.
            if self.tokenizer.pad_token_id is None and self.tokenizer.eos_token_id is not None:
                self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        except Exception as exc:
            self.logger.error("Failed to load tokenizer", extra={"error": str(exc)})
            self.tokenizer = None

    def _format_chat(self, messages: List[Dict[str, str]]) -> str:
        if self.tokenizer and hasattr(self.tokenizer, "apply_chat_template"):
            try:
                return self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                    return_tensors=None,
                )
            except Exception:
                pass
        # Fallback: simple role-tagged format.
        parts = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            parts.append(f"{role}: {content}")
        parts.append("assistant:")
        return "\n".join(parts)

    def _encode(self, messages: List[Dict[str, str]]) -> Dict[str, np.ndarray]:
        if self.tokenizer is None:
            raise RuntimeError("Tokenizer unavailable; install transformers and ensure tokenizer files exist.")
        text = self._format_chat(messages)
        encoded = self.tokenizer(
            text,
            return_tensors="np",
            add_special_tokens=True,
        )
        # Ensure attention_mask exists.
        if "attention_mask" not in encoded:
            encoded["attention_mask"] = np.ones_like(encoded["input_ids"])
        return encoded

    def _run_step(self, input_ids: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
        if self.session is None:
            raise RuntimeError("ModelRunner is inactive; install/configure onnxruntime and model files.")
        feeds: Dict[str, np.ndarray] = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
        }
        if "position_ids" in self.input_names:
            feeds["position_ids"] = np.arange(input_ids.shape[1], dtype=np.int64)[None, :]

        outputs = self.session.run(None, feeds)
        # Assume first output is logits [batch, seq, vocab]
        return outputs[0]

    def _truncate_context(self, input_ids: np.ndarray, attention_mask: np.ndarray) -> Dict[str, np.ndarray]:
        max_len = self.config.max_context
        if input_ids.shape[1] <= max_len:
            return {"input_ids": input_ids, "attention_mask": attention_mask}
        return {
            "input_ids": input_ids[:, -max_len:],
            "attention_mask": attention_mask[:, -max_len:],
        }

    def generate(self, messages: List[Dict[str, str]], params: Optional[Dict[str, object]] = None) -> str:
        if self.session is None:
            raise RuntimeError("ModelRunner is inactive; install/configure onnxruntime and model files.")
        encoded = self._encode(messages)
        encoded = self._truncate_context(encoded["input_ids"], encoded["attention_mask"])

        input_ids = encoded["input_ids"]
        attention_mask = encoded["attention_mask"]

        params = params or {}
        max_new_tokens = int(params.get("max_tokens", self.config.max_output_tokens))
        stop_tokens = params.get("stop") or []

        eos_token_id = self.tokenizer.eos_token_id if self.tokenizer else None
        generated = input_ids

        for _ in range(max_new_tokens):
            logits = self._run_step(generated, attention_mask)
            next_token = int(np.argmax(logits[:, -1, :], axis=-1)[0])

            generated = np.concatenate([generated, np.array([[next_token]], dtype=np.int64)], axis=1)
            attention_mask = np.concatenate(
                [attention_mask, np.ones((1, 1), dtype=attention_mask.dtype)], axis=1
            )

            if eos_token_id is not None and next_token == eos_token_id:
                break

            decoded_full = self.tokenizer.decode(generated[0], skip_special_tokens=True) if self.tokenizer else ""
            if any(stop in decoded_full for stop in stop_tokens):
                break

        decoded = self.tokenizer.decode(generated[0], skip_special_tokens=True) if self.tokenizer else ""
        if "assistant:" in decoded:
            decoded = decoded.split("assistant:", 1)[-1].strip()
        return decoded

    def stream_generate(
        self, messages: List[Dict[str, str]], params: Optional[Dict[str, object]] = None
    ) -> Iterable[str]:
        if self.session is None:
            raise RuntimeError("ModelRunner is inactive; install/configure onnxruntime and model files.")
        encoded = self._encode(messages)
        encoded = self._truncate_context(encoded["input_ids"], encoded["attention_mask"])

        input_ids = encoded["input_ids"]
        attention_mask = encoded["attention_mask"]

        params = params or {}
        max_new_tokens = int(params.get("max_tokens", self.config.max_output_tokens))
        stop_tokens = params.get("stop") or []

        eos_token_id = self.tokenizer.eos_token_id if self.tokenizer else None
        generated = input_ids

        for _ in range(max_new_tokens):
            logits = self._run_step(generated, attention_mask)
            next_token = int(np.argmax(logits[:, -1, :], axis=-1)[0])

            generated = np.concatenate([generated, np.array([[next_token]], dtype=np.int64)], axis=1)
            attention_mask = np.concatenate(
                [attention_mask, np.ones((1, 1), dtype=attention_mask.dtype)], axis=1
            )

            if eos_token_id is not None and next_token == eos_token_id:
                break

            token_text = self.tokenizer.decode([next_token], skip_special_tokens=True) if self.tokenizer else ""
            yield token_text

            decoded_full = self.tokenizer.decode(generated[0], skip_special_tokens=True) if self.tokenizer else ""
            if any(stop in decoded_full for stop in stop_tokens):
                break
