#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: patcher.py
Author: Mauricio Aravena Cifuentes (mac@dopaminelabs.cl)
Date: 15 - 06 - 2025
Version: 1.0
Description: Automatic patcher for the ESP32 based cameras. 
"""
ARGS_DESCRIPTION = "A simple patcher program for the esp32 based cameras."

## PATHS
FW_FOLDER_PATH = "./esp32CamFirmware"
CONFIG_JSON_PATH = "./esp32CamFirmware/data/config.json"

from PySide6 import QtWidgets
from gui.Entry import Entry
from gui.Handler import Handler
import sys

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    widget = Handler(FW_FOLDER_PATH, CONFIG_JSON_PATH)
    widget.show()
    sys.exit(app.exec())
