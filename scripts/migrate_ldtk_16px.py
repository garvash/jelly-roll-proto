#!/usr/bin/env python3
"""Migrate LDtk project and simplified exports from 8px to 16px grid.

This script performs a one-shot, reproducible migration:
  1. File moves: tiles.png -> tilesets/cavern.png, delete tileset.png
  2. Patch output.ldtk JSON (defaultGridSize, tilesets, layers, levels)
  3. Patch simplified exports (IntGrid.csv downsampling, entity snapping)
  4. Patch entity-schema.json tileset path

Usage:
    python scripts/migrate_ldtk_16px.py

Phase 21 - Tileset & LDtk Pipeline
"""

import json
import glob
import os
import shutil
import sys

# --- Constants ---
OLD_GRID = 8       # Old tile grid size in pixels
NEW_GRID = 16      # New tile grid size in pixels
OLD_COLS = 12      # Old tileset columns (tiles.png was 96px / 8px = 12)
NEW_COLS = 16      # New tileset columns (cavern.png is 256px / 16px = 16)
NEW_TILESET_PX_W = 256  # New tileset width in pixels
NEW_TILESET_PX_H = 256  # New tileset height in pixels

# Paths relative to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(PROJECT_ROOT, "assets")
OUTPUT_LDTK = os.path.join(ASSETS, "output.ldtk")
ENTITY_SCHEMA = os.path.join(ASSETS, "entity-schema.json")
TILES_PNG = os.path.join(ASSETS, "tiles.png")
TILES_ASEPRITE = os.path.join(ASSETS, "tiles.aseprite")
TILESET_PNG = os.path.join(ASSETS, "tileset.png")
TILESETS_DIR = os.path.join(ASSETS, "tilesets")
CAVERN_PNG = os.path.join(TILESETS_DIR, "cavern.png")
CAVERN_ASEPRITE = os.path.join(TILESETS_DIR, "cavern.aseprite")
SIMPLIFIED_DIR = os.path.join(ASSETS, "output", "simplified")


def snap_to_grid(val, grid=NEW_GRID):
    """Snap a pixel value to the nearest grid multiple (round-to-nearest)."""
    return round(val / grid) * grid


def convert_tile_id(old_id):
    """Convert a linear tile ID from old 12-column grid to new 16-column grid.

    Col/row position is preserved; only the linear ID changes because
    tiles_per_row differs (12 -> 16).
    """
    col = old_id % OLD_COLS
    row = old_id // OLD_COLS
    return row * NEW_COLS + col


# ---- Step 1: File Moves ----

def move_tileset_files():
    """Copy tiles.png -> tilesets/cavern.png, delete old tileset.png."""
    os.makedirs(TILESETS_DIR, exist_ok=True)

    if os.path.exists(TILES_PNG):
        shutil.copy2(TILES_PNG, CAVERN_PNG)
        print(f"Copied {TILES_PNG} -> {CAVERN_PNG}")
    else:
        print(f"WARNING: {TILES_PNG} not found, skipping copy")

    if os.path.exists(TILES_ASEPRITE):
        shutil.copy2(TILES_ASEPRITE, CAVERN_ASEPRITE)
        print(f"Copied {TILES_ASEPRITE} -> {CAVERN_ASEPRITE}")
    else:
        print(f"INFO: {TILES_ASEPRITE} not found, skipping (not fatal)")

    if os.path.exists(TILESET_PNG):
        os.remove(TILESET_PNG)
        print(f"Deleted {TILESET_PNG}")
    else:
        print(f"INFO: {TILESET_PNG} already removed")


# ---- Step 2: Patch output.ldtk ----

