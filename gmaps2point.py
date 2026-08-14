"""
gmaps2point.py
Main plugin class: registers the toolbar/menu entry and opens the dialog.

Author:  Leenath Wimukthi Gamage <leenathgamage@gmail.com>
License: GPL-3.0-or-later (see LICENSE)
"""

import os

from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon

from .gmaps2point_dialog import Gmaps2PointDialog


class Gmaps2Point:
    """QGIS plugin: convert Google Maps links into point features."""

    def __init__(self, iface):
        self.iface = iface
        self.actions = []
        self.menu = "&Google Maps to Point"
        self.dlg = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()

        self.action = QAction(icon, "Google Maps Link to Point", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.action.setEnabled(True)

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.menu, self.action)
        self.actions.append(self.action)

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        self.actions = []

    def run(self):
        if self.dlg is None:
            self.dlg = Gmaps2PointDialog(self.iface.mainWindow())
        self.dlg.show()
        self.dlg.exec_()
