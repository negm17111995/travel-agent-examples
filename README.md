# Travel agent examples for the MAQAMI Travel MCP server

Small, runnable examples that connect popular agent frameworks to the [MAQAMI Travel MCP server](https://github.com/negm17111995/mcp-server), the official remote MCP server for [MAQAMI](https://maqami.co), a hotel and flight booking platform with 3M+ hotels.

The server is hosted at `https://mcp.maqami.co/` (Streamable HTTP, no API key). Each example builds a terminal travel assistant that can search hotels and flights, look up places, airports and hotel details, and then prebook and book after you approve.

| Example | Language | Framework |
| --- | --- | --- |
| [`openai-agents-python/`](openai-agents-python/) | Python | OpenAI Agents SDK (`MCPServerStreamableHttp`) |
| [`langchain-python/`](langchain-python/) | Python | LangChain `create_agent` on LangGraph, with the built-in `langchain.mcp` adapter |
| [`vercel-ai-sdk/`](vercel-ai-sdk/) | TypeScript | Vercel AI SDK (`@ai-sdk/mcp` and `generateText`) |

## Booking safety

Prebooking and booking create real reservations and need guest and payment details. Every example therefore uses the same rule:

- Tools that the server marks as read-only (`readOnlyHint: true`) run without asking.
- Every other tool pauses the agent and asks you to approve or reject the call in the terminal, showing the tool name and arguments.

Each framework does this with its own human-in-the-loop feature, so the pattern carries over to a web app or chat UI.

## Quick start

Pick a folder and follow its README. In short:

```bash
# Python examples
cd openai-agents-python        # or langchain-python
pip install -r requirements.txt
export OPENAI_API_KEY=...
python travel_agent.py "Find 4-star hotels in Lisbon for 2 adults, 12 to 15 May"

# TypeScript example
cd vercel-ai-sdk
npm install
export OPENAI_API_KEY=...
npm start -- "Search flights from Dubai to London on 10 December for one adult"
```

The examples use OpenAI models by default. Each framework supports other providers, so swap the model line if you prefer another one.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `MAQAMI_MCP_URL` | `https://mcp.maqami.co/` | MCP endpoint. Override it to point at a local mock server while developing. |
| `OPENAI_MODEL` / `LANGCHAIN_MODEL` | `gpt-5.4-mini` / `openai:gpt-5.4-mini` | Model used by the agent. |

## Checks

The examples are checked statically before each change, without connecting to the MAQAMI endpoint:

```bash
ruff check . && ruff format --check .
python -m py_compile openai-agents-python/travel_agent.py langchain-python/travel_agent.py
(cd vercel-ai-sdk && npm ci && npm run typecheck)
```

## Other clients

To connect Claude, ChatGPT, Cursor, VS Code, Codex, Gemini CLI and other MCP clients without code, see the setup guide in the [server repository](https://github.com/negm17111995/mcp-server).

## License

[MIT](LICENSE)
