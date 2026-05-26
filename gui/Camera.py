from PySide6 import QtWidgets

class CameraWidget(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Camera configurations", parent)

        # Widgets
        self.thing_name = QtWidgets.QLineEdit(self)
        self.ap_password = QtWidgets.QLineEdit(self)
        self.ssid = QtWidgets.QLineEdit(self)
        self.password = QtWidgets.QLineEdit(self)
        self.ip = QtWidgets.QLineEdit(self)
        self.gateway = QtWidgets.QLineEdit(self)
        self.netmask = QtWidgets.QLineEdit(self)

        # Signals


        # Layout
        layout = QtWidgets.QFormLayout()
        layout.addRow("Thing Name: ", self.thing_name)
        layout.addRow("AP Password: ", self.ap_password)
        layout.addRow("WiFi SSID: ", self.ssid)
        layout.addRow("WiFi Password: ", self.password)
        layout.addRow("IP: ", self.ip)
        layout.addRow("Gateway: ", self.gateway)
        layout.addRow("Netmask: ", self.netmask)
        self.setLayout(layout)
        

