import threading
import web_connector
import firebase_manager
import socket

class Mirror(threading.Thread):
    def __init__(self, gui):
        threading.Thread.__init__(self)
        self.gui = gui
        self.mirror_uid = "rorrim1234567890"#str("rorrim1234567890")
        self.wc = web_connector.WebConnector()
        self.fm = firebase_manager.FirebaseManager(self.mirror_uid)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

        recv_th = threading.Thread(target=self.receive_msg)
        recv_th.daemon = True
        recv_th.start()

    def connect(self):
        host = "203.252.166.206"
        port = 8099
        self.sock.connect((host, port))
        self.send_msg(self.mirror_uid)
        print("Connect to Server Complete")

    def send_msg(self, msg):
        msg = msg.encode('utf-8')
        self.sock.send(msg)

    def receive_msg(self):
        while True:
            msg_dict = self.sock.recv(4096).decode('utf-8')
            msg_protocol = msg_dict['MSG']
            if msg_protocol is '/WEATHER':
                self.gui.setWeather(msg_dict['DATA'])
            elif msg_protocol is 'NEWS':
                pass
                #self.gui.set_weather


    def get_weather(self):
        '''
        url = self.domain + "/get_weather"
        req = requests.get(url)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        link = soup.findChildren()

        ret = {}
        for i in link:
            ret[i.name] = i.text
        '''
        return self.fm.get_weather()

    def get_playlist(self):
        playlist = []
        playlist.append(["What is Love?", "TWICE(트와이스)"])
        return self.fm.get_playlist()

    def get_schedule(self, uid=None):
        schedules = self.fm.get_schedule(uid, "2018-06-05")
        return schedules

