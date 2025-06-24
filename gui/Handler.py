from PySide6 import QtCore, QtWidgets, QtGui
from gui.Entry import Entry
from gui.Threads.FSBuildThread import FSBuilder
from gui.Threads.FSUploadThread import FSUpload
from gui.Threads.BuilderThread import Builder
import subprocess
import json
import os

CAMERA_TABLES = ["dispositivos_kundt", "dispositivos_pendulo", "dispositivos_estanque", "dispositivos_venturi"]
SELECT_TEMPLATE = "SEARCH "
PLATFORM = "esp32cam_ai_thinker"
JSON_COFIG_DEFAULT = "boards/esp32cam_ai_thinker.json"
DEFAULT_GATEWAY = "192.168.0.1"
DEFAULT_MASK = "255.255.255.0"

DEFAULT_THING_NAME = "rexCamera-ESP32"
DEFAULT_AP_PASS = "rexcamera"

MAIN_KEY = "iwcAll"
SYS_KEY = "iwcSys"
THING_NAME_KEY = "iwcThingName"
AP_PASS_KEY = "iwcApPassword"
WIFI_KEY = "iwcWifi0"
WIFI_SSID_KEY = "iwcWifiSsid"
WIFI_PASS_KEY = "iwcWifiPassword"
CUSTOM_KEY = "iwcCustom"
CONN_KEY = "conn"
CAMERA_KEY = "camera"
IP_KEY = "ipAddress"
GATE_KEY = "gateway"
MASK_KEY = "netmask"


