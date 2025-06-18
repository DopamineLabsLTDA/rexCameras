from PySide6 import QtCore, QtWidgets, QtGui
from gui.Entry import Entry
import subprocess
from pprint import pprint
import json
import os
CAMERA_TABLES = ["dispositivos_kundt", "dispositivos_pendulo", "dispositivos_estanque", "dispositivos_venturi"]
SELECT_TEMPLATE = "SEARCH "
PLATFORM = "esp32cam_ai_thinker"
JSON_COFIG_DEFAULT = "boards/esp32cam_ai_thinker.json"

class Handler(QtWidgets.QWidget):
    def __init__(self, db, project_path):
        super().__init__()
        
        self.db = db
        self.cursor = db.cursor()

        self.project_path = project_path

        self.current_results = []
        self.current_index = 0

        # Widgets
        self.table_selector = QtWidgets.QComboBox(self)
        self.search_button = QtWidgets.QPushButton("Search", self)
        self.info_label = QtWidgets.QLabel(self)
        self.next_button = QtWidgets.QPushButton("Next", self)
        self.refresh_button = QtWidgets.QPushButton("Refresh", self)
        self.back_button = QtWidgets.QPushButton("Back", self)
        self.entry = Entry(self.updateProcess, self)
        

        # Initialize widgets
        self.table_selector.addItems(CAMERA_TABLES)
        self.entry.setEnabled(False)

        # Signals
        self.search_button.clicked.connect(self.searchTable)
        self.refresh_button.clicked.connect(self.refreshEntry)
        self.next_button.clicked.connect(self.nextEntry)
        self.back_button.clicked.connect(self.prevEntry)

        # Layout
        self.layout = QtWidgets.QVBoxLayout(self)

        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.addWidget(self.table_selector)
        controls_layout.addWidget(self.search_button)
        
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.next_button)
        
        self.layout.addLayout(controls_layout)
        self.layout.addWidget(self.info_label)
        self.layout.addLayout(buttons_layout)
        self.layout.addWidget(self.entry)
        
    @QtCore.Slot()
    def searchTable(self):
        # Get current selection
        selection = self.table_selector.currentText()
        # Get all the results
        self.cursor.execute(f"SELECT * FROM {selection} ORDER BY id;")
        results = self.cursor.fetchall()
        n_results = len(results)
        # Update widgets
        self.updateInfoLabel(n_results)
        self.current_results = results
        self.current_index = 0
        self.refreshEntry()
        
    @QtCore.Slot()
    def refreshEntry(self):
        self.entry.fill(self.current_results, self.current_index)


    @QtCore.Slot()
    def updateProcess(self):
        # Get info for entry
        entry_values = self.entry.serialize()
        _id, _equipo, _device, _ip = entry_values
        _, _, _, old_ip = self.current_results[self.current_index]
        
        # Update config file
        self.handleJSON(old_ip)

        # Update firmware and wait
        self.info_label.setText("Burning firmware. Please wait.")
        self.setEnabled(False)
        build_pipe = subprocess.Popen(
            [
                'pio',
                'run',
                '-d',
                self.project_path,
                '-e',
                PLATFORM,
                '-t',
                'upload'
            ]
            
        )
        return_code = build_pipe.wait()
        self.setEnabled(True)

        if return_code == 0:
            # Update entry on db
            table = self.table_selector.currentText()
            self.cursor.execute(f"UPDATE {table} SET equipo = {_equipo}, dispositivo = {_device}, ip = '{_ip}' WHERE id = {_id}")
            self.db.commit()
            

            # Retrive values with changes
            self.searchTable()
            self.info_label.setText("Build completed. Values updated on DB.")
        else:
            self.info_label.setText("BUILD FAILED. Try again.")

    def updateInfoLabel(self, n_results):
        # Check if results where found
        if(n_results != 0):
            self.info_label.setText(f"{n_results} entries found!")
        else:
            self.info_label.setText("No entries found.")
            

    @QtCore.Slot()
    def nextEntry(self):
        n_entries = len(self.current_results)
        if self.current_index == n_entries -1:
            self.current_index = 0
        else:
            self.current_index +=1
            
        # Call update to entry widget
        self.refreshEntry()
        
    @QtCore.Slot()
    def prevEntry(self):
        n_entries = len(self.current_results)
        if self.current_index == 0:
            self.current_index = n_entries -1
        else:
            self.current_index -= 1
        # Update widget
        self.refreshEntry()
        
    def handleJSON(self, ip):
        json_path = os.path.join(self.project_path, JSON_COFIG_DEFAULT)
        with open(json_path, 'r') as json_file:
            json_data = json.load(json_file)
            
        # Handle the macro flag
        extra_flags = json_data['build']['extra_flags']
        
        for i, flag in enumerate(extra_flags):
            if("REXBACK" not in flag):
                continue
            # Modify the flag to the desired ip value
            a, b, c, d = ip.split(".")
            extra_flags[i] = f"'-D REXBACK_IP = {a}, {b}, {c}, {d}'"
        # Update json and write to file
        json_data['build']['extra_flags'] = extra_flags
        json_obj = json.dumps(json_data, indent=2)
        with open(json_path, 'w') as out_json:
            out_json.write(json_obj)