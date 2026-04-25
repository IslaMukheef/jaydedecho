#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  EchoFind — Vision Game  /  One-shot setup script
#  Run this on your Linux machine once.
# ═══════════════════════════════════════════════════════════════════

set -e
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║         EchoFind — Setup Script          ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# 1. Install Python deps
echo "▸ Installing Python dependencies…"
pip3 install flask flask-cors requests pillow --quiet

# 2. Check Ollama
echo "▸ Checking Ollama…"
if ! command -v ollama &>/dev/null; then
  echo ""
  echo "  ⚠  Ollama not found. Installing…"
  curl -fsSL https://ollama.com/install.sh | sh
fi

# 3. Pull vision model
echo "▸ Pulling vision model (llava) — this may take a while…"
ollama pull llava

echo ""
echo "✓ Setup complete!"
echo ""
echo "  TO START:"
echo "  ┌─────────────────────────────────────────┐"
echo "  │  Terminal 1:  ollama serve               │"
echo "  │  Terminal 2:  python3 server.py          │"
echo "  │  Browser:     open index.html            │"
echo "  └─────────────────────────────────────────┘"
echo ""
