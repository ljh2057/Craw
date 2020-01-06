from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot,QTimer
class BasePlugin(QThread):
    trigger = pyqtSignal()
    def __init__(self, state):
        super(BasePlugin, self).__init__()
        self.state = state
    def start(self):
        pass
    def stop(self):
        pass
