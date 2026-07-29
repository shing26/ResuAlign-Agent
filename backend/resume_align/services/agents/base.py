"""Base agent abstraction for PydanticAI-style agents."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from resume_align.infra.llm import LLMClient

logger = logging.getLogger(__name__)

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class BaseAgent(ABC, Generic[InputT, OutputT]):
    """Generic base agent with structured input/output via PydanticAI pattern."""

    def __init__(self, llm: LLMClient, name: str = "") -> None:
        self.llm = llm
        self.name = name or self.__class__.__name__

    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt that defines this agent role & constraints."""

    @abstractmethod
    def output_model(self) -> type[OutputT]:
        """Return the Pydantic model for structured output."""

    async def run(self, input_data: InputT) -> OutputT:
        """Execute agent with structured input, return structured output."""
        logger.info("[%s] Running agent...", self.name)
        user_prompt = self._format_input(input_data)
        result = await self.llm.generate_structured(
            system_prompt=self.system_prompt(),
            user_prompt=user_prompt,
            response_model=self.output_model(),
        )
        logger.info("[%s] Agent completed successfully", self.name)
        return result

    async def run_streaming(self, input_data: InputT):
        """Execute agent with streaming text output."""
        logger.info("[%s] Running streaming agent...", self.name)
        user_prompt = self._format_input(input_data)
        async for chunk in self.llm.generate_streaming_text(
            system_prompt=self.system_prompt(),
            user_prompt=user_prompt,
        ):
            yield chunk

    def _format_input(self, input_data: InputT) -> str:
        """Convert structured input to a prompt string."""
        return input_data.model_dump_json(indent=2)
