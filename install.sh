#!/bin/bash
# Installation script for Elysian

set -e

INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="elysian"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SCRIPT="$SCRIPT_DIR/elysian.py"

echo "Installing Elysian..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script requires sudo privileges to install to $INSTALL_DIR"
    echo "Please run: sudo ./install.sh"
    exit 1
fi

# Check if source script exists
if [ ! -f "$SOURCE_SCRIPT" ]; then
    echo "Error: $SOURCE_SCRIPT not found"
    exit 1
fi

# Copy script to install directory
cp "$SOURCE_SCRIPT" "$INSTALL_DIR/$SCRIPT_NAME"

# Make it executable
chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
cat << "EOF"
       _           _             
      | |         (_)            
   ___| |_   _ ___ _  __ _ _ __  
  / _ \ | | | / __| |/ _` | '_ \ 
 |  __/ | |_| \__ \ | (_| | | | |
  \___|_|\__, |___/_|\__,_|_| |_|
          __/ |                  
         |___/                   
EOF
echo "Elysian has been installed successfully!"
echo "You can now use 'elysian' from anywhere in your terminal."
echo ""
echo "Try it out:"
echo "  elysian https://example.com"
echo "  elysian --help"
