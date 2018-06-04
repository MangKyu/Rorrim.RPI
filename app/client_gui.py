import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import datetime
import time
import threading
import web_connector
import ctypes

class SmartMirrorGUI(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.showFullScreen()
        self.setFixedSize(width, height)
        self.setWindowTitle('鏡:Rorrim')
        self.wc = web_connector.WebConnector()
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
        self.dt_th = threading.Thread(target=self.updateDatetime)
        self.dt_th.daemon = True
        self.dt_th.start()
        self.wt_th = threading.Thread(target=self.updateWeather)
        self.wt_th.daemon = True
        self.wt_th.start()
        self.ns_th = threading.Thread(target=self.updateNews)
        self.ns_th.daemon = True
        self.ns_th.start()

    def initSchedule(self):
        # get schedules from server or google calendar
        schedules = self.wc.get_schedule('A1rNcfWsplVW6SeK2gdclDZC2R12')

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
        self.news = self.wc.get_news("world")
        self.index = 1

        LB = QLabel(self.news[0][0])
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

        weather_info = self.wc.get_weather()

        if weather_info is None:
            return None

        dt = datetime.datetime.now()

        imgLB = QLabel()
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

        img.scaledToWidth(5, Qt.FastTransformation)
        img = img.scaledToWidth(self.width()/100*5)
        imgLB.setPixmap(img)
        imgLB.setFixedSize(img.width(), img.height())
        imgLB.move(self.width()/100*2, self.height()/100*1)
        imgLB.setAutoFillBackground(True)
        p = imgLB.palette()
        p.setColor(imgLB.backgroundRole(), Qt.black)
        imgLB.setPalette(p)
        imgLB.setAlignment(Qt.AlignCenter)

        tempLB = QLabel(str(weather_info['cur_tem'])+"˚C")
        tempLB.setStyleSheet('color: white')
        tempLB.setFont(QFont("", 30, QFont.Bold))
        tempLB.setFixedSize(self.width()/100*8, img.height())
        tempLB.move(self.width()/100*2+img.width(), self.height()/100*1)
        tempLB.setAutoFillBackground(True)
        p = tempLB.palette()
        p.setColor(tempLB.backgroundRole(), Qt.black)
        tempLB.setPalette(p)
        tempLB.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        loc = self.wc.get_location()
        locLB = QLabel(loc)
        locLB.setStyleSheet('color: white')
        locLB.setFont(QFont("", 20, QFont.Bold))
        locLB.setFixedSize(self.width()/100*20, self.height()/100*5)
        locLB.move(self.width()/100, self.height()/100*1+img.height())
        locLB.setAutoFillBackground(True)
        p = locLB.palette()
        p.setColor(locLB.backgroundRole(), Qt.black)
        locLB.setPalette(p)
        locLB.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        mmLB = QLabel("▲"+str(weather_info["max_tem"])[:-2]+"˚C ▼"+str(weather_info["min_tem"])[:-2]+"˚C")
        mmLB.setStyleSheet('color: white')
        mmLB.setFont(QFont("", 20, QFont.Bold))
        mmLB.setFixedSize(self.width()/100*20, self.height()/100*5)
        mmLB.move(self.width()/100, self.height()/100*7 + img.height())
        mmLB.setAutoFillBackground(True)
        p = mmLB.palette()
        p.setColor(mmLB.backgroundRole(), Qt.black)
        mmLB.setPalette(p)
        mmLB.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.imgLB = imgLB
        self.tempLB = tempLB
        self.mmLB = mmLB
        self.layout().addChildWidget(self.imgLB)
        self.layout().addChildWidget(self.tempLB)
        self.layout().addChildWidget(locLB)
        self.layout().addChildWidget(self.mmLB)


    def initMusic(self):
        # get music file or information

        self.playlist = self.wc.get_playlist()

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

    def updateWeather(self):
        while(True):
            try:
                time.sleep(300)
                weather_info = self.wc.get_weather()

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
                img = img.scaledToWidth(self.width() / 100 * 10)
                self.imgLB.setPixmap(img)

                self.tempLB = QLabel(str(weather_info['cur_tem'])+"˚C")
                self.mmLB = QLabel("▲"+weather_info["max_tem"][:-2]+"˚C ▼"+weather_info["min_tem"][:-2]+"˚C")
            except:
                break

    def updateNews(self):
        while(True):
            try:
                time.sleep(5)
                self.newsLB.setText(self.news[self.index][0])
                self.index += 1
                if self.index >= len(self.news):
                    #update news
                    self.index = 0
            except:
                break
