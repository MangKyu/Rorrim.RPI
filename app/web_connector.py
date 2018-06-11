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

    def get_mp3_file(self):
        url = self.domain + "/download_mp3_file/"
        fileName = 'a.mp3'
        path = 'C:/Users/jaewook/Desktop/'
        url_request = urllib.request.Request(url + fileName)
        url_connect = urllib.request.urlopen(url_request)
        with open(path + fileName, 'wb') as f:
            while True:
                buffer = url_connect.read(1024)
                if not buffer: break
                data_write = f.write(buffer)
        url_connect.close()

    def get_path(self, startX="126.9850380932383", startY="37.566567545861645", endX="127.10331814639885",
                 endY="37.403049076341794"):
        pass

