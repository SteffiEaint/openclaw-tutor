#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-$(pwd)}"
mkdir -p "$TARGET/ui/peppimock" "$TARGET/ui/mailermock"
cp "$ROOT/ui/peppimock/package.json" "$TARGET/ui/peppimock/package.json"
cp "$ROOT/ui/peppimock/index.html" "$TARGET/ui/peppimock/index.html"
cp "$ROOT/ui/peppimock/vite.config.js" "$TARGET/ui/peppimock/vite.config.js"
cp "$ROOT/ui/mailermock/package.json" "$TARGET/ui/mailermock/package.json"
cp "$ROOT/ui/mailermock/index.html" "$TARGET/ui/mailermock/index.html"
cp "$ROOT/ui/mailermock/vite.config.js" "$TARGET/ui/mailermock/vite.config.js"
echo "Added Vite scaffolding to: $TARGET/ui/peppimock and $TARGET/ui/mailermock"