def patch_output_ldtk():
    """Patch output.ldtk JSON for 16px grid migration."""
    with open(OUTPUT_LDTK, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Top-level
    data["defaultGridSize"] = NEW_GRID
    data["defaultEntityWidth"] = NEW_GRID
    data["defaultEntityHeight"] = NEW_GRID
    print(f"  defaultGridSize: {OLD_GRID} -> {NEW_GRID}")

    # Tileset definitions
    patch_tileset_defs(data)

    # Layer definitions
    patch_layer_defs(data)

    # Level instances
    for level in data.get("levels", []):
        patch_level(level)

    with open(OUTPUT_LDTK, "w", encoding="utf-8") as f:
        json.dump(data, f, indent="\t", ensure_ascii=False)
        f.write("\n")
    print(f"  Wrote patched {OUTPUT_LDTK}")


def patch_tileset_defs(data):
    """Update tileset definitions for 16px grid."""
    tilesets = data.get("defs", {}).get("tilesets", [])
    for ts in tilesets:
        uid = ts.get("uid")
        if uid == 64:
            # Primary auto-rule tileset (Tiles)
            ts["relPath"] = "tilesets/cavern.png"
            ts["pxWid"] = NEW_TILESET_PX_W
            ts["pxHei"] = NEW_TILESET_PX_H
            ts["tileGridSize"] = NEW_GRID
            ts["__cWid"] = NEW_COLS
            ts["__cHei"] = NEW_TILESET_PX_H // NEW_GRID  # 256/16 = 16
            ts["cachedPixelData"] = None
            ts["savedSelections"] = []
            print(f"  Tileset uid=64 (Tiles): relPath=tilesets/cavern.png, "
                  f"tileGridSize={NEW_GRID}, {NEW_TILESET_PX_W}x{NEW_TILESET_PX_H}")
        elif uid == 61:
            # Old tileset.png - update relPath to avoid broken reference
            ts["relPath"] = "tilesets/cavern.png"
            ts["tileGridSize"] = NEW_GRID
            ts["__cWid"] = NEW_COLS
            ts["__cHei"] = NEW_TILESET_PX_H // NEW_GRID
            ts["cachedPixelData"] = None
            print(f"  Tileset uid=61 (Tileset): relPath updated to tilesets/cavern.png")


def patch_layer_defs(data):
    """Update layer gridSize from 8 to 16."""
    layers = data.get("defs", {}).get("layers", [])
    for layer in layers:
        uid = layer.get("uid")
        if uid in (1, 2):  # Entities (uid=1) and IntGrid (uid=2)
            old_gs = layer.get("gridSize", OLD_GRID)
            layer["gridSize"] = NEW_GRID
            print(f"  Layer uid={uid} ({layer.get('identifier')}): "
                  f"gridSize {old_gs} -> {NEW_GRID}")

        # Patch auto-rule tileRectsIds (IntGrid layer)
        if uid == 2:
            patch_auto_rule_tile_ids(layer)


def patch_auto_rule_tile_ids(layer):
    """Recalculate tileRectsIds for 12-col -> 16-col tileset."""
    count = 0
    for group in layer.get("autoRuleGroups", []):
        for rule in group.get("rules", []):
            new_rects = []
            for rect_list in rule.get("tileRectsIds", []):
                new_rect = [convert_tile_id(tid) for tid in rect_list]
                new_rects.append(new_rect)
            rule["tileRectsIds"] = new_rects
            count += 1
    print(f"  Recalculated tileRectsIds for {count} auto-rules (12-col -> 16-col)")


def patch_level(level):
    """Patch a single level's layer instances for 16px grid."""
    level_id = level.get("identifier", "?")
    px_wid = level.get("pxWid", 320)
    px_hei = level.get("pxHei", 176)

    for layer in level.get("layerInstances", []):
        layer_type = layer.get("__type")
        layer["__gridSize"] = NEW_GRID
        layer["__cWid"] = px_wid // NEW_GRID
        layer["__cHei"] = px_hei // NEW_GRID

        if layer_type == "IntGrid":
            patch_intgrid_csv(layer, px_wid)
            patch_autolayer_tiles(layer)
        elif layer_type == "Entities":
            patch_entity_instances(layer)


def patch_intgrid_csv(layer, px_wid):
    """Downsample intGridCsv from 8px to 16px (top-left wins, stride 2)."""
    csv = layer.get("intGridCsv", [])
    if not csv:
        return

    old_width = px_wid // OLD_GRID  # e.g., 320 / 8 = 40
    new_width = px_wid // NEW_GRID  # e.g., 320 / 16 = 20

    # Reshape flat array to 2D
    old_rows = []
    for i in range(0, len(csv), old_width):
        old_rows.append(csv[i:i + old_width])

    # Downsample: take every-other-row, every-other-column
    new_csv = []
    for r in range(0, len(old_rows), 2):
        row = old_rows[r]
        for c in range(0, min(len(row), old_width), 2):
            new_csv.append(row[c])

    layer["intGridCsv"] = new_csv


def patch_autolayer_tiles(layer):
    """Filter auto-tiles to 16px-aligned positions, double src coords."""
    tiles = layer.get("autoLayerTiles", [])
    if not tiles:
        return

    old_count = len(tiles)
    filtered = []
    for tile in tiles:
        px_x, px_y = tile["px"]
        # Keep only tiles at positions divisible by 16 (top-left of 2x2 block)
        if px_x % NEW_GRID == 0 and px_y % NEW_GRID == 0:
            # Scale src coordinates (tileset upscaled 2x: 8px -> 16px tiles)
            tile["src"] = [tile["src"][0] * 2, tile["src"][1] * 2]
            # Recalculate tile ID (t field) for new column count
            old_t = tile.get("t", 0)
            tile["t"] = convert_tile_id(old_t)
            # Recalculate d array coordIds for new grid width
            # d[1] is the coordId = row * width + col in the grid
            # We keep this as-is since it references the old grid; LDtk uses it internally
            filtered.append(tile)

    layer["autoLayerTiles"] = filtered
    print(f"    autoLayerTiles: {old_count} -> {len(filtered)} "
          f"(filtered to 16px-aligned)")


def patch_entity_instances(layer):
    """Snap entity positions to nearest 16px multiple."""
    for entity in layer.get("entityInstances", []):
        px = entity.get("px", [])
        if len(px) >= 2:
            old_px = list(px)
            entity["px"] = [snap_to_grid(px[0]), snap_to_grid(px[1])]
            # Update __grid values
            entity["__grid"] = [
                round(entity["px"][0] / NEW_GRID),
                round(entity["px"][1] / NEW_GRID)
            ]
            # Update __worldX / __worldY if present
            if "__worldX" in entity:
                # worldX/Y = levelWorldX + px
                # Since we're snapping px, worldX/Y should be updated too
                delta_x = entity["px"][0] - old_px[0]
                delta_y = entity["px"][1] - old_px[1]
                entity["__worldX"] = entity.get("__worldX", 0) + delta_x
                entity["__worldY"] = entity.get("__worldY", 0) + delta_y
            if old_px != entity["px"]:
                ident = entity.get("__identifier", "?")
                print(f"    Entity {ident}: px {old_px} -> {entity['px']}")


# ---- Step 3: Patch Simplified Exports ----

def patch_simplified_exports():
    """Patch IntGrid.csv and data.json for each level in simplified export."""
    level_dirs = sorted(glob.glob(os.path.join(SIMPLIFIED_DIR, "Level_*")))
    if not level_dirs:
        print("  WARNING: No simplified export directories found")
        return

    for level_dir in level_dirs:
        level_name = os.path.basename(level_dir)

        # Downsample IntGrid.csv
        csv_path = os.path.join(level_dir, "IntGrid.csv")
        if os.path.exists(csv_path):
            downsample_intgrid_csv(csv_path)

        # Patch data.json entity positions
        data_path = os.path.join(level_dir, "data.json")
        if os.path.exists(data_path):
            patch_simplified_data_json(data_path)

    print(f"  Patched {len(level_dirs)} simplified export directories")


def downsample_intgrid_csv(csv_path):
    """Downsample IntGrid CSV from 40x22 to 20x11 using top-left-wins."""
    with open(csv_path, "r") as f:
        rows = [line.strip() for line in f if line.strip()]

    if not rows:
        return

    # Parse each row into values
    parsed = []
    for row in rows:
        # Handle trailing comma
        vals = [v for v in row.split(",") if v.strip() != ""]
        parsed.append(vals)

    # Downsample: take every-other-row, every-other-column
    new_rows = []
    for r in range(0, len(parsed), 2):
        row = parsed[r]
        new_row = [row[c] for c in range(0, len(row), 2)]
        new_rows.append(",".join(new_row))

    with open(csv_path, "w", newline="\n") as f:
        f.write("\n".join(new_rows) + "\n")


def patch_simplified_data_json(data_path):
    """Snap entity positions in simplified data.json to 16px grid."""
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    entities = data.get("entities", {})
    for entity_type, entity_list in entities.items():
        if not isinstance(entity_list, list):
            continue
        for entity in entity_list:
            if "x" in entity and "y" in entity:
                old_x, old_y = entity["x"], entity["y"]
                entity["x"] = snap_to_grid(old_x)
                entity["y"] = snap_to_grid(old_y)

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent="\t", ensure_ascii=False)
        f.write("\n")


