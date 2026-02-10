#!/usr/bin/env bash
# Setup script for MCP Server
# This script checks prerequisites and installs dependencies

set -e

echo "🔧 MCP Server Setup"
echo "===================="
echo ""

# Check Node.js
echo "Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found"
    echo "Please install Node.js >= 18.0.0 from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Node.js found: $NODE_VERSION"

# Check npm
echo ""
echo "Checking npm..."
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found"
    echo "Please install npm"
    exit 1
fi

NPM_VERSION=$(npm --version)
echo "✅ npm found: $NPM_VERSION"

# Install dependencies
echo ""
echo "Installing MCP server dependencies..."
cd "$(dirname "$0")"
npm install

echo ""
echo "✅ MCP Server setup complete!"
echo ""
echo "To test the server, run:"
echo "  npm start"
echo ""
echo "To run tests, run:"
echo "  npm test"
