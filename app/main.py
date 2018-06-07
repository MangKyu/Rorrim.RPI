import client_gui
from PyQt5.QtWidgets import *
import sys
import threading
import time
import mirror


gui = None
'''
wc = None
def updateWeather():
    while True:
        try:
            weather_info = wc.get_weather()
            gui.setWeather(weather_info)
            time.sleep(300)
        except:
            pass

def updateNews():
    news = wc.get_news("world")
    index = 0
    while True:
        try:
            gui.setNews(news[index][0])
            index += 1
            if index >= len(news):
                # update news
                index = 0
            time.sleep(5)
        except:
            pass
'''

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mirror = mirror.Mirror(gui)
    screen = app.desktop().screenGeometry()
    gui = client_gui.SmartMirrorGUI(screen.width(), screen.height())

    '''
    wt_th = threading.Thread(target=updateWeather)
    wt_th.daemon = True
    wt_th.start()

    ns_th = threading.Thread(target=updateNews)
    ns_th.daemon = True
    ns_th.start()
    '''
    gui.setLocation(mirror.wc.get_location())
    gui.show()

    app.exec_()
