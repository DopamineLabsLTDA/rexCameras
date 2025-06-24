from PySide6 import QtCore
import subprocess
from .Common import CommonThread

class FSUpload(CommonThread):
    def run(self):
        # Upload the filesystem
        # platformio run --target uploadfs --environment esp32cam_ai_thinker 
        result_code = subprocess.run(
            [
                'pio',
                'run',
                '-d',
                self.path,
                '--target',
                'uploadfs',
                '--environment',
                self.platform
        ])
        self.exit_code.emit(result_code.returncode)