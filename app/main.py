import client_gui
from PyQt5.QtWidgets import *
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = app.desktop().screenGeometry()
    gui = client_gui.SmartMirrorGUI(screen.width(), screen.height())
    gui.show()
    app.exec_()
    
