import json
import os
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from ..service import get_users, get_weather

load_dotenv()


@tool("get_users")
def get_users_tool() -> list[dict[str, Any]]:
    """Return all users in the system."""
    return get_users()


@tool("get_weather")
def get_weather_tool(city: str) -> dict[str, Any]:
    """Get weather for a city. Input must be a city name."""
    return get_weather(city=city)


TOOLS = [get_users_tool, get_weather_tool]


def _build_llm():
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            temperature=0,
        )

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
    )


def _build_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful backend assistant. "
                "Answer directly using your general knowledge when possible. "
                "Use tools only when they are needed for live/system data (for example users or weather). "
                "If a tool is not needed, do not call one. "
                "Never claim you lack information about common general topics when you can answer directly.",
            ),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )


@lru_cache(maxsize=1)
def _get_executor() -> AgentExecutor:
    llm = _build_llm()
    prompt = _build_prompt()

    agent = create_tool_calling_agent(
        llm=llm,
        tools=TOOLS,
        prompt=prompt,
    )

    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=False,
        max_iterations=5,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )


def _format_context(*, memory_context: str, chat_context: str, user_message: str) -> str:
    parts: list[str] = []
    if memory_context.strip():
        parts.append(f"Long-term memory (JSON):\n{memory_context.strip()}")
    if chat_context.strip():
        parts.append(f"Recent conversation:\n{chat_context.strip()}")
    parts.append(f"Current user message:\n{user_message.strip()}")
    return "\n\n".join(parts)


def _parse_last_tool(steps: list) -> tuple[str | None, Any]:
    if not steps:
        return None, None
    tool_used: str | None = None
    tool_result: Any = None
    for action, observation in steps:
        tool_used = getattr(action, "tool", None)
        if isinstance(tool_used, str):
            pass
        else:
            tool_used = str(tool_used) if tool_used is not None else None
        tool_result = observation
        if isinstance(observation, str):
            try:
                tool_result = json.loads(observation)
            except (json.JSONDecodeError, TypeError):
                tool_result = observation
    return tool_used, tool_result


def _normalize_output_text(output: Any) -> str:
    # Gemini/LangChain can return structured content blocks; extract readable text.
    if isinstance(output, str):
        return output

    if isinstance(output, list):
        text_parts: list[str] = []
        for item in output:
            if isinstance(item, str):
                text_parts.append(item)
                continue
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    text_parts.append(text)
        if text_parts:
            return "\n".join(part.strip() for part in text_parts if part.strip())

    if isinstance(output, dict):
        text = output.get("text")
        if isinstance(text, str):
            return text

    return str(output)


def run_agent(
    user_message: str,
    *,
    chat_context: str = "",
    memory_context: str = "",
) -> dict[str, Any]:
    full_input = _format_context(
        memory_context=memory_context,
        chat_context=chat_context,
        user_message=user_message,
    )
    executor = _get_executor()
    result = executor.invoke({"input": full_input})

    output = result.get("output", "")
    output_str = _normalize_output_text(output)

    steps = result.get("intermediate_steps") or []
    tool_used, tool_result = _parse_last_tool(steps)

    return {
        "output": output_str,
        "tool_used": tool_used,
        "tool_result": tool_result,
    }