class Handler(QtWidgets.QWidget):
    def __init__(self, db, project_path, config_path):
        super().__init__()
        
        self.db = db
        self.cursor = db.cursor()

        self.project_path = project_path
        self.config_path = config_path

        self.current_results = []
        self.current_index = 0

        self.builder_thread = None
        self.build_data = None

        # Widgets
        self.table_selector = QtWidgets.QComboBox(self)
        self.thing_name = QtWidgets.QLineEdit(self)
        self.ap_pass = QtWidgets.QLineEdit(self)
        self.wifi_ssid = QtWidgets.QLineEdit(self)
        self.wifi_pass = QtWidgets.QLineEdit(self)
        self.gateway = QtWidgets.QLineEdit(self)
        self.mask = QtWidgets.QLineEdit(self)
        self.info_label = QtWidgets.QLabel(self)
        self.next_button = QtWidgets.QPushButton("Next", self)
        self.refresh_button = QtWidgets.QPushButton("Refresh", self)
        self.back_button = QtWidgets.QPushButton("Back", self)
        self.entry = Entry(self.updateProcess, self)
        

        # Initialize widgets
        self.thing_name.setText(DEFAULT_THING_NAME)
        self.ap_pass.setText(DEFAULT_AP_PASS)
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.table_selector.addItems(CAMERA_TABLES)
        self.entry.setEnabled(False)
        self.info_label.setStyleSheet('font-weight: bold')
        self.gateway.setText(DEFAULT_GATEWAY)
        self.mask.setText(DEFAULT_MASK)
        self.searchTable(0)

        # Signals
        self.table_selector.currentIndexChanged.connect(self.searchTable)
        self.refresh_button.clicked.connect(self.refreshEntry)
        self.next_button.clicked.connect(self.nextEntry)
        self.back_button.clicked.connect(self.prevEntry)

        # Layout
        self.layout = QtWidgets.QVBoxLayout(self)

        controls_layout = QtWidgets.QFormLayout()
        controls_layout.addRow(self.table_selector)
        controls_layout.addRow("Thing Name:", self.thing_name)
        controls_layout.addRow("AP Password:", self.ap_pass)
        controls_layout.addRow("SSID:", self.wifi_ssid)
        controls_layout.addRow("PASS:", self.wifi_pass)
        controls_layout.addRow("GATEWAY:", self.gateway)
        controls_layout.addRow("MASK:", self.mask)
    
        
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.next_button)
        
        self.layout.addLayout(controls_layout)
        self.layout.addWidget(self.info_label)
        self.layout.addLayout(buttons_layout)
        self.layout.addWidget(self.entry)
        
    @QtCore.Slot()
    def searchTable(self, value):
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
        self.build_data = self.entry.serialize()
        _id, _equipo, _device, _ip, _substring = self.build_data
        
        # Update config file
        self.handleJSON(_ip)

        # Update firmware and wait
        self.info_label.setStyleSheet('color: ')
        self.info_label.setText("Building filesystem.")
        self.setEnabled(False)
        
        # Start building process
        self.builder_thread = FSBuilder(self.project_path, PLATFORM, self)
        self.builder_thread.exit_code.connect(self.handleBuildFSExit)
        self.builder_thread.start()

        #self.builder_thread = Builder(self.project_path, PLATFORM, self)
        #self.builder_thread.exit_code.connect(self.dbHandle)
        #self.builder_thread.start()
        
    @QtCore.Slot()
    def handleBuildFSExit(self, result_code):
        # Check code value 
        if(result_code != 0):
            # Error during process
            self.info_label.setText("Filesystem build failed.")
            self.info_label.setStyleSheet("color: red")
            self.setEnabled(True)
            self.builder_thread = None
        else:
            # Process completed: Upload filesystem
            self.builder_thread = FSUpload(self.project_path, PLATFORM, self)
            self.builder_thread.exit_code.connect(self.handleUploadFSExit)
            self.info_label.setText("Uploading filesystem.")
            self.builder_thread.start()
            
    @QtCore.Slot()
    def handleUploadFSExit(self, result_code):
        if (result_code != 0):
            # Error during process
            self.info_label.setText("Filesystem upload error.")
            self.info_label.setStyleSheet("color: red")
            self.setEnabled(True)
            self.builder_thread = None
        else:
            # Process completed: Build firmware
            self.builder_thread = Builder(self.project_path, PLATFORM, self)
            self.builder_thread.exit_code.connect(self.dbHandle)            
            self.info_label.setText("Building firmware")
            self.builder_thread.start()

    @QtCore.Slot()
    def dbHandle(self, result_code):
        _id, _equipo, _device, _ip, _substring = self.build_data
        # Generate new ip for registry
        new_ip = _ip + _substring        

        self.setEnabled(True)

        if result_code == 0:
            # Update entry on db
            table = self.table_selector.currentText()
            self.cursor.execute(f"UPDATE {table} SET equipo = {_equipo}, dispositivo = {_device}, ip = '{new_ip}' WHERE id = {_id}")
            self.db.commit()
            

            # Retrive values with changes
            self.searchTable(0)
            self.info_label.setStyleSheet('color: ')
            self.info_label.setText("Build completed. Values updated on DB.")
        else:
            self.info_label.setText("BUILD FAILED. Try again.")
            self.info_label.setStyleSheet("color: red")

    def updateInfoLabel(self, n_results):
        # Check if results where found
        self.info_label.setStyleSheet('color: ')
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
        with open(self.config_path, 'r') as json_file:
            json_data = json.load(json_file)
        
        # Main system parameters
        system_parameters = json_data[MAIN_KEY][SYS_KEY]
        # -> Update name
        system_parameters[THING_NAME_KEY] = self.thing_name.text()
        # -> ap password
        system_parameters[AP_PASS_KEY] = self.ap_pass.text()
        # -> Setup wifi
        system_parameters[WIFI_KEY][WIFI_SSID_KEY] = self.wifi_ssid.text()
        system_parameters[WIFI_KEY][WIFI_PASS_KEY] = self.wifi_pass.text()
        
        # Connection parameters
        conn_parameters = json_data[MAIN_KEY][CUSTOM_KEY][CONN_KEY]
        # -> Set static ip
        conn_parameters[IP_KEY] = ip
        conn_parameters[GATE_KEY] = self.gateway.text()
        conn_parameters[MASK_KEY] = self.mask.text()

        # Write onto the file
        json_obj = json.dumps(json_data, indent=4)
        with open(self.config_path, 'w') as out_json:
            out_json.write(json_obj)