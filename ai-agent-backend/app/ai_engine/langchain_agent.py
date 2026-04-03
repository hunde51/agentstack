import os
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
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
                "You are a backend agent. Use tools when needed to answer accurately. "
                "Call exactly the most relevant tool when required, and then provide a concise final answer.",
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
    )


def run_agent(user_message: str) -> str:
    executor = _get_executor()
    result = executor.invoke({"input": user_message})

    output = result.get("output", "")
    return output if isinstance(output, str) else str(output)
