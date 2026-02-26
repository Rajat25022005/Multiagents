"""
Unified LLM router with provider abstraction and optional Langfuse tracing.
"""
from __future__ import annotations

import os
import time
from typing import Any, Generator

from core.config import get_settings

settings = get_settings()

# Optional Langfuse tracing
_langfuse = None
if settings.langfuse_public_key and settings.langfuse_secret_key:
    try:
        from langfuse import Langfuse
        _langfuse = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
    except ImportError:
        pass


class LLMResponse:
    def __init__(self, content: str, model: str, usage: dict | None = None):
        self.content = content
        self.model = model
        self.usage = usage or {}


class LLMRouter:
    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
    ):
        self.provider = (provider or settings.llm_provider).lower()
        self.model = model or settings.default_model

    # ──────────────────────────────────────────────────────────────────────────
    # Public interface
    # ──────────────────────────────────────────────────────────────────────────

    def chat(
        self,
        messages: list[dict],
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        trace_name: str = "llm_call",
        **kwargs,
    ) -> LLMResponse:
        """Send a chat request and return a unified LLMResponse."""
        if system:
            messages = [{"role": "system", "content": system}] + messages

        span = self._start_trace(trace_name, messages)
        t0 = time.time()
        try:
            response = self._dispatch(messages, temperature, max_tokens, **kwargs)
            self._end_trace(span, response.content, time.time() - t0)
            return response
        except Exception as exc:
            self._end_trace(span, str(exc), time.time() - t0, error=True)
            raise

    def stream(
        self,
        messages: list[dict],
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Generator[str, None, None]:
        """Yield text chunks for streaming responses."""
        if system:
            messages = [{"role": "system", "content": system}] + messages
        yield from self._dispatch_stream(messages, temperature, max_tokens)

    # ──────────────────────────────────────────────────────────────────────────
    # Provider dispatch
    # ──────────────────────────────────────────────────────────────────────────

    def _dispatch(self, messages, temperature, max_tokens, **kwargs) -> LLMResponse:
        match self.provider:
            case "openai":
                return self._openai(messages, temperature, max_tokens, **kwargs)
            case "groq":
                return self._groq(messages, temperature, max_tokens)
            case "gemini":
                return self._gemini(messages, temperature, max_tokens)
            case "ollama":
                return self._ollama(messages, temperature, max_tokens)
            case _:
                raise ValueError(f"Unknown LLM provider: {self.provider}")

    def _dispatch_stream(self, messages, temperature, max_tokens):
        match self.provider:
            case "openai":
                yield from self._openai_stream(messages, temperature, max_tokens)
            case "groq":
                yield from self._groq_stream(messages, temperature, max_tokens)
            case "ollama":
                yield from self._ollama_stream(messages, temperature, max_tokens)
            case _:
                # Fallback: non-streaming response in one chunk
                resp = self._dispatch(messages, temperature, max_tokens)
                yield resp.content

    # ──────────────────────────────────────────────────────────────────────────
    # Provider implementations
    # ──────────────────────────────────────────────────────────────────────────

    def _openai(self, messages, temperature, max_tokens, **kwargs) -> LLMResponse:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return LLMResponse(
            content=resp.choices[0].message.content,
            model=resp.model,
            usage=resp.usage.model_dump() if resp.usage else {},
        )

    def _openai_stream(self, messages, temperature, max_tokens):
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        stream = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _groq(self, messages, temperature, max_tokens) -> LLMResponse:
        from groq import Groq
        client = Groq(api_key=settings.groq_api_key)
        resp = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return LLMResponse(
            content=resp.choices[0].message.content,
            model=resp.model,
        )

    def _groq_stream(self, messages, temperature, max_tokens):
        from groq import Groq
        client = Groq(api_key=settings.groq_api_key)
        stream = client.chat.completions.create(
            model=self.model, messages=messages,
            temperature=temperature, max_tokens=max_tokens, stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _gemini(self, messages, temperature, max_tokens) -> LLMResponse:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(self.model)
        # Convert to Gemini format
        history, last = messages[:-1], messages[-1]
        def _to_gemini_role(role: str) -> str:
            return "model" if role == "assistant" else "user"

        chat = model.start_chat(history=[
            {"role": _to_gemini_role(m["role"]), "parts": [m["content"]]}
            for m in history
            if m["role"] != "system"
        ])
        resp = chat.send_message(last["content"])
        return LLMResponse(content=resp.text, model=self.model)

    def _ollama(self, messages, temperature, max_tokens) -> LLMResponse:
        import httpx
        resp = httpx.post(
            f"{settings.ollama_base_url}/api/chat",
            json={"model": self.model, "messages": messages, "stream": False,
                  "options": {"temperature": temperature, "num_predict": max_tokens}},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return LLMResponse(content=data["message"]["content"], model=self.model)

    def _ollama_stream(self, messages, temperature, max_tokens):
        import httpx, json
        with httpx.stream(
            "POST",
            f"{settings.ollama_base_url}/api/chat",
            json={"model": self.model, "messages": messages, "stream": True,
                  "options": {"temperature": temperature, "num_predict": max_tokens}},
            timeout=120,
        ) as r:
            for line in r.iter_lines():
                if line:
                    data = json.loads(line)
                    if content := data.get("message", {}).get("content"):
                        yield content

    # ──────────────────────────────────────────────────────────────────────────
    # Tracing helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _start_trace(self, name: str, messages: list[dict]):
        if _langfuse:
            try:
                return _langfuse.generation(
                    name=name,
                    model=self.model,
                    input=messages,
                )
            except Exception:
                pass
        return None

    def _end_trace(self, span, output: str, latency: float, error: bool = False):
        if span and _langfuse:
            try:
                span.end(output=output, status_message="error" if error else "success")
            except Exception:
                pass
