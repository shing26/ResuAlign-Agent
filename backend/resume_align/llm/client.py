"""Unified LLM client with multi-provider support."""

from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator

import google.genai as genai
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from resume_align.config import LLMProvider, PROVIDER_CONFIGS, settings

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> str:
    if not text or not text.strip():
        return "{}"
    text = text.strip()
    text = re.sub(r"^```(?:json|)\s*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n?```\s*$", "", text)
    text = re.sub(r"^`(.*)`$", r"\1", text)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    return text.strip()


def _make_example(model: type) -> str:
    schema = model.model_json_schema()
    defs = schema.get("$defs", {})
    result = {}

    def example_for(prop_name: str, prop: dict) -> Any:
        ref = prop.get("$ref", "")
        if ref:
            ref_key = ref.split("/")[-1]
            if ref_key in defs:
                return example_for("", defs[ref_key])
            return {}
        typ = prop.get("type", "string")
        if typ == "number":
            return 0.0
        if typ == "integer":
            return 0
        if typ == "boolean":
            return False
        if typ == "array":
            return ["example"]
        if typ == "object":
            obj = {}
            for k, v in prop.get("properties", {}).items():
                obj[k] = example_for(k, v)
            return obj
        return prop_name.replace("_", " ")

    for name, prop in schema.get("properties", {}).items():
        result[name] = example_for(name, prop)
    return json.dumps(result, indent=2, ensure_ascii=False)


def _inject_schema(system_prompt: str, response_model: type) -> str:
    example = _make_example(response_model)
    return (
        system_prompt.strip()
        + "\n\nYou MUST return valid JSON matching this exact structure.\n"
        + "Do NOT add extra fields, explanations, markdown, or code fences.\n"
        + f"Expected JSON structure:\n{example}"
    )


class LLMClient(ABC):
    @abstractmethod
    async def generate_structured(self, system_prompt, user_prompt, response_model, **kwargs) -> Any: ...

    @abstractmethod
    async def generate_text(self, system_prompt, user_prompt, **kwargs) -> str: ...

    @abstractmethod
    async def generate_streaming_text(self, system_prompt, user_prompt, **kwargs) -> AsyncGenerator[str, None]: ...


class OpenAIClient(LLMClient):
    def __init__(self, api_key=None, base_url=None, model=None):
        self.client = AsyncOpenAI(api_key=api_key or settings.api_key, base_url=base_url or settings.base_url)
        self.model = model or settings.model

    async def generate_structured(self, system_prompt, user_prompt, response_model, **kwargs):
        model = kwargs.get("model", self.model)
        temp = kwargs.get("temperature", 0.1)
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

        # Strategy 0: Ollama native API with format=json (forces valid JSON output)
        if "11434" in str(getattr(self.client, "_base_url", self.client.base_url)):
            try:
                import httpx
                raw = await httpx.AsyncClient(timeout=120).post(
                    str(getattr(self.client, "_base_url", self.client.base_url)).replace("/v1", "/api/chat"),
                    json={"model": model, "messages": messages, "format": "json", "stream": False,
                          "options": {"temperature": float(temp)}},
                )
                data = raw.json()
                text = data["message"]["content"]
                text = text[text.find("{"):text.rfind("}")+1] if "{" in text else text
                return response_model(**json.loads(text))
            except Exception as e:
                logger.debug("Strategy 0 (Ollama native JSON) failed: %s", e)
        try:
            response = await self.client.beta.chat.completions.parse(
                model=model, messages=messages, response_format=response_model, temperature=temp,
            )
            return response.choices[0].message.parsed
        except Exception as e:
            logger.debug("Strategy 1 (structured API) failed: %s", e)
        enhanced = _inject_schema(system_prompt, response_model)
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": enhanced}, {"role": "user", "content": user_prompt}],
                response_format={"type": "json_object"}, temperature=temp,
            )
            data = json.loads(_extract_json(response.choices[0].message.content or "{}"))
            return response_model(**data)
        except Exception as e:
            logger.debug("Strategy 2 (JSON mode) failed: %s", e)
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": enhanced}, {"role": "user", "content": user_prompt}],
                temperature=temp,
            )
            data = json.loads(_extract_json(response.choices[0].message.content or "{}"))
            return response_model(**data)
        except Exception as e:
            logger.error("All 3 strategies failed for %s: %s", response_model.__name__, e)
            raise

    async def generate_text(self, system_prompt, user_prompt, **kwargs):
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=kwargs.get("temperature", 0.1),
        )
        return response.choices[0].message.content or ""

    async def generate_streaming_text(self, system_prompt, user_prompt, **kwargs):
        stream = await self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=kwargs.get("temperature", 0.1), stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content


