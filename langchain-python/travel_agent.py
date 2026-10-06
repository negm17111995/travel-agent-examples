"""Travel assistant built with LangChain (create_agent on LangGraph) and the MAQAMI Travel MCP server.

It uses LangChain's built-in MCP support (`langchain.mcp`, which replaced the
standalone langchain-mcp-adapters package). Read-only tools run freely. Tools the
server does not mark as read-only, such as prebook or cancel, are interrupted by
HumanInTheLoopMiddleware so you can approve or reject them in the terminal.

Run:
    pip install -r requirements.txt
    export OPENAI_API_KEY=...
    python travel_agent.py "Search flights from Dubai to London on 10 December for one adult"
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.mcp import MCPAdapter
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

# The public MAQAMI Travel MCP endpoint (Streamable HTTP, no API key).
MAQAMI_MCP_URL = os.environ.get("MAQAMI_MCP_URL", "https://mcp.maqami.co/")
MODEL = os.environ.get("LANGCHAIN_MODEL", "openai:gpt-5.4-mini")

SYSTEM_PROMPT = """\
You are a travel assistant. Use the MAQAMI Travel tools to search hotels and
flights, look up cities, airports and hotel details, and answer with concrete
options (name, dates, price, currency, cancellation terms when available).
Customers book and pay only on book.maqami.co. After the user has chosen an
option and confirmed the final price, call post_rates_prebook (hotels) or
post_flights_verify (flights) and give them the checkoutUrl it returns. Never
ask for card or passport details in the chat.
"""


def is_read_only(tool: Any) -> bool:
    """True when the MCP server marked the tool with readOnlyHint."""
    annotations = ((tool.metadata or {}).get("mcp") or {}).get("tool", {}).get("annotations", {})
    return annotations.get("read_only_hint") is True or annotations.get("readOnlyHint") is True


def ask(question: str) -> bool:
    return input(f"{question} [y/N] ").strip().lower() in {"y", "yes"}


async def main(prompt: str) -> None:
    async with MCPAdapter(MAQAMI_MCP_URL) as adapter:
        tools = await adapter.list_tools()
        guarded = {t.name: True for t in tools if not is_read_only(t)}

        agent = create_agent(
            MODEL,
            tools,
            system_prompt=SYSTEM_PROMPT,
            middleware=[HumanInTheLoopMiddleware(interrupt_on=guarded)],
            checkpointer=InMemorySaver(),  # needed to pause and resume on interrupts
        )
        config = {"configurable": {"thread_id": str(uuid.uuid4())}}

        result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]}, config)
        # Human-in-the-loop: answer each interrupt, then resume the same thread.
        while result.get("__interrupt__"):
            request = result["__interrupt__"][0].value
            decisions = []
            for action in request["action_requests"]:
                if ask(f"Allow {action['name']} with arguments {action['args']}?"):
                    decisions.append({"type": "approve"})
                else:
                    decisions.append({"type": "reject", "message": "The user declined this action."})
            result = await agent.ainvoke(Command(resume={"decisions": decisions}), config)

        print(result["messages"][-1].content)


if __name__ == "__main__":
    user_prompt = " ".join(sys.argv[1:]) or "Find 4-star hotels in Lisbon for 2 adults, 12 to 15 May."
    asyncio.run(main(user_prompt))
