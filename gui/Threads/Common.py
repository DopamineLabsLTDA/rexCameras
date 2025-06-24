from PySide6 import QtCore
import subprocess


class CommonThread(QtCore.QThread):
    exit_code = QtCore.Signal(int)

    def __init__(self, path, platform, parent=None):
        super().__init__(parent)
        self.path = path
        self.platform = platform