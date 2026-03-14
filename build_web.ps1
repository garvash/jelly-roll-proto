# Pyxel Web Build Script for itch.io
$APP_NAME = "jelly-roll-proto"
$BUILD_DIR = "dist"
$STAGING_DIR = "build_staging"

Write-Host "--- Starting Clean Build: $APP_NAME ---" -ForegroundColor Cyan

# 1. Setup directories
if (Test-Path $BUILD_DIR) { Remove-Item -Recurse -Force $BUILD_DIR }
if (Test-Path $STAGING_DIR) { Remove-Item -Recurse -Force $STAGING_DIR }
New-Item -ItemType Directory -Path $BUILD_DIR
New-Item -ItemType Directory -Path $STAGING_DIR

# 2. Stage only necessary files
Write-Host "Staging files..."
Copy-Item "main.py" "$STAGING_DIR/"
Copy-Item -Recurse "src" "$STAGING_DIR/"
Copy-Item -Recurse "assets" "$STAGING_DIR/"

# Clean pycache from staging
Get-ChildItem -Path $STAGING_DIR -Include __pycache__ -Recurse | Remove-Item -Recurse -Force

# 3. Package the app
Write-Host "Packaging pyxapp..."
Push-Location $STAGING_DIR
# This creates a package named after the directory
pyxel package . main.py
Pop-Location

# Rename the directory-named package to our app name and move to dist
$GENERATED_PACKAGE = "$STAGING_DIR/build_staging.pyxapp"
if (Test-Path $GENERATED_PACKAGE) {
    Move-Item $GENERATED_PACKAGE "$BUILD_DIR/${APP_NAME}.pyxapp"
} else {
    Write-Error "Could not find generated package at $GENERATED_PACKAGE"
    exit
}

# 4. Convert to HTML
Write-Host "Converting to HTML..."
pyxel app2html "$BUILD_DIR/${APP_NAME}.pyxapp"
# pyxel app2html output goes to current directory
Move-Item "${APP_NAME}.html" "$BUILD_DIR/index.html"

# 5. Prepare itch.io zip
Write-Host "Preparing itch.io zip..."
Compress-Archive -Path "$BUILD_DIR/index.html" -DestinationPath "$BUILD_DIR/${APP_NAME}_web.zip" -Force

# Cleanup staging
Remove-Item -Recurse -Force $STAGING_DIR

Write-Host "--- Build Complete! ---" -ForegroundColor Green
Write-Host "Upload this file to itch.io: $BUILD_DIR/${APP_NAME}_web.zip"
Write-Host "To test locally, run: python -m http.server -d $BUILD_DIR"
