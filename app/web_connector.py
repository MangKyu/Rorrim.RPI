import requests
import urllib
from bs4 import BeautifulSoup
import os
import json

class WebConnector:

    def __init__(self):
        self.domain = "http://sd100.iptime.org:5000"

    def login(self, mirror_uid):
        url = self.domain + "/login"
        file = os.path.join('Files', 'test.jpg')
        data = {
            'mirror_uid': mirror_uid,
        }
        files = {
            'file_name':  open(file, 'rb')
        }
        req = requests.post(url=url, data=data, files=files)
        return req.json()

    def send_user_info(self, mirror_uid, user_uid):
        url = self.domain + "/sendUserInfo"
        user_dict ={
            'mirror_uid': mirror_uid,
            'user_uid': user_uid
        }
        req = requests.post(url=url, data=user_dict)

    def get_weather(self):
        url = self.domain + "/getWeather"
        res = requests.get(url)
        return res.json()

    def get_news(self, user_uid):
        url = self.domain + "/getNews"
        if user_uid is None:
            user_uid = "None"
        data_dict = {
            'uid': user_uid
        }
        req = requests.post(url=url, data=data_dict)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        link = soup.find_all("news")

        ret = []

        for i in link:
            ret.append([i.title.text, i.content.text])

        return ret

    def get_geocode(self, place):
        api_url = "https://maps.googleapis.com/maps/api/geocode/json?address="+place+"&key=AIzaSyAnuRGIRSK9MWOKjsKFvjvLrTOUyU7e9DU"
        req = requests.get(api_url)
        if req.status_code == 200:
            data = json.loads(req.text)
            if data is not None and data['results'] is not None:
                return data['results'][0]['geometry']['location']
        return None

    def get_location(self):
        location = ""

        req = requests.get("http://ipconfig.kr")
        html = req.text
        html = html[html.find("IP address : "):].splitlines()[0]
        html = html[html.find(": ") + 2:]
        html = html[html.find("red> ") + 5:html.find("</font>")]
        # print(html)

        info = {'query': html,  # target ip (my ip)
                'ip': html}  # my ip

        with requests.Session() as s:
            req = s.post('https://후이즈검색.한국/kor.whois.jsc', data=info)
            html = req.text
            html = html[html.rfind("[ 네트워크 할당 정보 ]"):]
            html = html[:html.find("우편번호")]
            html = html.splitlines()[-1]
            html = html[html.find(": ") + 2:]
            html = html.split(" ")
            for i in html:
                location = location + i + " "
                if i.endswith("구"):
                    break

        return location

    def get_playlist(self, mirror_uid, user_uid):
        url = self.domain + "/getPlayList?mirrorUid="+mirror_uid+"&uid="+user_uid
        req = requests.get(url)
        html = req.text
        data = json.loads(html)
        return data

    def get_name(self, user_uid):
        url = self.domain + "/getName?uid="+user_uid
        req = requests.get(url)
        html = req.text
        return html

    '''
    def get_music(self, mirror_uid, user_uid, fName):
        url = self.domain + "/getMusicFile?mirrorUid="+mirror_uid+"&uid="+user_uid+"&fileName="+fName
        if not os.path.exists('music'):
            os.mkdir('music')
        if not os.path.exists('music/'+user_uid):
            os.mkdir('music/'+user_uid)
        if os.path.exists('music/'+user_uid+"/"+fName):
            return
        f = open("music/"+user_uid+"/"+fName, 'wb')
        print("download start")
        req = requests.get(url)
        f.write(req.content)
        print("download ended")
        f.close()
        #html = req.text
        #print(html)
    '''

    def get_music(self, mirror_uid, user_uid, fName, playlist=None, playlist_hash=None):
        url = self.domain + "/getMusicFile?mirrorUid="+mirror_uid+"&uid="+user_uid+"&fileName="+fName
        if not os.path.exists('music'):
            os.mkdir('music')
        if not os.path.exists('music/'+user_uid):
            os.mkdir('music/'+user_uid)
        if os.path.exists('music/'+user_uid+'/'+fName):
            return
        print('download start')
        downloaded = 0
        req = requests.get(url, stream=True)
        with open('music/'+user_uid+'/'+fName, 'wb') as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
            f.close()
        print('download finish')
        if playlist is not None and playlist_hash is not None:
            playlist.append(fName)
            playlist_hash[fName] = True

if __name__ == "__main__":
    wc = WebConnector()
    mirror_uid = "rorrim1234567890"
    user_uid = "Xrb4lbiAAeUTiyMndUC1eLQWsKI3"
    wc.get_music(mirror_uid, user_uid, 'abc.mp3')
    #playlist = wc.get_playlist(mirror_uid, user_uid)
    #print(playlist)
    #wc.get_music(mirror_uid, user_uid, "test.mp3")
    #for i in playlist:
    #    wc.get_music(mirror_uid, user_uid, playlist[i])
