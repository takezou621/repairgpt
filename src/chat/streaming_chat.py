"""Streaming chat functionality for real-time LLM responses"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncGenerator, Dict, List, Optional

try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    openai = None
    AsyncOpenAI = None

try:
    import anthropic
    from anthropic import AsyncAnthropic
except ImportError:
    anthropic = None
    AsyncAnthropic = None

try:
    from ..utils.logger import get_logger
    from .llm_chatbot import Message, RepairChatbot, RepairContext
except ImportError:
    # Fallback for direct execution
    import os
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from chat.llm_chatbot import Message, RepairChatbot, RepairContext
    from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class StreamingResponse:
    """Represents a streaming response chunk"""

    content: str
    is_complete: bool = False
    token_count: Optional[int] = None
    metadata: Optional[Dict] = None


class StreamingRepairChatbot(RepairChatbot):
    """Enhanced chatbot with streaming response capabilities"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.async_openai_client = None
        self.async_anthropic_client = None

        # Initialize async clients
        self._init_async_clients()

    def _init_async_clients(self):
        """Initialize async API clients"""
        if AsyncOpenAI and self.openai_client:
            try:
                self.async_openai_client = AsyncOpenAI(
                    api_key=self.openai_client.api_key
                )
                logger.info("Async OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize async OpenAI client: {e}")

        if AsyncAnthropic and self.anthropic_client:
            try:
                self.async_anthropic_client = AsyncAnthropic(
                    api_key=self.anthropic_client.api_key
                )
                logger.info("Async Anthropic client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize async Anthropic client: {e}")

    async def stream_chat(
        self, user_message: str, include_context: bool = True
    ) -> AsyncGenerator[StreamingResponse, None]:
        """Generate streaming response for user message"""
        datetime.now()

        # Add user message to history
        self.add_message("user", user_message)

        try:
            if self.active_client == "openai" and self.async_openai_client:
                async for chunk in self._stream_with_openai(
                    user_message, include_context
                ):
                    yield chunk
            elif self.active_client == "anthropic" and self.async_anthropic_client:
                async for chunk in self._stream_with_anthropic(
                    user_message, include_context
                ):
                    yield chunk
            else:
                # Fallback to non-streaming response
                response = await asyncio.to_thread(
                    self.chat, user_message, include_context
                )
                yield StreamingResponse(content=response, is_complete=True)

        except Exception as e:
            logger.error(f"Streaming chat error: {e}")
            fallback_response = self._enhanced_fallback_response(user_message)
            yield StreamingResponse(content=fallback_response, is_complete=True)

    async def _stream_with_openai(
        self, user_message: str, include_context: bool
    ) -> AsyncGenerator[StreamingResponse, None]:
        """Stream response using OpenAI API"""
        if not self.async_openai_client:
            raise Exception("Async OpenAI client not available")

        messages = self._build_messages(user_message, include_context)
        full_response = ""

        try:
            stream = await self.async_openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=800,
                temperature=0.7,
                stream=True,
                presence_penalty=0.1,
                frequency_penalty=0.1,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content

                    yield StreamingResponse(
                        content=content,
                        is_complete=False,
                        metadata={"model": "gpt-4", "provider": "openai"},
                    )

            # Final chunk indicating completion
            yield StreamingResponse(
                content="",
                is_complete=True,
                metadata={
                    "model": "gpt-4",
                    "provider": "openai",
                    "total_tokens": len(full_response.split()),
                    "full_response": full_response,
                },
            )

            # Add complete response to conversation history
            self.add_message("assistant", full_response)

        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise

    async def _stream_with_anthropic(
        self, user_message: str, include_context: bool
    ) -> AsyncGenerator[StreamingResponse, None]:
        """Stream response using Anthropic API"""
        if not self.async_anthropic_client:
            raise Exception("Async Anthropic client not available")

        system_prompt = self._build_system_prompt(include_context)
        conversation = self._build_conversation_for_anthropic()
        full_response = ""

        try:
            async with self.async_anthropic_client.messages.stream(
                model="claude-3-sonnet-20240229",
                max_tokens=800,
                temperature=0.7,
                system=system_prompt,
                messages=conversation + [{"role": "user", "content": user_message}],
            ) as stream:
                async for chunk in stream:
                    if chunk.type == "content_block_delta":
                        content = chunk.delta.text
                        full_response += content

                        yield StreamingResponse(
                            content=content,
                            is_complete=False,
                            metadata={
                                "model": "claude-3-sonnet",
                                "provider": "anthropic",
                            },
                        )

            # Final chunk indicating completion
            yield StreamingResponse(
                content="",
                is_complete=True,
                metadata={
                    "model": "claude-3-sonnet",
                    "provider": "anthropic",
                    "total_tokens": len(full_response.split()),
                    "full_response": full_response,
                },
            )

            # Add complete response to conversation history
            self.add_message("assistant", full_response)

        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise


