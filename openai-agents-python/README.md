# OpenAI Agents SDK + MAQAMI Travel MCP

A terminal travel assistant built with the OpenAI Agents SDK. It connects to the MAQAMI Travel MCP server at `https://mcp.maqami.co/` with `MCPServerStreamableHttp`.

## How it works

- `MCPServerStreamableHttp(params={"url": "https://mcp.maqami.co/"})` connects to the remote server. No API key is needed for MAQAMI.
- `require_approval=needs_approval` marks every tool that the server does not flag as read-only as needing approval.
- When the agent wants to prebook or book, `Runner.run` returns `interruptions`. The script asks you to approve or reject each one, then resumes the run from `result.to_state()`.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=...
python travel_agent.py "Find 4-star hotels in Lisbon for 2 adults, 12 to 15 May"
```

Try follow-ups such as "Show the amenities of the second hotel" or "Search flights from Dubai to London on 10 December for one adult".

Booking creates a real reservation and needs guest and payment details. Only approve a prebook or book call when you mean it.

## Options

- `OPENAI_MODEL` sets the model (default `gpt-5.4-mini`).
- `MAQAMI_MCP_URL` overrides the endpoint, for example to test against a local mock server.
