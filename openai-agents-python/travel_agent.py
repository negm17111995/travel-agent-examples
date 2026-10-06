"""Travel assistant built with the OpenAI Agents SDK and the MAQAMI Travel MCP server.

The agent connects to the remote MCP server over Streamable HTTP. Read-only tools
(search, details, lookups) run freely. Any tool the server does not mark as
read-only, such as prebook or cancel, pauses the run and asks you to approve it
in the terminal first.

Run:
    pip install -r requirements.txt
    export OPENAI_API_KEY=...
    python travel_agent.py "Find 4-star hotels in Lisbon for 2 adults, 12 to 15 May"
"""

from __future__ import annotations

import asyncio
import os
import sys
from typing import Any

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

# The public MAQAMI Travel MCP endpoint (Streamable HTTP, no API key).
MAQAMI_MCP_URL = os.environ.get("MAQAMI_MCP_URL", "https://mcp.maqami.co/")
MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.4-mini")

INSTRUCTIONS = """\
You are a travel assistant. Use the MAQAMI Travel tools to search hotels and
flights, look up cities, airports and hotel details, and answer with concrete
options (name, dates, price, currency, cancellation terms when available).
Customers book and pay only on book.maqami.co. After the user has chosen an
option and confirmed the final price, call post_rates_prebook (hotels) or
post_flights_verify (flights) and give them the checkoutUrl it returns. Never
ask for card or passport details in the chat.
"""


def needs_approval(_ctx: Any, _agent: Any, tool: Any) -> bool:
    """Ask a human before any tool that the server does not mark as read-only."""
    annotations = getattr(tool, "annotations", None)
    # The attribute is `read_only_hint` in mcp 2.x and `readOnlyHint` in mcp 1.x.
    read_only = getattr(annotations, "read_only_hint", getattr(annotations, "readOnlyHint", None))
    return read_only is not True


def ask(question: str) -> bool:
    return input(f"{question} [y/N] ").strip().lower() in {"y", "yes"}


async def main(prompt: str) -> None:
    async with MCPServerStreamableHttp(
        name="MAQAMI Travel",
        params={"url": MAQAMI_MCP_URL, "timeout": 60},
        client_session_timeout_seconds=60,
        cache_tools_list=True,
        require_approval=needs_approval,
    ) as maqami:
        agent = Agent(
            name="Travel assistant",
            instructions=INSTRUCTIONS,
            model=MODEL,
            mcp_servers=[maqami],
        )

        result = await Runner.run(agent, prompt)
        # Human-in-the-loop: approve or reject each paused tool call, then resume.
        while result.interruptions:
            state = result.to_state()
            for item in result.interruptions:
                if ask(f"Allow {item.name} with arguments {item.arguments}?"):
                    state.approve(item)
                else:
                    state.reject(item)
            result = await Runner.run(agent, state)

        print(result.final_output)


if __name__ == "__main__":
    user_prompt = " ".join(sys.argv[1:]) or "Find 4-star hotels in Lisbon for 2 adults, 12 to 15 May."
    asyncio.run(main(user_prompt))
