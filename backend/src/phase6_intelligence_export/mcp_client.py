import os
import json
import asyncio
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

async def run_mcp_export(content: str):
    """
    Directly uses the @a-bonus/google-docs-mcp server to append intelligence to GDocs.
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    doc_id = os.getenv("GOOGLE_DOC_ID")

    if not client_id or not client_secret or not doc_id:
        logger.error("Missing Google Credentials or Doc ID in .env")
        return False

    # Parameters for the @a-bonus MCP server
    # We run it via npx with the necessary env vars
    server_params = StdioServerParameters(
        command="npx",
        args=["--silent", "-y", "@a-bonus/google-docs-mcp"],
        env={
            **os.environ,
            "GOOGLE_CLIENT_ID": client_id,
            "GOOGLE_CLIENT_SECRET": client_secret,
            "PATH": os.environ.get("PATH", "") # Ensure npx is in path
        }
    )

    logger.info("Connecting to @a-bonus/google-docs-mcp server...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List available tools to find the append tool
                tools = await session.list_tools()
                logger.info(f"Available tools: {[t.name for t in tools.tools]}")
                
                # Check for appendMarkdown or appendText
                # The tool list showed 'appendMarkdown'
                tool_name = "appendMarkdown"
                
                # Format the arguments
                args = {
                    "documentId": doc_id,
                    "markdown": content
                }
                
                logger.info(f"Calling tool {tool_name} for Doc ID: {doc_id}...")
                result = await session.call_tool(tool_name, args)
                
                if result.isError:
                    logger.error(f"MCP Tool Error: {result.content}")
                    return False
                
                logger.info("Successfully exported to Google Doc via MCP!")
                return True

    except Exception as e:
        logger.error(f"MCP Connection failed: {e}")
        # Hint for the user if it's an auth issue
        if "npx" in str(e):
            logger.error("Ensure Node.js/npm is installed and 'npx' is in your PATH.")
        return False

def export_to_gdoc_mcp(content: str):
    """Sync wrapper for the async MCP call."""
    return asyncio.run(run_mcp_export(content))

if __name__ == "__main__":
    # Test content
    test_content = "\n\n### 🧪 MCP Test Update\nSuccessfully appended using @a-bonus/google-docs-mcp server via Python MCP SDK."
    export_to_gdoc_mcp(test_content)