class AnthropicClient(LLMClient):
    def __init__(self, api_key=None, model=None):
        self.client = AsyncAnthropic(api_key=api_key or settings.anthropic_api_key)
        self.model = model or settings.anthropic_model

    async def generate_structured(self, system_prompt, user_prompt, response_model, **kwargs):
        enhanced = _inject_schema(system_prompt, response_model)
        response = await self.client.messages.create(
            model=kwargs.get("model", self.model), system=enhanced,
            messages=[{"role": "user", "content": user_prompt + "\n\nReturn ONLY valid JSON. No markdown."}],
            max_tokens=kwargs.get("max_tokens", 4096), temperature=kwargs.get("temperature", 0.1),
        )
        data = json.loads(_extract_json(response.content[0].text if response.content else "{}"))
        return response_model(**data)

    async def generate_text(self, system_prompt, user_prompt, **kwargs):
        response = await self.client.messages.create(
            model=kwargs.get("model", self.model), system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=kwargs.get("max_tokens", 4096), temperature=kwargs.get("temperature", 0.1),
        )
        return response.content[0].text if response.content else ""

    async def generate_streaming_text(self, system_prompt, user_prompt, **kwargs):
        async with self.client.messages.stream(
            model=kwargs.get("model", self.model), system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=kwargs.get("max_tokens", 4096), temperature=kwargs.get("temperature", 0.1),
        ) as stream:
            async for chunk in stream:
                if chunk.type == "content_block_delta" and chunk.delta.text:
                    yield chunk.delta.text


class GeminiClient(LLMClient):
    def __init__(self, api_key=None, model=None):
        self.client = genai.Client(api_key=api_key or settings.gemini_api_key)
        self.model = model or settings.gemini_model

    async def generate_structured(self, system_prompt, user_prompt, response_model, **kwargs):
        enhanced = _inject_schema(system_prompt, response_model)
        response = self.client.models.generate_content(
            model=kwargs.get("model", self.model), contents=user_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=enhanced, response_mime_type="application/json",
            ),
        )
        data = json.loads(_extract_json(response.text))
        return response_model(**data)

    async def generate_text(self, system_prompt, user_prompt, **kwargs):
        response = self.client.models.generate_content(
            model=kwargs.get("model", self.model), contents=user_prompt,
            config=genai.types.GenerateContentConfig(system_instruction=system_prompt),
        )
        return response.text

    async def generate_streaming_text(self, system_prompt, user_prompt, **kwargs):
        response = self.client.models.generate_content_stream(
            model=kwargs.get("model", self.model), contents=user_prompt,
            config=genai.types.GenerateContentConfig(system_instruction=system_prompt),
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text


class MockClient(LLMClient):
    async def generate_structured(self, system_prompt, user_prompt, response_model, **kwargs):
        import asyncio
        await asyncio.sleep(settings.mock_delay_ms / 1000)
        return response_model()

    async def generate_text(self, system_prompt, user_prompt, **kwargs):
        import asyncio
        await asyncio.sleep(settings.mock_delay_ms / 1000)
        return "[Mock] Simulated response."

    async def generate_streaming_text(self, system_prompt, user_prompt, **kwargs):
        import asyncio
        for chunk in ["[Mock] ", "streaming ", "response."]:
            await asyncio.sleep(50 / 1000)
            yield chunk


def get_llm_client(provider=None, api_key=None, model=None, base_url=None) -> LLMClient:
    return create_llm_client(provider, api_key, model, base_url)


def create_llm_client(provider=None, api_key=None, model=None, base_url=None) -> LLMClient:
    p = provider if provider is not None else settings.llm_provider
    if isinstance(p, str):
        try:
            p = LLMProvider(p.lower())
        except ValueError:
            p = LLMProvider.OPENAI

    if p == LLMProvider.OLLAMA:
        logger.info("Ollama: model=" + str(settings.ollama_model))
        return OpenAIClient(api_key="ollama", base_url=settings.ollama_api_url, model=settings.ollama_model)
    if p == LLMProvider.GEMINI:
        m = model or settings.gemini_model
        logger.info("Gemini: model=" + str(m))
        return GeminiClient(api_key=api_key, model=m)
    if p == LLMProvider.ANTHROPIC:
        m = model or settings.anthropic_model
        logger.info("Anthropic: model=" + str(m))
        return AnthropicClient(api_key=api_key, model=m)
    if p == LLMProvider.MOCK:
        return MockClient()

    cfg = PROVIDER_CONFIGS.get(p.value if isinstance(p, LLMProvider) else str(p), {})
    final_key = api_key or settings.api_key
    final_url = base_url or cfg.get("base_url", "") or settings.base_url
    final_model = model or cfg.get("default_model", "") or settings.model
    logger.info("OpenAI-compat: provider=" + str(p) + " model=" + str(final_model))
    return OpenAIClient(api_key=final_key, base_url=final_url, model=final_model)