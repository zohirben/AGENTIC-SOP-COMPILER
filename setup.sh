#!/usr/bin/env bash
# ── Agentic SOP Compiler — Quick Setup ───────────────────────────────────────
# Usage:  chmod +x setup.sh && ./setup.sh
set -e

VENV_DIR="venv"
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   Agentic SOP Compiler — Environment Setup  ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
echo ""

# 1. Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${GREEN}[1/5]${NC} Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo -e "${GREEN}[1/5]${NC} Virtual environment already exists."
fi

# 2. Activate and install deps
echo -e "${GREEN}[2/5]${NC} Installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "       ✅ $(pip list --format=columns | wc -l) packages installed."

# 3. Create .env from template if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${GREEN}[3/5]${NC} Creating .env from template..."
    cp .env.example .env
    echo -e "       ${RED}⚠  EDIT .env and add your API keys before running!${NC}"
else
    echo -e "${GREEN}[3/5]${NC} .env already exists — skipping."
fi

# 4. Create outputs directory
echo -e "${GREEN}[4/5]${NC} Ensuring output directories exist..."
mkdir -p outputs
touch outputs/.gitkeep

# 5. Generate mock data
echo -e "${GREEN}[5/5]${NC} Generating mock data..."
python scripts/generate_mock_data.py
echo "       ✅ data/mock_data.csv ready."

echo ""
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup complete! Next steps:${NC}"
echo ""
echo -e "  1. ${CYAN}Edit .env${NC} — add your CEREBRAS_API_KEY"
echo -e "  2. ${CYAN}source venv/bin/activate${NC}"
echo -e "  3. ${CYAN}streamlit run app.py${NC}"
echo ""
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
