import json
from typing import Any, Callable, Dict

from ..service import get_users, get_weather
from .llm import get_react_step


TOOLS: Dict[str, Callable[..., Any]] = {
    "get_users": get_users,
    "get_weather": get_weather,
}


def _execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> Any:
    if tool_name not in TOOLS:
        raise ValueError(f"Unknown tool name: {tool_name}")

    tool_fn = TOOLS[tool_name]
    try:
        return tool_fn(**tool_input)
    except TypeError as exc:
        raise ValueError(f"Invalid input for tool '{tool_name}': {str(exc)}") from exc


def agent_loop(user_message: str, max_iterations: int = 5) -> str:
    messages = [
        {"role": "user", "content": user_message},
    ]

    for _ in range(max_iterations):
        try:
            decision = get_react_step(messages)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM returned invalid JSON.") from exc

        decision_type = decision.get("type")

        if decision_type == "tool":
            tool_name = decision.get("name")
            tool_input = decision.get("input", {})

            if not isinstance(tool_name, str):
                raise ValueError("Tool decision missing valid 'name'.")
            if not isinstance(tool_input, dict):
                raise ValueError("Tool decision missing valid 'input'.")

            tool_result = _execute_tool(tool_name=tool_name, tool_input=tool_input)

            # Feed back the action and observation so the model can continue reasoning.
            messages.append({"role": "assistant", "content": json.dumps(decision, ensure_ascii=True)})
            messages.append(
                {
                    "role": "tool",
                    "content": json.dumps(
                        {"name": tool_name, "output": tool_result},
                        ensure_ascii=True,
                    ),
                }
            )
            continue

        if decision_type == "final":
            content = decision.get("content")
            if not isinstance(content, str):
                raise ValueError("Final decision missing valid 'content'.")
            return content

        raise ValueError("LLM returned unsupported decision type.")

    raise RuntimeError(f"Agent loop exceeded max iterations ({max_iterations}).")
