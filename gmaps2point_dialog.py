"""
gmaps2point_dialog.py
Dialog UI: paste links, preview parsed points, add to map or export.

Author:  Leenath Wimukthi Gamage <leenathgamage@gmail.com>
License: GPL-3.0-or-later (see LICENSE)
"""

from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QFileDialog,
    QHeaderView,
)
from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsField,
    QgsProject,
    QgsVectorFileWriter,
)

from .url_parser import parse_gmaps_url_full


class Gmaps2PointDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Google Maps Link to Point")
        self.resize(650, 520)
        self.results = []  # list of dicts from parse_gmaps_url_full
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Paste one or more Google Maps links (one per line):"))
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "https://www.google.com/maps/place/.../@-37.8136,144.9631,15z/...\n"
            "https://maps.app.goo.gl/xxxxx\n"
            "https://www.google.com/maps?q=-37.8136,144.9631"
        )
        self.text_input.setFixedHeight(120)
        layout.addWidget(self.text_input)

        btn_row = QHBoxLayout()
        self.parse_btn = QPushButton("Parse Links")
        self.parse_btn.clicked.connect(self.parse_links)
        btn_row.addWidget(self.parse_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Name", "Latitude", "Longitude", "Status"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.table)

        action_row = QHBoxLayout()
        self.add_layer_btn = QPushButton("Add Point Layer to Map")
        self.add_layer_btn.clicked.connect(self.add_point_layer)
        self.export_btn = QPushButton("Export to File...")
        self.export_btn.clicked.connect(self.export_to_file)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        action_row.addWidget(self.add_layer_btn)
        action_row.addWidget(self.export_btn)
        action_row.addStretch()
        action_row.addWidget(self.close_btn)
        layout.addLayout(action_row)

    def parse_links(self):
        text = self.text_input.toPlainText()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if not lines:
            QMessageBox.warning(self, "No input", "Please paste at least one Google Maps link.")
            return

        self.results = []
        self.table.setRowCount(0)

        for line in lines:
            result = parse_gmaps_url_full(line)
            self.results.append(result)

            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(result["name"]))
            lat_text = f'{result["lat"]:.6f}' if result["lat"] is not None else ""
            lon_text = f'{result["lon"]:.6f}' if result["lon"] is not None else ""
            self.table.setItem(row, 1, QTableWidgetItem(lat_text))
            self.table.setItem(row, 2, QTableWidgetItem(lon_text))
            self.table.setItem(row, 3, QTableWidgetItem(result["status"]))

        ok_count = sum(1 for r in self.results if r["lat"] is not None)
        QMessageBox.information(
            self,
            "Parsing complete",
            f"Parsed {ok_count} of {len(self.results)} link(s) successfully.",
        )

    def _build_memory_layer(self):
        valid = [r for r in self.results if r["lat"] is not None]
        if not valid:
            QMessageBox.warning(
                self,
                "No valid points",
                "No coordinates were successfully parsed yet. Click 'Parse Links' first.",
            )
            return None

        layer = QgsVectorLayer("Point?crs=EPSG:4326", "Google Maps Points", "memory")
        provider = layer.dataProvider()
        provider.addAttributes(
            [
                QgsField("name", QVariant.String),
                QgsField("latitude", QVariant.Double),
                QgsField("longitude", QVariant.Double),
                QgsField("source_url", QVariant.String),
            ]
        )
        layer.updateFields()

        features = []
        for r in valid:
            feat = QgsFeature(layer.fields())
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(r["lon"], r["lat"])))
            feat.setAttributes([r["name"], r["lat"], r["lon"], r["input_url"]])
            features.append(feat)
        provider.addFeatures(features)
        layer.updateExtents()
        return layer

    def add_point_layer(self):
        layer = self._build_memory_layer()
        if layer:
            QgsProject.instance().addMapLayer(layer)
            QMessageBox.information(
                self, "Layer added", f"Added layer with {layer.featureCount()} point(s)."
            )

    def export_to_file(self):
        layer = self._build_memory_layer()
        if not layer:
            return

        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Point Layer",
            "",
            "GeoPackage (*.gpkg);;Shapefile (*.shp);;GeoJSON (*.geojson)",
        )
        if not path:
            return

        if "GeoPackage" in selected_filter and not path.endswith(".gpkg"):
            path += ".gpkg"
        elif "Shapefile" in selected_filter and not path.endswith(".shp"):
            path += ".shp"
        elif "GeoJSON" in selected_filter and not path.endswith(".geojson"):
            path += ".geojson"

        ext = "." + path.rsplit(".", 1)[-1].lower()
        driver_map = {".gpkg": "GPKG", ".shp": "ESRI Shapefile", ".geojson": "GeoJSON"}
        driver_name = driver_map.get(ext, "GPKG")

        error = self._write_layer(layer, path, driver_name)

        if error:
            QMessageBox.critical(self, "Export failed", f"Error: {error}")
        else:
            QMessageBox.information(self, "Export complete", f"Saved to:\n{path}")

    @staticmethod
    def _write_layer(layer, path, driver_name):
        """
        Write `layer` to `path` using whichever QgsVectorFileWriter API is
        available on the running QGIS version. Returns None on success, or
        an error description string on failure.
        """
        try:
            # QGIS >= 3.20
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = driver_name
            result = QgsVectorFileWriter.writeAsVectorFormatV3(
                layer, path, QgsProject.instance().transformContext(), options
            )
            error_code = result[0] if isinstance(result, tuple) else result
            if error_code == QgsVectorFileWriter.NoError:
                return None
            return str(result)
        except AttributeError:
            pass

        try:
            # Older QGIS fallback
            error_code, error_message = QgsVectorFileWriter.writeAsVectorFormat(
                layer, path, "UTF-8", layer.crs(), driver_name
            )
            if error_code == QgsVectorFileWriter.NoError:
                return None
            return error_message
        except Exception as exc:
            return str(exc)
