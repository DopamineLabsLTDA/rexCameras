from PySide6 import QtCore
import subprocess


class Builder(QtCore.QThread):
    exit_code = QtCore.Signal(int)

    def __init__(self, path, platform, parent=None):
        super().__init__(parent)
        self.path = path
        self.platform = platform
        
    def run(self):
        # Run the build
        result_code = subprocess.run(
            [
                'pio',
                'run',
                '-d',
                self.path,
                '-e',
                self.platform,
                '-t',
                'upload'
        ])
        self.exit_code.emit(result_code.returncode)