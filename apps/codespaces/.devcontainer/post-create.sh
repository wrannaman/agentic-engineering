#!/bin/bash
set -e

echo "=== Setting up agentic engineering environment ==="

# Install skills
if [ -d "/workspaces/agentic-eng/skills" ]; then
  echo "Installing skills..."
  /workspaces/agentic-eng/skills/install.sh
fi

# Configure MCP connection to KB server
if [ -n "$KB_SERVER_URL" ] && [ -n "$KB_AUTH_TOKEN" ]; then
  echo "Configuring MCP connection to KB server..."
  mkdir -p .claude
  cat > .mcp.json << EOF
{
  "mcpServers": {
    "kb": {
      "type": "http",
      "url": "${KB_SERVER_URL}/mcp",
      "headers": {
        "Authorization": "Bearer ${KB_AUTH_TOKEN}"
      }
    }
  }
}
EOF
  echo "MCP configured: ${KB_SERVER_URL}"
else
  echo "WARNING: KB_SERVER_URL or KB_AUTH_TOKEN not set. Skipping MCP configuration."
fi

echo "=== Setup complete ==="
