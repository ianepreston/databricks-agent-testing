"""The deliberately small learning agent: date + a caller's Google Calendar."""

import logging
import time
from collections.abc import Callable, Generator
from contextlib import AsyncExitStack
from datetime import datetime

import httpx
from agents import (
    Agent,
    Runner,
    function_tool,
    set_default_openai_api,
    set_default_openai_client,
)
from agents.mcp import MCPServerStreamableHttp
from agents.mcp.util import create_static_tool_filter
from agents.tracing import set_trace_processors
from databricks.sdk import WorkspaceClient
from openai import AsyncOpenAI

# The repository's DAB creates this Unity Gateway model service and configures
# its routing plus inference table independently of this application.
MODEL_SERVICE = "databricks_agent_testing.default.demo_model"

logger = logging.getLogger(__name__)


class DatabricksBearerAuth(httpx.Auth):
    """Refresh Databricks credentials immediately before each gateway request."""

    def __init__(self, authenticate: Callable):
        self.authenticate = authenticate

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = self.authenticate()["Authorization"]
        yield request


def request_workspace_client(access_token: str | None = None) -> WorkspaceClient:
    """Use OBO in Apps; fall back to the local Databricks profile during development."""
    if access_token:
        return WorkspaceClient(token=access_token, auth_type="pat")
    return WorkspaceClient()


def configure_model_client(workspace_client: WorkspaceClient) -> None:
    """Configure OpenAI Agents SDK to call the model through Unity Gateway."""
    set_default_openai_client(
        AsyncOpenAI(
            base_url=f"{workspace_client.config.host}/ai-gateway/mlflow/v1",
            api_key="no-token",
            http_client=httpx.AsyncClient(
                auth=DatabricksBearerAuth(workspace_client.config.authenticate),
                follow_redirects=True,
            ),
        )
    )
    set_default_openai_api("chat_completions")


# This v1 deliberately emits no tracing. Add an MLflow trace processor later if
# you want observability; tracing is not required for inference or tool use.
set_trace_processors([])


@function_tool(strict_mode=False)
def get_current_date() -> str:
    """Get today's date in ISO 8601 format."""
    return datetime.now().date().isoformat()


async def init_calendar_server(
    workspace_client: WorkspaceClient,
) -> MCPServerStreamableHttp:
    """Expose exactly one read-only Calendar tool to the model."""
    return MCPServerStreamableHttp(
        params={
            "url": (
                f"{workspace_client.config.host}"
                "/ai-gateway/mcp-services/system.ai.google_calendar"
            ),
            "headers": workspace_client.config.authenticate(),
        },
        name="Google Calendar",
        tool_filter=create_static_tool_filter(
            allowed_tool_names=["calendar_event_list"]
        ),
    )


def create_agent(calendar_server: MCPServerStreamableHttp) -> Agent:
    return Agent(
        name="Calendar Assistant",
        instructions=(
            "You are a helpful calendar assistant. Always call get_current_date before answering "
            "any question about today, the current date, or a relative date. "
            "Use Google Calendar only to answer questions about the caller's calendar. "
            "Do not claim that a calendar action succeeded unless the tool result confirms it."
        ),
        model=MODEL_SERVICE,
        tools=[get_current_date],
        mcp_servers=[calendar_server],
    )


async def answer(message: str, access_token: str | None = None) -> str:
    """Run one stateless turn for the browser user who made this request."""
    started = time.monotonic()
    logger.info("turn start (forwarded token: %s)", access_token is not None)
    workspace_client = request_workspace_client(access_token)
    configure_model_client(workspace_client)
    async with AsyncExitStack() as stack:
        calendar_server = await stack.enter_async_context(
            await init_calendar_server(workspace_client)
        )
        logger.info("calendar MCP connected after %.1fs", time.monotonic() - started)
        result = await Runner.run(
            create_agent(calendar_server),
            message,
        )
        logger.info("turn done after %.1fs", time.monotonic() - started)
        return str(result.final_output)
