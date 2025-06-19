from PySide6 import QtCore, QtWidgets, QtGui

class Entry(QtWidgets.QWidget):
    def __init__(self, updateFunction, parent=None):
        super().__init__(parent)
        
        # Widgets
        self.id_field = QtWidgets.QSpinBox(self)
        self.equipo_field = QtWidgets.QSpinBox(self)
        self.device_field = QtWidgets.QSpinBox(self)
        self.ip_field = QtWidgets.QLineEdit(self)
        self.sub_string = QtWidgets.QLineEdit(self)
        self.update_button = QtWidgets.QPushButton("Update", self)
        self.auto_patch = QtWidgets.QPushButton("Auto", self)


        # Signals
        self.update_button.clicked.connect(updateFunction)
        self.auto_patch.clicked.connect(self.fillSubString)

        # Layout
        self.layout = QtWidgets.QFormLayout(self)
        self.layout.addRow("ID:", self.id_field)
        self.layout.addRow("EQUIPO:", self.equipo_field)
        self.layout.addRow("DISPOSITIVO:", self.device_field)
        self.layout.addRow("IP:", self.ip_field)
        self.layout.addRow("SUBSTRING:", self.sub_string)
        # Lower controls
        lower_controls = QtWidgets.QHBoxLayout()
        lower_controls.addWidget(self.auto_patch)
        lower_controls.addWidget(self.update_button)
        
        self.layout.addRow(lower_controls)

    def fill(self, data, data_index):
        try:
            self.setEnabled(True)
            _id, _equipo, _device, _ip = data[data_index]
            self.id_field.setValue(_id)
            self.equipo_field.setValue(_equipo)
            self.device_field.setValue(_device)
            # Check if substring
            check_substring = _ip.split('/')
            if(len(check_substring) > 1):
                self.ip_field.setText(check_substring[0])
                self.sub_string.setText("/"+check_substring[1])
            else:
                self.ip_field.setText(_ip)
                self.sub_string.setText("")

        except:
            self.setEnabled(False)
            

    def serialize(self):
        _id = self.id_field.value()
        _equipo = self.equipo_field.value()
        _device = self.device_field.value()
        _ip = self.ip_field.text()
        _substring = self.sub_string.text()
        return (_id, _equipo, _device, _ip, _substring)
    
    @QtCore.Slot()
    def fillSubString(self):
        # Update field
        self.sub_string.setText("/stream")