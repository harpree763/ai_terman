#!/usr/bin/env bash
set -e
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
REPO="https://github.com/harpree763/ai_terman"
INSTALL_DIR="$HOME/.ai-terminal"
echo -e "${CYAN}${BOLD}  AI Terminal Installer${NC}"
echo -e "${YELLOW}[1/5] Checking dependencies...${NC}"
sudo apt-get update -qq
sudo apt-get install -y python3 python3-pip python3-venv git
echo -e "${GREEN}✓ Dependencies ready${NC}"
echo -e "${YELLOW}[2/5] Downloading...${NC}"
if [ -d "$INSTALL_DIR/.git" ]; then git -C "$INSTALL_DIR" pull --quiet; else git clone --quiet "$REPO" "$INSTALL_DIR"; fi
echo -e "${GREEN}✓ Downloaded${NC}"
echo -e "${YELLOW}[3/5] Installing Python dependencies...${NC}"
python3 -m venv "$INSTALL_DIR/.venv"
source "$INSTALL_DIR/.venv/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet -r "$INSTALL_DIR/requirements.txt"
deactivate
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo -e "${YELLOW}[4/5] Setting up API key...${NC}"
cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
echo -e "${GREEN}✓ API key configured${NC}"
echo -e "${YELLOW}[5/5] Creating 'ait' command...${NC}"
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/ait" << EOF
#!/usr/bin/env bash
source "$INSTALL_DIR/.venv/bin/activate"
python3 "$INSTALL_DIR/agent.py" "\$@"
deactivate
EOF
chmod +x "$HOME/.local/bin/ait"
grep -qxF 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc" 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
export PATH="$HOME/.local/bin:$PATH"
echo -e "${GREEN}${BOLD}"
echo "  ✓ Done! Run: ait"
echo -e "${NC}"
