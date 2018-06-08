import threading
import web_connector
import firebase_manager
import socket
import time
import json

class Mirror(threading.Thread):
    def __init__(self, gui):
        threading.Thread.__init__(self)
        self.mirror_uid = "rorrim1234567890"
        self.gui = gui
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # we have to do => first, user_id should be none and display data and after login we have to set user_uid
        self.user_uid = "A1rNcfWsplVW6SeK2gdclDZC2R12"

        # we have to do => after login, socket connect should start
        self.connect()

        self.wc = web_connector.WebConnector()
        self.news = self.wc.get_news(self.user_uid)
        self.init_pi()

    def login(self):
        # we have to do => after we get sound data, request login and send face data with user data
        self.wc.send_user_info(self.mirror_uid, self.user_uid)

    def connect(self):
        #host = '192.168.0.126'
        #host = "172.16.28.163"
        host = "203.252.166.206"
        port = 8099
        self.sock.connect((host, port))
        msg_dict = self.create_dict('/MUID', self.mirror_uid)
        self.send_msg(msg_dict)
        print("Connect to Server Complete")

    def init_pi(self):
        self.login()
        weather_data = self.wc.get_weather()
        self.gui.setWeather(weather_data)

        news_th = threading.Thread(target=self.update_news)
        news_th.daemon = True
        news_th.start()

        # we have to do => after login start threading
        recv_th = threading.Thread(target=self.receive_msg)
        recv_th.daemon = True
        recv_th.start()

    def create_dict(self, head, body):
        msg_dict = {
            'HEAD': head,
            'BODY': body,
        }
        return msg_dict

    def update_news(self):
        index = 0
        while True:
            try:
                self.gui.setNews(self.news[index][0])
                index += 1
                if index >= len(self.news):
                    index = 0
                time.sleep(5)
            except:
                pass

    def send_msg(self, msg):
        # send only dictionary format data
        msg = json.dumps(msg)
        msg = msg.encode('utf-8')
        self.sock.send(msg)

    def receive_msg(self):
        while True:
            head, body = self.analyze_msg()
            print(head)
            print(body)
            if head == '/WEATHER':
                self.gui.setWeather(body)
            elif head == '/NEWS':
                self.news = self.wc.get_news(self.user_uid)
            elif head == '/SWITCH':
                self.gui.controlView(body)


    def analyze_msg(self):
        try:
            msg = self.sock.recv(4096)
            msg = msg.decode('utf-8')
            msg_dict = json.loads(msg)
            return msg_dict['HEAD'], msg_dict['BODY']
        except Exception as e:
            # we have to do => here means server socket closed so stop pi or restart pi
            print('Web Server Error')
            print(e)
            pass

    def get_playlist(self):
        # we have to do  => we have to set playlist
        playlist = []
        playlist.append(["What is Love?", "TWICE(트와이스)"])
        #return self.fm.get_playlist()

    def get_schedule(self, uid=None):
        # we have to do  => we have to set schedule
        #schedules = self.fm.get_schedule(uid, "2018-06-05")
        #return schedules
        pass
