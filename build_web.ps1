# Pyxel Web Build Script for itch.io
$APP_NAME = "slime-drill-proto"
$BUILD_DIR = "dist"

# 1. Cleanup old builds
if (Test-Path $BUILD_DIR) { Remove-Item -Recurse -Force $BUILD_DIR }
New-Item -ItemType Directory -Path $BUILD_DIR

Write-Host "--- Starting Build: $APP_NAME ---" -ForegroundColor Cyan

# 2. Package the app
# Note: This bundles everything in the current directory
Write-Host "Packaging pyxapp..."
pyxel package . main.py
Move-Item "${APP_NAME}.pyxapp" "$BUILD_DIR/${APP_NAME}.pyxapp"

# 3. Convert to HTML
Write-Host "Converting to HTML..."
pyxel app2html "$BUILD_DIR/${APP_NAME}.pyxapp"

# 4. Prepare for itch.io (rename to index.html inside a zip)
Write-Host "Preparing itch.io zip..."
Copy-Item "$BUILD_DIR/${APP_NAME}.html" "$BUILD_DIR/index.html"
Compress-Archive -Path "$BUILD_DIR/index.html" -DestinationPath "$BUILD_DIR/${APP_NAME}_web.zip" -Force

Write-Host "--- Build Complete! ---" -ForegroundColor Green
Write-Host "Upload this file to itch.io: $BUILD_DIR/${APP_NAME}_web.zip"
Write-Host "To test locally, run: python -m http.server -d $BUILD_DIR"
