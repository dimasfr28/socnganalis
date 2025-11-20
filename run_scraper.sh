#!/bin/bash

# Script wrapper untuk menjalankan get_Data.py dengan mudah
# Usage: ./run_scraper.sh

echo "=================================================="
echo "  Twitter Replies Scraper"
echo "=================================================="
echo ""

# Check if tweet.xlsx exists
if [ ! -f "tweets-data/tweet.xlsx" ]; then
    echo "❌ Error: File tweets-data/tweet.xlsx tidak ditemukan!"
    echo ""
    echo "Pastikan file tweet.xlsx sudah ada di folder tweets-data/"
    exit 1
fi

# Check if TWITTER_AUTH_TOKEN is set
if [ -z "$TWITTER_AUTH_TOKEN" ]; then
    echo "❌ Error: TWITTER_AUTH_TOKEN tidak ditemukan!"
    echo ""
    echo "Cara set token:"
    echo "  export TWITTER_AUTH_TOKEN='your_token_here'"
    echo ""
    echo "Atau jalankan dengan:"
    echo "  TWITTER_AUTH_TOKEN='your_token' ./run_scraper.sh"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js tidak terinstall!"
    echo ""
    echo "Install Node.js terlebih dahulu:"
    echo "  Ubuntu/Debian: sudo apt-get install nodejs npm"
    echo "  macOS: brew install node"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 tidak terinstall!"
    exit 1
fi

# Check Python dependencies
echo "📦 Checking Python dependencies..."
python3 -c "import pandas, openpyxl" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installing required Python packages..."
    pip install pandas openpyxl
fi

echo ""
echo "✅ All checks passed!"
echo ""
echo "🚀 Starting scraper..."
echo "=================================================="
echo ""

# Run the scraper
python3 get_Data.py

echo ""
echo "=================================================="
echo "✅ Scraper finished!"
echo "=================================================="
