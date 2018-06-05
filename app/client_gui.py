import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import datetime
import time
import threading
from PyQt5 import QtWebEngineWidgets

class SmartMirrorGUI(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.showFullScreen()
        self.setFixedSize(width, height)
        self.setWindowTitle('鏡:Rorrim')
        self.playlist = []
        self.initUI()

    def closeEvent(self, event):
        self.deleteLater()

    def initUI(self):
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)
        vlayout = QVBoxLayout()
        self.setLayout(vlayout)
        self.initDatetime()
        self.initSchedule()
        self.initNews()
        self.initMusic()
        self.initWeather()
        self.initPath()
        self.dt_th = threading.Thread(target=self.updateDatetime)
        self.dt_th.daemon = True
        self.dt_th.start()

    def initPath(self):
        self.webView = QtWebEngineWidgets.QWebEngineView(self)
        self.webView.setUrl(QUrl("http://203.252.166.206:5000/getPath?startX=126.9850380932383&startY=37.566567545861645&endX=127.10331814639885&endY=37.403049076341794"))
        self.webView.setFixedSize(self.width()/3, self.width()/3)
        self.webView.move(self.width()/3*2, (self.height()-self.width()/3))
        self.layout().addChildWidget(self.webView)
        self.layout().removeWidget(self.webView)

    def initSchedule(self):
        # get schedules from server or google calendar
        schedules = []

        if schedules is not None:
            num_schedules = len(schedules)
        else:
            num_schedules = 0

        '''
        scheduleLB = []
        for i in range(num_schedules):
            LB = QLabel(schedules[i][0]+" "+schedules[i][1])
            LB.setStyleSheet('color: white')
            LB.setFont(QFont("", 25, QFont.Bold))
            LB.setFixedSize(self.width()/100*40, self.height()/100*6)
            LB.move(self.width()/100, self.height()/100*(94-(num_schedules-i)*6))
            LB.setAutoFillBackground(True)
            p = LB.palette()
            p.setColor(LB.backgroundRole(), Qt.black)
            LB.setPalette(p)
            LB.setAlignment(Qt.AlignVCenter)
            scheduleLB.append(LB)

        self.scheduleLB = scheduleLB
        for i in self.scheduleLB:
            self.layout().addChildWidget(i)
        '''

    def initNews(self):
        # get news from server

        LB = QLabel("")
        LB.setStyleSheet('color: white')
        LB.setFont(QFont("", 20, QFont.Bold))
        LB.setFixedSize(self.width(), self.height()/100*5)
        LB.move(self.width()/100, self.height()/100*94)
        LB.setAutoFillBackground(True)
        p = LB.palette()
        p.setColor(LB.backgroundRole(), Qt.black)
        LB.setPalette(p)
        LB.setAlignment(Qt.AlignVCenter)

        self.newsLB = LB
        self.layout().addChildWidget(self.newsLB)

    def initWeather(self):
        # get weather information from server or by using api

        #weather_info = self.wc.get_weather()

        #if weather_info is None:
        #    return None

        dt = datetime.datetime.now()

        self.imgLB = QLabel()
        img = QPixmap("weather_img/sunny-day.png")
        """
        if weather_info['cur_sky'] == "Sunny":
            if dt.hour >= 6 and dt.hour <= 20:
                img = QPixmap("weather_img/sunny-day.png")
            else:
                img = QPixmap("weather_img/sunny-night.png")
        elif weather_info['cur_sky'] == "Cloudy":
            if dt.hour >= 6 and dt.hour <= 20:
                img = QPixmap("weather_img/cloudy-day.png")
            else:
                img = QPixmap("weather_img/cloudy-night.png")
        elif weather_info['cur_sky'] == "Very Cloudy":
            img = QPixmap("weather_img/cloudy-many.png")
        elif weather_info['cur_sky'] == "Foggy":
            img = QPixmap("weather_img/cloudy-so-much.png")
        elif weather_info['cur_sky'] == "Rainy":
            img = QPixmap("weather_img/rainy.png")
        elif weather_info['cur_sky'] == "rain with snow":
            img = QPixmap("weather_img/rainy-snow.png")
        elif weather_info['cur_sky'] == "Snowy":
            img = QPixmap("weather_img/snow.png")
        """
        img.scaledToWidth(5, Qt.FastTransformation)
        img = img.scaledToWidth(self.width()/100*5)
        self.imgLB.setPixmap(img)
        self.imgLB.setFixedSize(img.width(), img.height())
        self.imgLB.move(self.width()/100*2, self.height()/100*1)
        self.imgLB.setAutoFillBackground(True)
        p = self.imgLB.palette()
        p.setColor(self.imgLB.backgroundRole(), Qt.black)
        self.imgLB.setPalette(p)
        self.imgLB.setAlignment(Qt.AlignCenter)

        self.tempLB = QLabel("")
        self.tempLB.setStyleSheet('color: white')
        self.tempLB.setFont(QFont("", 30, QFont.Bold))
        self.tempLB.setFixedSize(self.width()/100*8, img.height())
        self.tempLB.move(self.width()/100*2+img.width(), self.height()/100*1)
        self.tempLB.setAutoFillBackground(True)
        p = self.tempLB.palette()
        p.setColor(self.tempLB.backgroundRole(), Qt.black)
        self.tempLB.setPalette(p)
        self.tempLB.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        #loc = self.wc.get_location()
        #locLB = QLabel(loc)
        self.locLB = QLabel("")
        self.locLB.setStyleSheet('color: white')
        self.locLB.setFont(QFont("", 20, QFont.Bold))
        self.locLB.setFixedSize(self.width()/100*20, self.height()/100*5)
        self.locLB.move(self.width()/100, self.height()/100*1+img.height())
        self.locLB.setAutoFillBackground(True)
        p = self.locLB.palette()
        p.setColor(self.locLB.backgroundRole(), Qt.black)
        self.locLB.setPalette(p)
        self.locLB.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        #mmLB = QLabel("▲"+str(weather_info["max_tem"])[:-2]+"˚C ▼"+str(weather_info["min_tem"])[:-2]+"˚C")
        self.mmLB = QLabel("")
        self.mmLB.setStyleSheet('color: white')
        self.mmLB.setFont(QFont("", 20, QFont.Bold))
        self.mmLB.setFixedSize(self.width()/100*20, self.height()/100*5)
        self.mmLB.move(self.width()/100, self.height()/100*7 + img.height())
        self.mmLB.setAutoFillBackground(True)
        p = self.mmLB.palette()
        p.setColor(self.mmLB.backgroundRole(), Qt.black)
        self.mmLB.setPalette(p)
        self.mmLB.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.layout().addChildWidget(self.imgLB)
        self.layout().addChildWidget(self.tempLB)
        self.layout().addChildWidget(self.locLB)
        self.layout().addChildWidget(self.mmLB)


    def initMusic(self):
        # get music file or information

        #self.playlist = self.wc.get_playlist()
        self.playlist = []

        musicLB = []
        titleLB = QLabel("")
        if self.playlist is not None and len(self.playlist) > 0:
            titleLB.setText("♬ " + self.playlist[0][0])
        titleLB.setStyleSheet('color: white')
        titleLB.setFont(QFont("", 25, QFont.Bold))
        titleLB.setFixedSize(self.width()/100*30, self.height()/100*6)
        titleLB.move(self.width()/100*35, self.height()/100*3)
        titleLB.setAutoFillBackground(True)
        p = titleLB.palette()
        p.setColor(titleLB.backgroundRole(), Qt.black)
        titleLB.setPalette(p)
        titleLB.setAlignment(Qt.AlignHCenter)
        musicLB.append(titleLB)

        artistLB = QLabel("")
        if self.playlist is not None and len(self.playlist) > 0:
            artistLB.setText(self.playlist[0][1])
        artistLB.setStyleSheet('color: white')
        artistLB.setFont(QFont("", 22, QFont.Bold))
        artistLB.setFixedSize(self.width()/100*30, self.height()/100*6)
        artistLB.move(self.width()/100*35, self.height()/100*9)
        artistLB.setAutoFillBackground(True)
        p = artistLB.palette()
        p.setColor(artistLB.backgroundRole(), Qt.black)
        artistLB.setPalette(p)
        artistLB.setAlignment(Qt.AlignHCenter)
        musicLB.append(artistLB)

        self.musicLB = musicLB
        self.layout().addChildWidget(self.musicLB[0])
        self.layout().addChildWidget(self.musicLB[1])

    def initDatetime(self):
        dt = datetime.datetime.now()

        weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
        month = ["December", "January", "February", "March", "April", "May", "June", "July", "August", "September",
                 "October", "November", "December"]
        d = weekday[dt.weekday()] + ", " + month[dt.month] + " " + str(dt.day) + " " + str(dt.year)

        dateLB = QLabel(d)
        dateLB.setStyleSheet('color: white')
        dateLB.setFont(QFont("", 21, QFont.Bold))
        dateLB.setFixedSize(self.width()/100*33, self.height()/100*6)
        dateLB.move(self.width()/100*65, self.height()/100*3)
        dateLB.setAutoFillBackground(True)
        p = dateLB.palette()
        p.setColor(dateLB.backgroundRole(), Qt.black)
        dateLB.setPalette(p)
        dateLB.setAlignment(Qt.AlignRight)

        t = str(dt)[11:16]
        if dt.hour > 12:
            t = t + " PM"
        else:
            t = t + " AM"
        timeLB = QLabel(t)
        timeLB.setStyleSheet('color: white')
        timeLB.setFont(QFont("", 30, QFont.Bold))
        timeLB.setFixedSize(self.width()/100*33, self.height()/100*8)
        timeLB.move(self.width()/100*65, self.height()/100*9)
        timeLB.setAutoFillBackground(True)
        p = timeLB.palette()
        p.setColor(timeLB.backgroundRole(), Qt.black)
        timeLB.setPalette(p)
        timeLB.setAlignment(Qt.AlignRight | Qt.AlignTop)

        self.timeLB = timeLB
        self.dateLB = dateLB
        self.layout().addChildWidget(self.dateLB)
        self.layout().addChildWidget(self.timeLB)

    def setWeather(self, weather_info):
        if weather_info is None:
            return None

        dt = datetime.datetime.now()

        img = QPixmap("weather_img/sunny-day.png")

        if weather_info['cur_sky'] == "Sunny":
            if dt.hour >= 6 and dt.hour <= 20:
                img = QPixmap("weather_img/sunny-day.png")
            else:
                img = QPixmap("weather_img/sunny-night.png")
        elif weather_info['cur_sky'] == "Cloudy":
            if dt.hour >= 6 and dt.hour <= 20:
                img = QPixmap("weather_img/cloudy-day.png")
            else:
                img = QPixmap("weather_img/cloudy-night.png")
        elif weather_info['cur_sky'] == "Very Cloudy":
            img = QPixmap("weather_img/cloudy-many.png")
        elif weather_info['cur_sky'] == "Foggy":
            img = QPixmap("weather_img/cloudy-so-much.png")
        elif weather_info['cur_sky'] == "Rainy":
            img = QPixmap("weather_img/rainy.png")
        elif weather_info['cur_sky'] == "rain with snow":
            img = QPixmap("weather_img/rainy-snow.png")
        elif weather_info['cur_sky'] == "Snowy":
            img = QPixmap("weather_img/snow.png")

        img.scaledToWidth(10, Qt.FastTransformation)
        img = img.scaledToWidth(self.width() / 100 * 5)
        self.imgLB.setPixmap(img)

        self.tempLB.setText(str(weather_info['cur_tem']) + "˚C")
        self.mmLB.setText("▲" + str(weather_info["max_tem"])[:-2] + "˚C ▼" + str(weather_info["min_tem"])[:-2] + "˚C")

    def setLocation(self, loc):
        self.locLB.setText(loc)

    def setNews(self, text):
        self.newsLB.setText(text)

    def updateDatetime(self):
        while(True):
            try:
                dt = datetime.datetime.now()

                weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
                month = ["December", "January", "February", "March", "April", "May", "June", "July", "August", "September",
                         "October", "November", "December"]
                d = weekday[dt.weekday()] + ", " + month[dt.month] + " " + str(dt.day) + " " + str(dt.year)
                t = str(dt)[11:16]
                if dt.hour > 12:
                    t = t + " PM"
                else:
                    t = t + " AM"
                self.dateLB.setText(d)
                self.timeLB.setText(t)
                time.sleep(1)
            except:
                break
