"""
ServiceNow MCP Server (HTTP)

This module provides the main implementation of the ServiceNow MCP server
using Streamable HTTP transport.
"""

import argparse
import os
from typing import Dict, Union

import uvicorn
from dotenv import load_dotenv
from mcp.server import Server

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

    return Starlette(
        debug=debug,
        routes=[
            Route("/", endpoint=handle_http),  # Typically MCP over HTTP uses the root path
        ],
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

    def start(self, host: str = "0.0.0.0", port: int = 8080):
        """
        Start the MCP server with Streamable HTTP transport using Starlette and Uvicorn.

        Args:
            host: Host address to bind to.
            port: Port to listen on.
        """
        # Create Starlette app with Streamable HTTP transport
        starlette_app = create_starlette_app(self.mcp_server, debug=True)

        # Run using uvicorn
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
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()

    server = create_servicenow_mcp(
        instance_url=os.getenv("SERVICENOW_INSTANCE_URL"),
        username=os.getenv("SERVICENOW_USERNAME"),
        password=os.getenv("SERVICENOW_PASSWORD"),
    )
    server.start(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