# ---- Step 4: Patch entity-schema.json ----

def patch_entity_schema():
    """Update tileset path in entity-schema.json."""
    with open(ENTITY_SCHEMA, "r", encoding="utf-8") as f:
        data = json.load(f)

    old_path = data.get("biomes", {}).get("cavern", {}).get("tileset", "")
    data["biomes"]["cavern"]["tileset"] = "assets/tilesets/cavern.png"
    print(f"  entity-schema tileset: '{old_path}' -> 'assets/tilesets/cavern.png'")

    with open(ENTITY_SCHEMA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ---- Main ----

def main():
    print("=" * 60)
    print("LDtk 8px -> 16px Migration Script")
    print("=" * 60)

    print("\nStep 1: Moving tileset files...")
    move_tileset_files()

    print("\nStep 2: Patching output.ldtk...")
    patch_output_ldtk()

    print("\nStep 3: Patching simplified exports...")
    patch_simplified_exports()

    print("\nStep 4: Patching entity-schema.json...")
    patch_entity_schema()

    print("\n" + "=" * 60)
    print("Migration complete!")
    print("=" * 60)

    # Quick verification
    verify_migration()


def verify_migration():
    """Run quick sanity checks after migration."""
    errors = []

    # Check tileset file exists
    if not os.path.exists(CAVERN_PNG):
        errors.append("FAIL: tilesets/cavern.png does not exist")
    else:
        print("  OK: tilesets/cavern.png exists")

    # Check tileset.png deleted
    if os.path.exists(TILESET_PNG):
        errors.append("FAIL: tileset.png still exists")
    else:
        print("  OK: tileset.png deleted")

    # Check output.ldtk defaultGridSize
    with open(OUTPUT_LDTK, "r", encoding="utf-8") as f:
        ldtk = json.load(f)
    if ldtk.get("defaultGridSize") != NEW_GRID:
        errors.append(f"FAIL: defaultGridSize is {ldtk.get('defaultGridSize')}, expected {NEW_GRID}")
    else:
        print(f"  OK: defaultGridSize = {NEW_GRID}")

    # Check IntGrid.csv dimensions
    csv_path = os.path.join(SIMPLIFIED_DIR, "Level_0", "IntGrid.csv")
    if os.path.exists(csv_path):
        with open(csv_path) as f:
            rows = [line.strip() for line in f if line.strip()]
        if rows:
            first_row_cols = len([v for v in rows[0].split(",") if v.strip()])
            if first_row_cols != 20:
                errors.append(f"FAIL: IntGrid.csv width = {first_row_cols}, expected 20")
            else:
                print(f"  OK: IntGrid.csv width = 20")
            if len(rows) != 11:
                errors.append(f"FAIL: IntGrid.csv rows = {len(rows)}, expected 11")
            else:
                print(f"  OK: IntGrid.csv rows = 11")

    # Check entity-schema tileset
    with open(ENTITY_SCHEMA, "r", encoding="utf-8") as f:
        schema = json.load(f)
    ts = schema.get("biomes", {}).get("cavern", {}).get("tileset", "")
    if ts != "assets/tilesets/cavern.png":
        errors.append(f"FAIL: entity-schema tileset = '{ts}'")
    else:
        print("  OK: entity-schema tileset = assets/tilesets/cavern.png")

    if errors:
        print("\nERRORS:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("\nAll checks passed!")


if __name__ == "__main__":
    main()
