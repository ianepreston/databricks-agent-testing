import logging
import os

import uvicorn

from agent_server.app import app


def main():
    # INFO-level app and httpx logs show each turn's stages and every outbound
    # gateway/MCP request (method, URL, status) in `databricks apps logs`.
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    port = int(os.environ.get("DATABRICKS_APP_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
