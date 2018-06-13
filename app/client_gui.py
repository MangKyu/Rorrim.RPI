import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebKitWidgets import *
import datetime
import time
import threading
import ast
#from PyQt5.QtWebEngineWidgets import *
#from PyQt5 import QtWebEngineWidgets

class SmartMirrorGUI(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.startX = ""
        self.startY = ""
        self.endX = ""
        self.endY = ""
        self.webView = None
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
        self.initInfo()
        self.initDatetime()
        self.initSchedule()
        self.initNews()
        self.initMusic()
        self.initWeather()
        self.initPath()
        self.dt_th = threading.Thread(target=self.updateDatetime)
        self.dt_th.daemon = True
        self.dt_th.start()

    def initInfo(self):
        #self.infoLB = QLabel("Welcome, I'm Rorrim")
        self.infoLB = QLabel("")
        self.infoLB.setStyleSheet('color: white')
        self.infoLB.setFont(QFont("", 45, QFont.Bold))
        self.infoLB.setFixedSize(self.width(), self.height()/100*30)
        self.infoLB.move(self.width()/100*0, self.height()/100*35)
        self.infoLB.setAutoFillBackground(True)
        p = self.infoLB.palette()
        p.setColor(self.infoLB.backgroundRole(), Qt.black)
        self.infoLB.setPalette(p)
        self.infoLB.setAlignment(Qt.AlignCenter)
        self.layout().addChildWidget(self.infoLB)
        self.infoLB.setVisible(True)

    def setInfo(self, info_num, text=None):
        if info_num == 0:
            self.infoLB.setText("")
        elif info_num == 1:   #welcome
            #self.infoLB.setText("Welcome, I'm Rorrim")
            self.infoLB.setText(text)
        elif info_num == 2: #trying to login
            self.infoLB.setText("얼굴인식 시도 중")
        elif info_num == 3: #login success
            self.infoLB.setText(text+", 안녕하세요")
        elif info_num == 4:
            self.infoLB.setText(text+", 안녕히 가세요")
        elif info_num == 5:
            self.infoLB.setText("길찾기 시도 중: "+text)
        elif info_num == 6:
            self.infoLB.setText("길찾기 완료")
        elif info_num == 7:
            self.infoLB.setText("길찾기 정보 없음")
        elif info_num == 8:
            self.infoLB.setText("로그인 실패")

    def initPath(self):
        self.webView = QWebView(self)
        self.webView.setUrl(QUrl("http://sd100.iptime.org:5000/getPath"))
        self.webView.page().mainFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)
        self.webView.page().mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        self.webView.setFixedSize(self.width()/100*26, self.width()/100*26)
        self.webView.setZoomFactor(self.webView.width()/500)
        self.webView.move(self.width()-self.webView.width(), self.height()-self.webView.height())
        self.layout().addChildWidget(self.webView)
        self.webView.setVisible(True)
        self.sld = QSlider()
        self.sldvalue = 1
        self.sld.setValue(self.sldvalue)
        self.sld.valueChanged.connect(self.getPath)

    def setStartPoint(self, point):
        self.startX = point['longitude']
        self.startY = point['latitude']

    def initSchedule(self):
        # get schedules from server or google calendar
        self.scheLB = QLabel("")
        self.scheLB.setStyleSheet('color: white')
        self.scheLB.setFont(QFont("", 20, QFont.Bold))
        self.scheLB.setFixedSize(self.width()/100*40, self.height()/100*18)
        self.scheLB.move(self.width()/100, self.height()/100*78)
        self.scheLB.setAutoFillBackground(True)
        p = self.scheLB.palette()
        p.setColor(self.scheLB.backgroundRole(), Qt.black)
        self.scheLB.setPalette(p)
        self.scheLB.setAlignment(Qt.AlignVCenter)
        self.layout().addChildWidget(self.scheLB)
        self.scheLB.setVisible(False)

    def controlView(self, alarm_dict):
        activity = list(alarm_dict.keys())[0]
        flag = self.str_to_bool(alarm_dict[activity])
        # We have to do => set label enable, disable
        if activity == 'NewsActivity':
            self.newsLB.setVisible(flag)
        elif activity == 'CalendarActivity':
            self.scheLB.setVisible(flag)
        elif activity == 'PathActivity':
            if self.webView is not None:
                self.webView.setVisible(flag)
        elif activity == 'MusicActivity':
            self.musicLB.setVisible(flag)
        elif activity == 'WeatherActivity':
            self.weatherWidget.setVisible(flag)
        else:
            pass

    def str_to_bool(self, str):
        if str == 'true':
            return True
        elif str == 'false' or 'False':
            return False
        else:
            return True

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

        #if weather_info is None:
        #    return None

        dt = datetime.datetime.now()

        self.weatherWidget = QWidget()
        vlayout = QVBoxLayout()
        self.weatherWidget.setLayout(vlayout)

        self.imgLB = QLabel()
        img = QPixmap("weather_img/sunny-day.png")
        img.scaledToWidth(self.width()/100*7, Qt.FastTransformation)
        img = img.scaledToWidth(self.width()/100*7, Qt.FastTransformation)
        self.imgLB.setPixmap(img)
        self.imgLB.setFixedSize(img.width(), img.height())
        self.imgLB.move(self.width()/100*1, self.height()/100*1)
        self.imgLB.setAutoFillBackground(True)
        p = self.imgLB.palette()
        p.setColor(self.imgLB.backgroundRole(), Qt.black)
        self.imgLB.setPalette(p)
        self.imgLB.setAlignment(Qt.AlignVCenter)

        self.tempLB = QLabel("")
        self.tempLB.setStyleSheet('color: white')
        self.tempLB.setFont(QFont("", 35, QFont.Bold))
        self.tempLB.setFixedSize(self.width()/100*10, img.height())
        self.tempLB.move(self.width()/100*1+img.width(), self.height()/100*1)
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
        self.locLB.move(self.width()/100*1, self.height()/100*1+img.height())
        self.locLB.setAutoFillBackground(True)
        p = self.locLB.palette()
        p.setColor(self.locLB.backgroundRole(), Qt.black)
        self.locLB.setPalette(p)
        self.locLB.setAlignment(Qt.AlignVCenter)

        #mmLB = QLabel("▲"+str(weather_info["max_tem"])[:-2]+"˚C ▼"+str(weather_info["min_tem"])[:-2]+"˚C")
        self.mmLB = QLabel("")
        self.mmLB.setStyleSheet('color: white')
        self.mmLB.setFont(QFont("", 20, QFont.Bold))
        self.mmLB.setFixedSize(self.width()/100*20, self.height()/100*5)
        self.mmLB.move(self.width()/100*1, self.height()/100*7 + img.height())
        self.mmLB.setAutoFillBackground(True)
        p = self.mmLB.palette()
        p.setColor(self.mmLB.backgroundRole(), Qt.black)
        self.mmLB.setPalette(p)
        self.mmLB.setAlignment(Qt.AlignVCenter)

        self.weatherWidget.layout().addChildWidget(self.imgLB)
        self.weatherWidget.layout().addChildWidget(self.tempLB)
        self.weatherWidget.layout().addChildWidget(self.locLB)
        self.weatherWidget.layout().addChildWidget(self.mmLB)
        self.layout().addChildWidget(self.weatherWidget)

    def initMusic(self):
        # get music file or information

        #self.playlist = self.wc.get_playlist()
        musicLB = QLabel("")
        musicLB.setStyleSheet('color: white')
        musicLB.setFont(QFont("", 25, QFont.Bold))
        musicLB.setFixedSize(self.width()/100*54, self.height()/100*12)
        musicLB.move(self.width()/100*23, self.height()/100*3)
        musicLB.setAutoFillBackground(True)
        p = musicLB.palette()
        p.setColor(musicLB.backgroundRole(), Qt.black)
        musicLB.setPalette(p)
        musicLB.setAlignment(Qt.AlignVCenter)

        self.musicLB = musicLB
        self.layout().addChildWidget(self.musicLB)
        self.musicLB.setVisible(False)

    def initDatetime(self):
        dt = datetime.datetime.now()

        weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
        month = ["December", "January", "February", "March", "April", "May", "June", "July", "August", "September",
                 "October", "November", "December"]
        d = month[dt.month] + " " + str(dt.day) + " " + str(dt.year)

        dateLB = QLabel(d)
        dateLB.setStyleSheet('color: white')
        dateLB.setFont(QFont("", 21, QFont.Bold))
        dateLB.setFixedSize(self.width()/100*20, self.height()/100*6)
        dateLB.move(self.width()/100*78, self.height()/100*3)
        dateLB.setAutoFillBackground(True)
        p = dateLB.palette()
        p.setColor(dateLB.backgroundRole(), Qt.black)
        dateLB.setPalette(p)
        dateLB.setAlignment(Qt.AlignRight)

        weekLB = QLabel(weekday[dt.weekday()])
        weekLB.setStyleSheet('color: white')
        weekLB.setFont(QFont("", 21, QFont.Bold))
        weekLB.setFixedSize(self.width()/100*20, self.height()/100*6)
        weekLB.move(self.width()/100*78, self.height()/100*9)
        weekLB.setAutoFillBackground(True)
        p = weekLB.palette()
        p.setColor(weekLB.backgroundRole(), Qt.black)
        weekLB.setPalette(p)
        weekLB.setAlignment(Qt.AlignRight)

        t = str(dt)[11:16]
        if dt.hour > 12:
            t = t + " PM"
        else:
            t = t + " AM"
        timeLB = QLabel(t)
        timeLB.setStyleSheet('color: white')
        timeLB.setFont(QFont("", 30, QFont.Bold))
        timeLB.setFixedSize(self.width()/100*20, self.height()/100*8)
        timeLB.move(self.width()/100*78, self.height()/100*15)
        timeLB.setAutoFillBackground(True)
        p = timeLB.palette()
        p.setColor(timeLB.backgroundRole(), Qt.black)
        timeLB.setPalette(p)
        timeLB.setAlignment(Qt.AlignRight | Qt.AlignTop)

        self.timeLB = timeLB
        self.weekLB = weekLB
        self.dateLB = dateLB
        self.layout().addChildWidget(self.dateLB)
        self.layout().addChildWidget(self.weekLB)
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

        img.scaledToWidth(7, Qt.FastTransformation)
        img = img.scaledToWidth(self.width() / 100 * 7, Qt.FastTransformation)
        self.imgLB.setPixmap(img)

        self.tempLB.setText(str(weather_info['cur_tem']) + "˚C")
        self.mmLB.setText("▲" + str(weather_info["max_tem"])[:-2] + "˚C ▼" + str(weather_info["min_tem"])[:-2] + "˚C")

    def setLocation(self, loc):
        self.locLB.setText(loc)

    def setNews(self, text):
        self.newsLB.setText(text)

    def setMusic(self, music):
        self.musicLB.setText(music)
        self.musicLB.setVisible(True)

    def setSchedule(self, schedules):
        sche = ""
        if schedules is not None:
            schedules = sorted(schedules.items())
            dt = datetime.datetime.now()

            for i in range(len(schedules)):
                if int(schedules[i][0][:2]+schedules[i][0][3:]) >= dt.hour*100+dt.minute:
                    schedules = schedules[i:]
                    break
            length = len(schedules)

            for i in range(3-length):
                sche += '\n'

            if length > 3:
                length = 3
            for i in range(length):
                sche += (str(schedules[i][0]) + " " + str(schedules[i][1]) + '\n')

        self.scheLB.setText(sche)

    def updateDatetime(self):
        while(True):
            try:
                dt = datetime.datetime.now()

                weekday = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
                month = ["December", "January", "February", "March", "April", "May", "June", "July", "August", "September",
                         "October", "November", "December"]
                d = month[dt.month] + " " + str(dt.day) + " " + str(dt.year)
                t = str(dt)[11:16]
                if dt.hour > 12:
                    t = t + " PM"
                else:
                    t = t + " AM"
                self.dateLB.setText(d)
                self.weekLB.setText(weekday[dt.weekday()])
                self.timeLB.setText(t)
                time.sleep(1)
            except:
                break

    def setPath(self, point):
        self.endY = point['lat']
        self.endX = point['lng']
        self.sldvalue += 1
        if self.sldvalue == 100:
            sldvalue = 1
        self.sld.setValue(self.sldvalue)

    def getPath(self):
        self.webView.setUrl(QUrl("http://sd100.iptime.org:5000/getPath?startX="+str(self.startX)+"&startY="+str(self.startY)+"&endX="+str(self.endX)+"&endY="+str(self.endY)))
        self.webView.setVisible(True)

