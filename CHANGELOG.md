# Changelog

All notable changes to this plugin are documented here.

## [1.1.0] - 2026-08-14
### Added
- Prepared for publication on the official QGIS Plugin Repository (plugins.qgis.org).
- `LICENSE` file (GPL-3.0-or-later).
- `changelog`, `homepage`, and `license` fields in `metadata.txt`.

### Changed
- Author/maintainer details updated: Leenath Wimukthi Gamage (leenathgamage@gmail.com).
- Minor robustness improvements to URL parsing and file export error handling.

## [1.0.0] - 2026-08-13
### Added
- Initial release.
- Parse Google Maps links, including `@lat,lon`, `?q=`, `?query=`, `?ll=`,
  place links with `!3d/!4d` pin coordinates, and short links
  (`goo.gl/maps`, `maps.app.goo.gl`) resolved via HTTP redirect.
- Preview parsed results (name, latitude, longitude, status) in a table.
- Add parsed points as a temporary point layer on the map canvas.
- Export parsed points directly to Shapefile, GeoPackage, or GeoJSON.
