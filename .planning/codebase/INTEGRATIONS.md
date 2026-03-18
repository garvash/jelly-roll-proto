# External Integrations

**Analysis Date:** 2026-03-18

## APIs & External Services

**Not detected:** The game is a standalone local application and does not communicate with external APIs at runtime.

## Data Storage

**Databases:**
- **Local JSON/CSV:** Used for level data.
  - Client: Custom parsers in `src/level/map.py` using standard `json` and `os` libraries.
  - Data locations: `assets/map.json`, `assets/map.ldtk`, `assets/cave/simplified/`.

**File Storage:**
- **Local Filesystem:**
  - `assets/game.pyxres` - All-in-one resource file for graphics, sounds, and music.
  - `assets/tileset.png` - Exported from `generate_assets.py` for external editor use.

**Caching:**
- **None:** No network caching required.

## Authentication & Identity

**Auth Provider:**
- **None:** The project is a single-player local game.

## Monitoring & Observability

**Error Tracking:**
- **None:** Relies on standard Python traceback and console logging.

**Logs:**
- **Console:** Uses `print()` for development-time logging of map loading and system status.

## CI/CD & Deployment

**Hosting:**
- **itch.io:** Primary target for web and desktop builds as indicated by `ITCH_README.md` and `build_web.ps1`.

**CI Pipeline:**
- **None detected:** Manual build process via `build_web.ps1`.

## Environment Configuration

**Required env vars:**
- **None:** Configuration is handled within the code or by the Pyxel runtime.

**Secrets location:**
- **Not applicable:** No secrets detected.

## Webhooks & Callbacks

**Incoming:**
- **None**

**Outgoing:**
- **None**

---

*Integration audit: 2024-10-24*
