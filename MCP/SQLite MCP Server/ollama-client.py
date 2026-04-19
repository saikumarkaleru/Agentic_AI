
# ============================================================
# MCP-Powered Local Agent Demo
# Tech Stack:
# - FastMCP (MCP Server)
# - SQLite (Database)
# - LlamaIndex (Agent Host)
# - Ollama + DeepSeek-R1 (LLM)
# ============================================================
# CLIENT SIDE (LlamaIndex Agent + MCP Client)

import asyncio

from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import (
    FunctionAgent,
    ToolCallResult,
    ToolCall,
)

from llama_index.core.workflow import Context


# ------------------------------
# STEP 1: Configure Local LLM
# ------------------------------

llm = Ollama(
    model="llama3.2",
    request_timeout=120.0,
)

Settings.llm = llm

# ------------------------------
# STEP 2: System Prompt
# ------------------------------

SYSTEM_PROMPT = """
You are an AI assistant for database operations.
Always use tools before answering.
Never guess database contents.
Use the available tools to read or write data.
"""

# ------------------------------
# STEP 3: Build Agent
# ------------------------------

async def get_agent(tool_spec: McpToolSpec):
    tools = await tool_spec.to_tool_list_async()

    agent = FunctionAgent(
        name="DBAgent",
        description="Agent that interacts with SQLite via MCP tools.",
        tools=tools,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent

async def handle_user_message(
    message_content: str,
    agent: FunctionAgent,
    agent_context: Context,
    verbose: bool = False,
):
    handler = agent.run(
        message_content,
        ctx=agent_context
    )

    async for event in handler.stream_events():
        if verbose and type(event) == ToolCall:
            print(f"Calling tool {event.tool_name}")

        elif verbose and type(event) == ToolCallResult:
            print(
                f"{event.tool_name} returned "
                f"{event.tool_output}"
            )

    response = await handler
    return str(response)

# ------------------------------
# STEP 5: Main Runtime
# ------------------------------

async def main():
    # Example endpoint if server runs via SSE
    client = BasicMCPClient("http://127.0.0.1:8000/sse")

    tool_spec = McpToolSpec(client=client)

    agent = await get_agent(tool_spec)
    context = Context(agent)

    print("\nMCP Agent Ready")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        result = await handle_user_message(
            user_input,
            agent,
            context,
        )

        print("Agent:", result)


# Example usage:
# User: Add Rafael Nadal, age 39, profession Tennis Player
# User: Show all records
# Agent will decide which MCP tool to call.

if __name__ == "__main__":
    asyncio.run(main())
