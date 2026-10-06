# Vercel AI SDK + MAQAMI Travel MCP

A terminal travel assistant built with the Vercel AI SDK. It connects to the MAQAMI Travel MCP server at `https://mcp.maqami.co/` with `createMCPClient` from `@ai-sdk/mcp`.

## How it works

- `createMCPClient({ transport: { type: 'http', url: 'https://mcp.maqami.co/' } })` connects over Streamable HTTP. No API key is needed for MAQAMI.
- `client.listTools()` returns the tool definitions with their annotations, and `client.toolsFromDefinitions()` turns them into AI SDK tools.
- `generateText({ toolApproval })` returns `'user-approval'` for any tool that is not marked read-only. When the model wants to prebook or cancel, the result contains `tool-approval-request` parts. The script asks you, appends `tool-approval-response` parts to the conversation, and calls `generateText` again.

## Run

Node.js 20 or later.

```bash
npm install
export OPENAI_API_KEY=...
npm start -- "Find 4-star hotels in Lisbon for 2 adults, 12 to 15 May"
```

Prebook holds a real rate, and the customer pays only on book.maqami.co through the `checkoutUrl` it returns. Only approve a call that is not read-only when you mean it.

## Options

- `OPENAI_MODEL` sets the model (default `gpt-5.4-mini`).
- `MAQAMI_MCP_URL` overrides the endpoint, for example to test against a local mock server.
- `npm run typecheck` runs `tsc --noEmit`.

In a Next.js app, the same `toolApproval` setting works with `streamText`, and the approval requests show up as tool parts in `useChat`.