class TokenUsageTracker:
    """Track token usage across API calls"""

    def __init__(self):
        self.usage_log: List[Dict] = []
        self.daily_limits = {
            "openai": 10000,  # tokens per day
            "anthropic": 10000,
        }
        self.current_usage = {
            "openai": 0,
            "anthropic": 0,
        }

    def log_usage(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: Optional[float] = None,
    ):
        """Log token usage for a request"""
        total_tokens = input_tokens + output_tokens

        usage_entry = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost": cost
            or self._estimate_cost(provider, model, total_tokens),
        }

        self.usage_log.append(usage_entry)
        self.current_usage[provider] += total_tokens

        logger.info(f"Token usage logged: {provider}/{model} - {total_tokens} tokens")

    def _estimate_cost(self, provider: str, model: str, tokens: int) -> float:
        """Estimate cost based on provider pricing"""
        # Approximate pricing (update with current rates)
        pricing = {
            "openai": {"gpt-4": 0.00003, "gpt-3.5-turbo": 0.000002},  # per token
            "anthropic": {"claude-3-sonnet": 0.000015, "claude-3-haiku": 0.00000025},
        }

        rate = pricing.get(provider, {}).get(model, 0.00001)
        return tokens * rate

    def check_limits(self, provider: str) -> bool:
        """Check if daily limits are exceeded"""
        return self.current_usage.get(provider, 0) < self.daily_limits.get(
            provider, float("inf")
        )

    def get_usage_summary(self) -> Dict:
        """Get usage summary"""
        today = datetime.now().date()
        today_usage = [
            entry
            for entry in self.usage_log
            if datetime.fromisoformat(entry["timestamp"]).date() == today
        ]

        total_cost = sum(entry["estimated_cost"] for entry in today_usage)
        total_tokens = sum(entry["total_tokens"] for entry in today_usage)

        return {
            "date": today.isoformat(),
            "total_requests": len(today_usage),
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "by_provider": self._group_by_provider(today_usage),
        }

    def _group_by_provider(self, usage_entries: List[Dict]) -> Dict:
        """Group usage by provider"""
        grouped = {}
        for entry in usage_entries:
            provider = entry["provider"]
            if provider not in grouped:
                grouped[provider] = {"requests": 0, "tokens": 0, "cost": 0.0}

            grouped[provider]["requests"] += 1
            grouped[provider]["tokens"] += entry["total_tokens"]
            grouped[provider]["cost"] += entry["estimated_cost"]

        return grouped


class ConversationManager:
    """Manage conversation state and history"""

    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.conversations: Dict[str, List[Message]] = {}
        self.contexts: Dict[str, RepairContext] = {}

    def create_session(
        self, session_id: str, initial_context: Optional[RepairContext] = None
    ) -> str:
        """Create a new conversation session"""
        self.conversations[session_id] = []
        self.contexts[session_id] = initial_context or RepairContext()
        logger.info(f"Created conversation session: {session_id}")
        return session_id

    def add_message(self, session_id: str, message: Message):
        """Add message to session history"""
        if session_id not in self.conversations:
            self.create_session(session_id)

        self.conversations[session_id].append(message)

        # Trim history if it exceeds max_history
        if len(self.conversations[session_id]) > self.max_history:
            self.conversations[session_id] = self.conversations[session_id][
                -self.max_history :
            ]

    def get_history(self, session_id: str) -> List[Message]:
        """Get conversation history for session"""
        return self.conversations.get(session_id, [])

    def update_context(self, session_id: str, **kwargs):
        """Update repair context for session"""
        if session_id not in self.contexts:
            self.contexts[session_id] = RepairContext()

        for key, value in kwargs.items():
            if hasattr(self.contexts[session_id], key):
                setattr(self.contexts[session_id], key, value)

    def get_context(self, session_id: str) -> RepairContext:
        """Get repair context for session"""
        return self.contexts.get(session_id, RepairContext())

    def clear_session(self, session_id: str):
        """Clear session data"""
        self.conversations.pop(session_id, None)
        self.contexts.pop(session_id, None)
        logger.info(f"Cleared conversation session: {session_id}")

    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.conversations.keys())


# Global instances
token_tracker = TokenUsageTracker()
conversation_manager = ConversationManager()


def get_token_tracker() -> TokenUsageTracker:
    """Get global token usage tracker"""
    return token_tracker


def get_conversation_manager() -> ConversationManager:
    """Get global conversation manager"""
    return conversation_manager
