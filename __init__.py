"""
Google Maps Link to Point
--------------------------
A QGIS plugin that converts Google Maps links into point features.

Author:  Leenath Wimukthi Gamage <leenathgamage@gmail.com>
License: GPL-3.0-or-later (see LICENSE)
"""

def classFactory(iface):
    """Entry point required by QGIS to load the plugin."""
    from .gmaps2point import Gmaps2Point
    return Gmaps2Point(iface)
