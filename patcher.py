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

import argparse
import psycopg2
from PySide6 import QtCore, QtWidgets, QtGui
from gui.Entry import Entry
from gui.Handler import Handler
import sys
import json

if __name__ == '__main__':
    parser =  argparse.ArgumentParser(description=ARGS_DESCRIPTION)
    # parser.add_argument("--port", help="The port on which the ESP32 camera is connected.", required=True)
    parser.add_argument("--db-url", help="The database URL.", required=True)
    parser.add_argument("--db-name", help="The database name", required=True)
    parser.add_argument("--db-user", help="The database username", required=True)
    parser.add_argument("--db-pass", help="The database username password", required=True)
    parser.add_argument("--db-port", help="The port on which the database is attached", default=5432)
    parser.add_argument("--firmware", help="Folder of the firmware for the camera", required=True)
    args = parser.parse_args()
    
    # Connect to postgreSQL
    db = psycopg2.connect(
        database=args.db_name,
        host=args.db_url,
        user=args.db_user,
        password=args.db_pass,
        port=args.db_port)
        

    app = QtWidgets.QApplication([])
    widget = Handler(db, args.firmware)
    widget.show()
    sys.exit(app.exec())
    
    cursor.close()
    db.close()
