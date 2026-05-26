from PySide6 import QtWidgets

class PlatformWidget(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Platform configurations", parent)

        # Widgets
        self.platform_selector = QtWidgets.QComboBox(parent)
        self.motor_enable = QtWidgets.QRadioButton(parent)

        # Init
        self.platform_selector.addItems(["WOW", "TESTING"])
        # Signals


        # Layout
        layout = QtWidgets.QFormLayout()
        layout.addRow("Select platform: ", self.platform_selector)
        layout.addRow("Enable motor: ", self.motor_enable)
        self.setLayout(layout)