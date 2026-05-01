from __future__ import annotations

import os
import time
from typing import Any

import httpx
from pydantic import BaseModel, Field


class ChatResult(BaseModel):
    text: str
    model: str
    usage: dict[str, int] = Field(default_factory=dict)
    finish_reason: str | None = None
    latency_ms: int
    base_url: str


class LMStudioClient:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_sec: int = 120,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ):
        self.base_url = (
            base_url or os.getenv("OACS_LMSTUDIO_BASE_URL") or "http://localhost:1234/v1"
        ).rstrip("/")
        self.model = model or os.getenv("OACS_LMSTUDIO_MODEL") or "gemma-4-e2b"
        self.timeout_sec = timeout_sec
        self.temperature = temperature
        self.max_tokens = max_tokens

    def chat(self, prompt: str, system: str | None = None) -> str:
        return self.chat_result(prompt, system).text

    def chat_result(self, prompt: str, system: str | None = None) -> ChatResult:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system or "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        started = time.perf_counter()
        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions", json=payload, timeout=self.timeout_sec
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"LM Studio unavailable at {self.base_url}; start the server or change config"
            ) from exc
        latency_ms = int((time.perf_counter() - started) * 1000)
        body = response.json()
        choice = body["choices"][0]
        usage = body.get("usage") if isinstance(body.get("usage"), dict) else {}
        normalized_usage = {
            key: int(value)
            for key, value in usage.items()
            if isinstance(key, str) and isinstance(value, int)
        }
        return ChatResult(
            text=str(choice["message"]["content"]),
            model=str(body.get("model", self.model)),
            usage=normalized_usage,
            finish_reason=choice.get("finish_reason"),
            latency_ms=latency_ms,
            base_url=self.base_url,
        )

    def structured_json(self, prompt: str, schema_hint: dict[str, Any]) -> str:
        return self.chat(f"{prompt}\nReturn JSON matching: {schema_hint}")

    def embeddings(self, texts: list[str]) -> list[list[float]]:
        payload = {"model": self.model, "input": texts}
        try:
            response = httpx.post(
                f"{self.base_url}/embeddings", json=payload, timeout=self.timeout_sec
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError("LM Studio embeddings endpoint unavailable") from exc
        return [item["embedding"] for item in response.json()["data"]]
