import client_gui
from PyQt5.QtWidgets import *
import sys
import threading
import time
import mirror

if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = app.desktop().screenGeometry()
    gui = client_gui.SmartMirrorGUI(screen.width(), screen.height())
    mirror = mirror.Mirror(gui)

    gui.setLocation(mirror.wc.get_location())
    gui.show()
    app.exec_()
