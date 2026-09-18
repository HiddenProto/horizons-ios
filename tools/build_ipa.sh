#!/usr/bin/env bash
# Build an unsigned Horizons.ipa. Runs on macOS (the GitHub Actions runner); Sideloadly does the
# signing on the user's side, so nothing here needs a certificate.
set -euo pipefail
cd "$(dirname "$0")/.."

PYODIDE=0.27.7
APP=build/Payload/Horizons.app
rm -rf build Horizons.ipa
mkdir -p "$APP" build/icon

echo "== game"
python3 tools/sync_game.py --pack-only

echo "== pyodide $PYODIDE"
mkdir -p web/pyodide
for f in pyodide.js pyodide.asm.js pyodide.asm.wasm python_stdlib.zip pyodide-lock.json; do
  [ -s "web/pyodide/$f" ] || curl -sfL -o "web/pyodide/$f" "https://cdn.jsdelivr.net/pyodide/v$PYODIDE/full/$f"
done

echo "== compile"
xcrun -sdk iphoneos clang -arch arm64 -miphoneos-version-min=15.0 -fobjc-arc -O2 \
  -framework UIKit -framework WebKit -framework Foundation \
  ios/main.m -o "$APP/Horizons"

echo "== bundle"
cp ios/Info.plist "$APP/Info.plist"
mkdir -p "$APP/web/pyodide"
cp web/index.html web/style.css web/app.js web/game.zip web/emblem.png "$APP/web/"
cp web/pyodide/* "$APP/web/pyodide/"

echo "== icon"
# ios/icon-1024.png is drawn by tools/make_icon.py (Pillow, run locally) and committed
SET=build/icon/Assets.xcassets/AppIcon.appiconset
mkdir -p "$SET"
echo '{"info":{"author":"xcode","version":1}}' > build/icon/Assets.xcassets/Contents.json
cp ios/icon-1024.png "$SET/icon-1024.png"
cat > "$SET/Contents.json" <<'JSON'
{"images":[{"filename":"icon-1024.png","idiom":"universal","platform":"ios","size":"1024x1024"}],
 "info":{"author":"xcode","version":1}}
JSON
if ! xcrun actool build/icon/Assets.xcassets --compile "$APP" --platform iphoneos \
     --minimum-deployment-target 15.0 --app-icon AppIcon --target-device iphone --target-device ipad \
     --output-partial-info-plist build/icon/partial.plist; then
  echo "actool failed - using loose icons"
  sips -z 120 120 ios/icon-1024.png --out "$APP/AppIcon60x60@2x.png"
  sips -z 180 180 ios/icon-1024.png --out "$APP/AppIcon60x60@3x.png"
  sips -z 152 152 ios/icon-1024.png --out "$APP/AppIcon76x76@2x~ipad.png"
  sips -z 167 167 ios/icon-1024.png --out "$APP/AppIcon83.5x83.5@2x~ipad.png"
fi
ls "$APP"

plutil -convert binary1 "$APP/Info.plist"
plutil -lint "$APP/Info.plist"
codesign --force --sign - --timestamp=none "$APP" || true

echo "== package"
(cd build && zip -qry ../Horizons.ipa Payload)
ls -la Horizons.ipa
