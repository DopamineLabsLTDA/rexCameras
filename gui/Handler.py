from PySide6 import QtCore, QtWidgets
from gui.Camera import CameraWidget
from gui.Platform import PlatformWidget
from gui.Threads.FSBuildThread import FSBuilder
from gui.Threads.FSUploadThread import FSUpload
from gui.Threads.BuilderThread import Builder
import json

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
    def __init__(self, project_path, config_path):
        super().__init__()

        self.project_path = project_path
        self.config_path = config_path

        self.current_results = []
        self.current_index = 0

        self.builder_thread = None
        self.build_data = None

        # Widgets
        self.camera_config_widget = CameraWidget(self)
        self.info_label = QtWidgets.QLabel(self)
        self.start_stop_button = QtWidgets.QPushButton('Inicio', self)
        

        # Initialize widgets
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.info_label.setStyleSheet('font-weight: bold')

        # Signals
        self.start_stop_button.clicked.connect(self.start_stop_handle)

        # Layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.camera_config_widget)


        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(self.start_stop_button)
        
        self.layout.addWidget(self.info_label)
        self.layout.addLayout(buttons_layout)
        
    @QtCore.Slot()


    @QtCore.Slot()
    def updateProcess(self):
        # Update firmware and wait
        self.info_label.setStyleSheet('color: ')
        self.info_label.setText("Building filesystem.")
        self.setEnabled(False)
        
        # Start building process
        self.builder_thread = FSBuilder(self.project_path, PLATFORM, self)
        self.builder_thread.exit_code.connect(self.handleBuildFSExit)
        self.builder_thread.start()

        
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
            self.info_label.setText("Building firmware")
            self.builder_thread.start()


    def updateInfoLabel(self, n_results):
        # Check if results where found
        self.info_label.setStyleSheet('color: ')
        if(n_results != 0):
            self.info_label.setText(f"{n_results} entries found!")
        else:
            self.info_label.setText("No entries found.")
            

    def handleJSON(self):
        with open(self.config_path, 'r') as json_file:
            json_data = json.load(json_file)
        
        # Main system parameters
        system_parameters = json_data[MAIN_KEY][SYS_KEY]
        # -> Update name
        system_parameters[THING_NAME_KEY] = self.camera_config_widget.getThingName()
        # -> ap password
        system_parameters[AP_PASS_KEY] = self.camera_config_widget.getAPPass()
        # -> Setup wifi
        system_parameters[WIFI_KEY][WIFI_SSID_KEY] = self.camera_config_widget.getWiFiSSID()
        system_parameters[WIFI_KEY][WIFI_PASS_KEY] = self.camera_config_widget.getWiFiPass()
        
        # Connection parameters
        conn_parameters = json_data[MAIN_KEY][CUSTOM_KEY][CONN_KEY]
        # -> Set static ip
        conn_parameters[IP_KEY] = self.camera_config_widget.getIP()
        conn_parameters[GATE_KEY] = self.camera_config_widget.getGateway()
        conn_parameters[MASK_KEY] = self.camera_config_widget.getNetmask()

        # Write onto the file
        json_obj = json.dumps(json_data, indent=4)
        with open(self.config_path, 'w') as out_json:
            out_json.write(json_obj)

    def start_stop_handle(self):
        self.handleJSON()
        self.updateProcess()