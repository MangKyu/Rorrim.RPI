import threading
from app import web_connector
from app import firebase_manager


class Mirror(threading.Thread):
    def __int__(self):
        threading.Thread.__init__(self)
        self.mirror_uid = "rorrim1234567890"
        self.wc = web_connector.WebConnector(self.mirror_uid)
        self.fm = firebase_manager.FirebaseManager(self.mirror_uid)

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

