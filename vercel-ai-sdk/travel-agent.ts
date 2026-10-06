/**
 * Travel assistant built with the Vercel AI SDK and the MAQAMI Travel MCP server.
 *
 * The MCP client connects to the remote server over Streamable HTTP. Read-only tools
 * (search, details, lookups) run freely. Any tool the server does not mark as
 * read-only, such as prebook or cancel, needs your approval in the terminal first.
 *
 * Run:
 *   npm install
 *   export OPENAI_API_KEY=...
 *   npm start -- "Find 4-star hotels in Lisbon for 2 adults, 12 to 15 May"
 */
import { createInterface } from 'node:readline/promises';
import { stdin, stdout } from 'node:process';

import { createMCPClient } from '@ai-sdk/mcp';
import { openai } from '@ai-sdk/openai';
import { generateText, stepCountIs, type ModelMessage, type ToolApprovalResponse } from 'ai';

// The public MAQAMI Travel MCP endpoint (Streamable HTTP, no API key).
const MAQAMI_MCP_URL = process.env.MAQAMI_MCP_URL ?? 'https://mcp.maqami.co/';
const MODEL = process.env.OPENAI_MODEL ?? 'gpt-5.4-mini';

const SYSTEM = `You are a travel assistant. Use the MAQAMI Travel tools to search hotels and
flights, look up cities, airports and hotel details, and answer with concrete
options (name, dates, price, currency, cancellation terms when available).
Customers book and pay only on book.maqami.co. After the user has chosen an
option and confirmed the final price, call post_rates_prebook (hotels) or
post_flights_verify (flights) and give them the checkoutUrl it returns. Never
ask for card or passport details in the chat.`;

async function main(prompt: string): Promise<void> {
  const client = await createMCPClient({
    transport: { type: 'http', url: MAQAMI_MCP_URL },
  });
  const rl = createInterface({ input: stdin, output: stdout });

  try {
    const definitions = await client.listTools();
    const readOnly = new Set(
      definitions.tools.filter((t) => t.annotations?.readOnlyHint === true).map((t) => t.name),
    );
    const tools = client.toolsFromDefinitions(definitions);

    const messages: ModelMessage[] = [{ role: 'user', content: prompt }];

    for (;;) {
      const result = await generateText({
        model: openai(MODEL),
        system: SYSTEM,
        tools,
        messages,
        stopWhen: stepCountIs(10),
        // Ask a human before any tool that is not marked read-only.
        toolApproval: ({ toolCall }) =>
          readOnly.has(toolCall.toolName) ? 'not-applicable' : 'user-approval',
      });
      messages.push(...result.response.messages);

      const requests = result.content.filter((part) => part.type === 'tool-approval-request');
      if (requests.length === 0) {
        console.log(result.text);
        break;
      }

      const responses: ToolApprovalResponse[] = [];
      for (const request of requests) {
        const answer = await rl.question(
          `Allow ${request.toolCall.toolName} with arguments ${JSON.stringify(request.toolCall.input)}? [y/N] `,
        );
        responses.push({
          type: 'tool-approval-response',
          approvalId: request.approvalId,
          approved: ['y', 'yes'].includes(answer.trim().toLowerCase()),
        });
      }
      messages.push({ role: 'tool', content: responses });
    }
  } finally {
    rl.close();
    await client.close();
  }
}

const userPrompt =
  process.argv.slice(2).join(' ') || 'Find 4-star hotels in Lisbon for 2 adults, 12 to 15 May.';

main(userPrompt).catch((error: unknown) => {
  console.error(error);
  process.exitCode = 1;
});
