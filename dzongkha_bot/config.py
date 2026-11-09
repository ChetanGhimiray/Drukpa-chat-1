"""Configuration. Everything comes from environment variables or a local .env file.

No secret is ever hardcoded here.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
log = logging.getLogger("dzongkha_bot")

KNOWN_PROVIDERS = ("gemini", "openai_compat", "ollama")


def _str(env: Mapping[str, str], key: str, default: str = "") -> str:
    return (env.get(key) or default).strip()


def _int(env: Mapping[str, str], key: str, default: int) -> int:
    try:
        return int(_str(env, key, str(default)))
    except ValueError:
        return default


def _float(env: Mapping[str, str], key: str, default: float) -> float:
    try:
        return float(_str(env, key, str(default)))
    except ValueError:
        return default


def _bool(env: Mapping[str, str], key: str, default: bool = False) -> bool:
    return _str(env, key, "true" if default else "false").lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    provider_order: tuple
    # One shared Dzongkha <-> English translation checkpoint
    dzongkha_translation_model: str
    translate_device: str
    translate_local_files_only: bool
    translate_beams: int
    translate_max_sentences: int
    # Gemini (official google-genai SDK)
    gemini_api_key: str
    gemini_model: str
    gemini_use_search: bool
    # Any OpenAI-compatible FREE endpoint (e.g. Groq, OpenRouter ":free" models)
    compat_base_url: str
    compat_api_key: str
    compat_model: str
    # Local Ollama
    ollama_host: str
    ollama_model: str
    # Generation / cost controls
    max_history_turns: int
    max_message_chars: int
    max_output_tokens: int
    temperature: float
    request_timeout: int
    rate_limit_cooldown: int


def load_settings(env: Optional[Mapping[str, str]] = None) -> Settings:
    """Build Settings. Pass `env` in tests; otherwise reads .env + os.environ."""
    if env is None:
        load_dotenv(ROOT / ".env")
        env = os.environ

    order = []
    for name in _str(env, "PROVIDER_ORDER", "ollama").lower().split(","):
        name = name.strip()
        if not name:
            continue
        if name not in KNOWN_PROVIDERS:
            log.warning("Ignoring unknown provider %r in PROVIDER_ORDER", name)
            continue
        if name not in order:
            order.append(name)

    device = _str(env, "TRANSLATE_DEVICE", "cpu").lower()
    if device not in ("cpu", "cuda", "auto"):
        device = "cpu"

    return Settings(
        provider_order=tuple(order),
        dzongkha_translation_model=_str(
            env,
            "DZONGKHA_TRANSLATION_MODEL",
            "kinleyrabgay/nllb-200-600M-dzo-eng-300k",
        ),
        translate_device=device,
        translate_local_files_only=_bool(env, "TRANSLATE_LOCAL_FILES_ONLY", False),
        translate_beams=_int(env, "TRANSLATE_BEAMS", 4),
        translate_max_sentences=_int(env, "TRANSLATE_MAX_SENTENCES", 40),
        gemini_api_key=_str(env, "GEMINI_API_KEY"),
        gemini_model=_str(env, "GEMINI_MODEL", "gemini-3.6-flash"),
        gemini_use_search=_bool(env, "GEMINI_USE_GOOGLE_SEARCH", True),
        compat_base_url=_str(env, "OPENAI_COMPAT_BASE_URL").rstrip("/"),
        compat_api_key=_str(env, "OPENAI_COMPAT_API_KEY"),
        compat_model=_str(env, "OPENAI_COMPAT_MODEL"),
        ollama_host=_str(env, "OLLAMA_HOST", "http://localhost:11434").rstrip("/"),
        ollama_model=_str(env, "OLLAMA_MODEL", "qwen2.5:3b"),
        max_history_turns=_int(env, "MAX_HISTORY_TURNS", 8),
        max_message_chars=_int(env, "MAX_MESSAGE_CHARS", 1500),
        max_output_tokens=_int(env, "MAX_OUTPUT_TOKENS", 2048),
        temperature=_float(env, "TEMPERATURE", 0.2),
        request_timeout=_int(env, "REQUEST_TIMEOUT_SECONDS", 60),
        rate_limit_cooldown=_int(env, "RATE_LIMIT_COOLDOWN_SECONDS", 60),
    )
