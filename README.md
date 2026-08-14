## Screenshots

### Main Plugin Window

plugin_window.png.jpg

### Google Maps Link Input

plugin_window_Link.png.jpg

### Results Preview

plugin_window_Results.png.jpg
# Google Maps Link to Point — QGIS Plugin

**Author:** Leenath Wimukthi Gamage ([leenathgamage@gmail.com](mailto:leenathgamage@gmail.com))
**License:** GPL-3.0-or-later
**Version:** 1.1.0

Paste one or more Google Maps links and convert them into point features.
Add them straight to your map as a temporary layer, or export directly to
Shapefile, GeoPackage, or GeoJSON.

## Supported link formats

- `https://www.google.com/maps/place/Some+Place/@-37.8136,144.9631,15z/data=!...!3d-37.8140!4d144.9633`
- `https://www.google.com/maps/@-37.8136,144.9631,15z`
- `https://www.google.com/maps?q=-37.8136,144.9631`
- `https://www.google.com/maps/search/?api=1&query=-37.8136,144.9631`
- `https://maps.google.com/maps?ll=-37.8136,144.9631`
- Short links: `https://maps.app.goo.gl/xxxxxxxx` and `https://goo.gl/maps/xxxxxxxx`
  (these are resolved via an HTTP redirect, so an internet connection is
  needed for short links specifically)

For "place" links that include a `!3d...!4d...` pair, that pair is used as
the coordinate (it's the actual pin location), rather than the `@lat,lon` in
the URL, which is just the map's viewport center and can be a bit off.

## Installation

**Option A — Install from ZIP (recommended)**
1. In QGIS, go to `Plugins > Manage and Install Plugins... > Install from ZIP`.
2. Point it at `gmaps2point.zip` (this whole folder, zipped).
3. Click "Install Plugin". Enable it if it isn't already enabled.

**Option B — Manual copy**
1. Find your QGIS plugins folder:
   - Windows: `C:\Users\<you>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`
   - macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins`
   - Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`
2. Copy the entire `gmaps2point` folder into that directory.
3. Restart QGIS, then go to `Plugins > Manage and Install Plugins... > Installed`
   and enable "Google Maps Link to Point".

## Usage

1. Open it via `Plugins > Google Maps to Point > Google Maps Link to Point`,
   or click its toolbar icon.
2. Paste one or more Google Maps links, one per line.
3. Click **Parse Links** — a preview table shows the name (if detected),
   latitude, longitude, and status for each link.
4. Click **Add Point Layer to Map** to add a temporary point layer to the
   current project, or **Export to File...** to save directly as a
   Shapefile, GeoPackage, or GeoJSON.

## Notes / limitations

- Short links (`goo.gl`, `maps.app.goo.gl`) require QGIS to reach the
  internet at parse time to resolve the redirect.
- A small number of Google Maps link styles (particularly ones that only
  encode a business Place ID with no coordinates anywhere in the URL, e.g.
  some `cid=` links) don't carry a lat/lon at all — geocoding those would
  require the Google Places API, which isn't used here.
- Output points use CRS EPSG:4326 (WGS84), matching the coordinates Google
  Maps URLs use.

## Files

```
gmaps2point/
├── __init__.py            # QGIS plugin entry point
├── metadata.txt           # Plugin metadata (name, version, description)
├── gmaps2point.py          # Main plugin class (menu/toolbar integration)
├── gmaps2point_dialog.py   # Dialog UI: input, preview table, actions
├── url_parser.py           # Regex/redirect logic for extracting coordinates
├── icon.png                # Toolbar icon
├── LICENSE                 # GPL-3.0-or-later
├── CHANGELOG.md
└── README.md
```

## Publishing to the official QGIS Plugin Repository

The official repository is at **https://plugins.qgis.org**. Here's the full path
from where this stands now to a public listing:

### 1. Create the GitHub repository
1. On GitHub, create a new **public** repo, e.g. `gmaps2point`.
2. Push the contents of this folder to it (not the zip — the raw files):
   ```bash
   cd gmaps2point
   git init
   git add .
   git commit -m "Initial commit: v1.1.0"
   git branch -M main
   git remote add origin https://github.com/Leenath-Gamage/gmaps2point.git
   git push -u origin main
   ```
   `metadata.txt` already points `tracker`, `repository`, and `homepage` at
   `https://github.com/Leenath-Gamage/gmaps2point` — just make sure the repo
   you create is named `gmaps2point` (or update those three fields to match
   whatever name you actually use).

### 2. Create a QGIS plugins.qgis.org account
1. Go to https://plugins.qgis.org and register/log in (it uses OSGeo credentials —
   if you don't have an OSGeo account yet, create one at https://www.osgeo.org/community/getting-started-osgeo/osgeo-userid/).

### 3. Package the plugin
- Zip the **`gmaps2point` folder itself** (not just its contents) so that
  paths inside the zip start with `gmaps2point/...` — this is what QGIS
  expects when installing.
- The folder name must exactly match the plugin's Python package name used
  in `__init__.py` / `classFactory` (it does: `gmaps2point`).
- Rebuild it after any metadata edits:
  ```bash
  cd /path/to/parent/of/gmaps2point
  zip -r gmaps2point.zip gmaps2point -x "*.pyc" -x "*__pycache__*"
  ```

### 4. Validate before submitting
- Optional but recommended: run the [Plugin Builder validator](https://plugins.qgis.org/plugins/validator/)
  or install [plugin_reloader](https://plugins.qgis.org/plugins/pluginreloader/) locally and load the
  zip via `Install from ZIP` to confirm it activates cleanly with no console errors.
- Double-check `metadata.txt` has no empty required fields (`name`,
  `qgisMinimumVersion`, `description`, `version`, `author`, `email`,
  `about`, `tracker`, `repository`).

### 5. Upload
1. On plugins.qgis.org, go to **"Share a plugin"** / **"Upload a plugin"**.
2. Upload `gmaps2point.zip`.
3. New plugins are held for moderator review before appearing publicly —
   this typically takes a few days. You'll get an email once it's approved.

### 6. Releasing updates later
- Bump `version` in `metadata.txt` (e.g. `1.1.0` → `1.1.1`), add a new
  `changelog` entry, rebuild the zip, and upload it again through the same
  "Share a plugin" flow — QGIS matches updates by the plugin's internal name.
