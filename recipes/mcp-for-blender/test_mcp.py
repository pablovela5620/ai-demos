"""Exercise the installed server through its public MCP transport."""

import asyncio
import os
from importlib.resources import files

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    """Check bundled data, tool discovery, and a disconnected Blender response."""
    assert files("blender_mcp").joinpath("bundled/addon.py").is_file()
    parameters: StdioServerParameters = StdioServerParameters(
        command="mcp-for-blender",
        env={**os.environ, "DISABLE_TELEMETRY": "true", "BLENDER_HOST": "127.0.0.1", "BLENDER_PORT": "1"},
    )
    async with asyncio.timeout(45):
        async with stdio_client(parameters) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                names: set[str] = {tool.name for tool in (await session.list_tools()).tools}
                assert {"get_scene_info", "execute_blender_code", "get_viewport_screenshot"} <= names
                result = await session.call_tool("get_scene_info", {"user_prompt": "Package connectivity test"})
                assert "connect" in str(result).lower(), result


if __name__ == "__main__":
    asyncio.run(main())
