import client_gui
from PyQt5.QtWidgets import *
import sys
#from app import gui,app
#from app import people_catcher as pc
#import threading

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = client_gui.SmartMirrorGUI()
    gui.show()
    app.exec_()
    '''
    th = threading.Thread(target=pc.catchPeople())
    th.daemon = True
    th.start()
    '''
