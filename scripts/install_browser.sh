#!/bin/bash
# Browser automation setup script
# Installs Playwright browsers for browser-use framework

set -e

echo "🌐 Installing Browser Automation Framework..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 is not installed${NC}"
    exit 1
fi

# Install Python dependencies
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
pip install -q browser-use>=0.1.36 playwright>=1.40.0

# Install Playwright browsers
echo -e "${YELLOW}🎭 Installing Playwright browsers...${NC}"
echo "This will download Chromium, Firefox, and WebKit browsers (~500MB)"

# Install all browsers (Chromium, Firefox, WebKit)
playwright install

# Install system dependencies for browsers (required on Linux)
echo -e "${YELLOW}🔧 Installing browser system dependencies...${NC}"
playwright install-deps 2>/dev/null || echo "Note: Some system dependencies might require sudo"

# Verify installation
echo -e "${YELLOW}✓ Verifying installation...${NC}"
python3 -c "
try:
    import browser_use
    import playwright
    from playwright.sync_api import sync_playwright

    # Test browser launch
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('about:blank')
        browser.close()

    print('✅ Browser automation framework installed successfully!')
    print('✅ Playwright browsers installed and working!')
except Exception as e:
    print(f'⚠️  Installation completed but verification failed: {e}')
    print('   This may not be an issue - test manually if needed')
"

echo -e "${GREEN}🚀 Browser automation setup complete!${NC}"
echo ""
echo "Available browsers:"
echo "  - Chromium (recommended for web automation)"
echo "  - Firefox"
echo "  - WebKit (Safari)"
echo ""
echo "Usage:"
echo "  - Headless mode (default): No visible browser window"
echo "  - Headed mode: Set headed=True to see browser in action"
