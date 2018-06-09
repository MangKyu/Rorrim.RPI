import firebase_admin
from firebase_admin import credentials, db
import datetime

class FirebaseManager():

    def __init__(self, mirror_uid):
        cred = credentials.Certificate('Files/Auth/smartmirror-75b89-firebase-adminsdk-vx8is-56d6e1cacc.json')
        #default_app = firebase_admin.initialize_app(cred)
        firebase_admin.initialize_app(cred, {
            'databaseURL' : 'https://smartmirror-75b89.firebaseio.com'
        })
        self.root = db.reference().child(mirror_uid)
        self.weather = self.root.child('weather')

    def get_weather(self):
        weather_data = db.reference('weather'.format(self.weather.key)).get()
        return weather_data

    def get_playlist(self):
        playlist = []
        playlist.append(["What is Love?", "TWICE(트와이스)"])
        return playlist

    def get_schedule(self, uid=None, date=None):
        if uid is None:
            return None
        if date is not None:
            sch = self.root.child('user').child(uid).child('calendar').child(date)
            return sch.get()
        dt = datetime.datetime.now()
        year = str(dt.year)
        month = str(dt.month)
        if len(month) == 1:
            month = "0" + month
        day = str(dt.day)
        if len(day) == 1:
            day = "0" + day
        sch = self.root.child('user').child(uid).child('calendar').child(year+"-"+month+"-"+day)
        return sch.get()

    def get_onoff(self, uid=None):
        if uid is None:
            return None
        onoff = self.root.child('user').child(uid).child('status')
        return onoff.get()
