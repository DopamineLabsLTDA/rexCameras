from PySide6 import QtCore
import subprocess
from .Common import CommonThread

class Builder(CommonThread):
    def run(self):
        # Build the firmware
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