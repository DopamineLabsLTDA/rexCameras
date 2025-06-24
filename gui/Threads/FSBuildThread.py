from PySide6 import QtCore
import subprocess
from .Common import CommonThread

class FSBuilder(CommonThread):
    def run(self):
        # Build the filesystem
        # platformio run --target buildfs --environment esp32cam_ai_thinker
        result_code = subprocess.run(
            [
                'pio',
                'run',
                '-d',
                self.path,
                '--target',
                'buildfs',
                '--environment',
                self.platform
        ])
        self.exit_code.emit(result_code.returncode)