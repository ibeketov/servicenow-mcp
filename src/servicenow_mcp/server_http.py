"""
ServiceNow MCP Server (HTTP)

This module provides the main implementation of the ServiceNow MCP server
using Streamable HTTP transport.
"""

import argparse
<<<<<<< HEAD
import contextlib

# It's good practice to have a logger if we're managing lifecycles
import logging
import os
from collections.abc import AsyncIterator
=======
import os
>>>>>>> bf5e7fc (Implement ServiceNow MCP Server using Streamable HTTP with Starlette and Uvicorn)
from typing import Dict, Union

import uvicorn
from dotenv import load_dotenv
from mcp.server import Server
<<<<<<< HEAD
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette

# Request is not directly used in create_starlette_app anymore for handler
from starlette.routing import Mount  # Changed from Route
from starlette.types import Receive, Scope, Send

from servicenow_mcp.event_store import InMemoryEventStore  # Corrected import path
from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig

logger = logging.getLogger(__name__)


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application for the mcp server with StreamableHTTPSessionManager."""
    
    # Create event store for resumability (as shown in the example)
    # For production, a persistent storage solution would be needed.
    event_store = InMemoryEventStore()

    # Create the session manager with the mcp_server (app) and event store
    session_manager = StreamableHTTPSessionManager(
        app=mcp_server, 
        event_store=event_store, 
        json_response=False # Defaulting to SSE as per MCP norms
    )

    # ASGI handler for streamable HTTP connections
    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for managing session manager lifecycle."""
        async with session_manager.run():
            logger.info("Application started with StreamableHTTPSessionManager!")
            try:
                yield
            finally:
                logger.info("Application shutting down StreamableHTTPSessionManager...")
=======

# from mcp.server.fastmcp import FastMCP
from mcp.server.streamable_http import StreamableHttpTransport  # Updated import
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route  # Mount is no longer needed

from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application for the mcp server with Streamable HTTP."""
    http_transport = StreamableHttpTransport()

    async def handle_http(request: Request) -> None:
        """Handles incoming HTTP requests and forwards them to the MCP server."""
        await http_transport.handle_request(
            request.scope,
            request.receive,
            request._send,  # noqa: SLF001
            mcp_server,
            mcp_server.create_initialization_options(),
        )
>>>>>>> bf5e7fc (Implement ServiceNow MCP Server using Streamable HTTP with Starlette and Uvicorn)

    return Starlette(
        debug=debug,
        routes=[
<<<<<<< HEAD
            Mount("/mcp", app=handle_streamable_http), # Route from example
        ],
        lifespan=lifespan,
=======
            Route("/", endpoint=handle_http),  # Typically MCP over HTTP uses the root path
        ],
>>>>>>> bf5e7fc (Implement ServiceNow MCP Server using Streamable HTTP with Starlette and Uvicorn)
    )


class ServiceNowHttpMCP(ServiceNowMCP):
    """
    ServiceNow MCP Server implementation using Streamable HTTP.

    This class provides a Model Context Protocol (MCP) server for ServiceNow,
    allowing LLMs to interact with ServiceNow data and functionality via HTTP.
    """

    def __init__(self, config: Union[Dict, ServerConfig]):
        """
        Initialize the ServiceNow MCP server.

        Args:
            config: Server configuration, either as a dictionary or ServerConfig object.
        """
        super().__init__(config)
<<<<<<< HEAD
        # Basic logging configuration for the module
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def start(self, host: str = "127.0.0.1", port: int = 8080):
=======

    def start(self, host: str = "0.0.0.0", port: int = 8080):
>>>>>>> bf5e7fc (Implement ServiceNow MCP Server using Streamable HTTP with Starlette and Uvicorn)
        """
        Start the MCP server with Streamable HTTP transport using Starlette and Uvicorn.

        Args:
            host: Host address to bind to.
            port: Port to listen on.
        """
        # Create Starlette app with Streamable HTTP transport
<<<<<<< HEAD
        # self.mcp_server is the actual mcp.server.Server instance from ServiceNowMCP base
        starlette_app = create_starlette_app(self.mcp_server, debug=True)

        # Run using uvicorn
        logger.info(f"Starting Uvicorn server on {host}:{port}")
=======
        starlette_app = create_starlette_app(self.mcp_server, debug=True)

        # Run using uvicorn
>>>>>>> bf5e7fc (Implement ServiceNow MCP Server using Streamable HTTP with Starlette and Uvicorn)
        uvicorn.run(starlette_app, host=host, port=port)


def create_servicenow_mcp(instance_url: str, username: str, password: str):
    """
    Create a ServiceNow MCP server with minimal configuration for HTTP transport.

    This is a simplified factory function that creates a pre-configured
    ServiceNow MCP server with basic authentication, using Streamable HTTP.

    Args:
        instance_url: ServiceNow instance URL.
        username: ServiceNow username.
        password: ServiceNow password.

    Returns:
        A configured ServiceNowHttpMCP instance ready to use.

    Example:
        ```python
        from servicenow_mcp.server_http import create_servicenow_mcp

        # Create an MCP server for ServiceNow
        mcp = create_servicenow_mcp(
            instance_url="https://instance.service-now.com",
            username="admin",
            password="password"
        )

        # Start the server
        mcp.start()
        ```
    """

    # Create basic auth config
    auth_config = AuthConfig(
        type=AuthType.BASIC, basic=BasicAuthConfig(username=username, password=password)
    )

    # Create server config
    config = ServerConfig(instance_url=instance_url, auth=auth_config)

    # Create and return server
    return ServiceNowHttpMCP(config)


def main():
    """Main function to run the ServiceNow MCP HTTP server."""
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Run ServiceNow MCP server with Streamable HTTP transport."
    )
<<<<<<< HEAD
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    args = parser.parse_args()

    # Configure logging level from command line
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info(f"Creating ServiceNowHttpMCP with instance: {os.getenv('SERVICENOW_INSTANCE_URL')}")
=======
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()

>>>>>>> bf5e7fc (Implement ServiceNow MCP Server using Streamable HTTP with Starlette and Uvicorn)
    server = create_servicenow_mcp(
        instance_url=os.getenv("SERVICENOW_INSTANCE_URL"),
        username=os.getenv("SERVICENOW_USERNAME"),
        password=os.getenv("SERVICENOW_PASSWORD"),
    )
    server.start(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
