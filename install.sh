#!/usr/bin/env bash
set -e

echo "🚀 Starting SimpCode Installation..."

# Define repo URL (Users can replace this or it can point to the official repo)
REPO_URL=${1:-"https://github.com/simp-code/simpcode.git"}
# Where the source code will live globally
INSTALL_DIR="${HOME}/.local/share/simpcode"
# Where the symlink will go so it's in the PATH
BIN_DIR="${HOME}/.local/bin"

# Check for dependencies
for cmd in git python3; do
    if ! command -v $cmd &> /dev/null; then
        echo "❌ Error: '$cmd' is not installed. Please install it and try again."
        exit 1
    fi
done

echo "📦 Cloning/Updating SimpCode repository into $INSTALL_DIR..."
if [ -d "$INSTALL_DIR" ]; then
    echo "🔄 Existing installation found. Pulling latest changes..."
    cd "$INSTALL_DIR"
    git pull -q
else
    git clone -q "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo "🐍 Setting up Python Virtual Environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "⚙️  Installing dependencies and configuring the package..."
pip install --quiet --upgrade pip
pip install --quiet -e .

echo "🔗 Creating binary symlink..."
mkdir -p "$BIN_DIR"
ln -sf "$INSTALL_DIR/.venv/bin/simp" "$BIN_DIR/simp"

echo ""
echo "✅ Installation Complete!"
echo "⚠️  Please ensure $BIN_DIR is in your system's PATH."
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "   You can add it by appending the following to your ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"\$PATH:$BIN_DIR\""
fi
echo ""
echo "To get started, simply run:"
echo "  simp setup"
echo "  simp init"
echo ""