# LangChain / LangGraph + MAQAMI Travel MCP

A terminal travel assistant built with LangChain's `create_agent` (which runs on LangGraph). It loads tools from the MAQAMI Travel MCP server at `https://mcp.maqami.co/` with LangChain's built-in MCP adapter, `langchain.mcp.MCPAdapter`.

`langchain.mcp` replaced the standalone `langchain-mcp-adapters` package and needs `langchain[mcp]>=1.4`. It is marked beta, so importing it prints a `LangChainBetaWarning`.

## How it works

- `MCPAdapter("https://mcp.maqami.co/")` infers Streamable HTTP from the URL, and `list_tools()` returns LangChain tools. No API key is needed for MAQAMI.
- Each tool keeps the server's annotations under `tool.metadata["mcp"]`. Tools that are not marked read-only go into `HumanInTheLoopMiddleware(interrupt_on=...)`.
- When the agent wants to prebook or book, the graph pauses with `__interrupt__`. The script asks you to approve or reject, then resumes the same thread with `Command(resume={"decisions": [...]})`. An `InMemorySaver` checkpointer keeps the paused state.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=...
python travel_agent.py "Search flights from Dubai to London on 10 December for one adult"
```

Booking creates a real reservation and needs guest and payment details. Only approve a prebook or book call when you mean it.

## Options

- `LANGCHAIN_MODEL` sets the model in `provider:model` form (default `openai:gpt-5.4-mini`). Install the matching integration package for other providers.
- `MAQAMI_MCP_URL` overrides the endpoint, for example to test against a local mock server.
