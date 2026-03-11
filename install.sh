#!/usr/bin/env bash
set -e
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
REPO="https://github.com/harpree763/ai_terman"
INSTALL_DIR="$HOME/.ai-terminal"
echo -e "${CYAN}${BOLD}  AI Terminal Installer${NC}"
echo -e "${YELLOW}[1/5] Checking dependencies...${NC}"
if ! command -v python3 &>/dev/null; then sudo apt-get update -qq && sudo apt-get install -y python3 python3-pip python3.11-venv; else sudo apt-get install -y python3.11-venv 2>/dev/null; echo -e "${GREEN}✓ python3 found${NC}"; fi
if ! command -v git &>/dev/null; then sudo apt-get install -y git; fi
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
ENV_FILE="$INSTALL_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then cp "$INSTALL_DIR/.env.example" "$ENV_FILE"; fi
echo -e "${CYAN}  Enter your Google Gemini API key:${NC}"
read -rp "  API Key: " user_api_key < /dev/tty
if [ -n "$user_api_key" ]; then
  sed -i "s|^GOOGLE_API_KEY=.*|GOOGLE_API_KEY=$user_api_key|" "$ENV_FILE"
  echo -e "${GREEN}✓ Key saved${NC}"
else
  echo -e "${RED}✗ No key entered. Edit manually: $ENV_FILE${NC}"
fi
echo -e "${YELLOW}[5/5] Creating 'ait' command...${NC}"
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/ait" << EOF
#!/usr/bin/env bash
source "$INSTALL_DIR/.venv/bin/activate"
python3 "$INSTALL_DIR/agent.py" "\$@"
deactivate
EOF
chmod +x "$HOME/.local/bin/ait"
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"; fi
echo -e "${GREEN}${BOLD}✓ Done! Run: ait \"your task here\"${NC}"
