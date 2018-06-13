import threading
import web_connector
import firebase_manager
import socket
import time
import json
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from speech import MicrophoneStream as microphone_stream
import re
import sys
import cv2
import numpy as np
import os
import eyed3, pygame
import random

font = cv2.FONT_HERSHEY_SIMPLEX

class Mirror():

    def __init__(self, gui):
        self.mirror_uid = "rorrim1234567890"
        self.gui = gui
        self.flag = True
        self.cam_flag = False
        self.auth_flag = False
        self.timer_flag = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        speech_th = threading.Thread(target=self.listening)
        speech_th.daemon = True
        speech_th.start()
        pygame.mixer.init()
        # we have to do => after login, socket connect should start
        self.connect()
        self.user_uid = None
        self.user_name = ""
        self.sem = None
        self.playlist = []
        self.playlist_hash = {}
        self.now_playing = ""
        self.music_th = None
        self.music_flag = False
        self.music_next = False
        self.wc = web_connector.WebConnector()
        self.fm = firebase_manager.FirebaseManager(self.mirror_uid)
        self.news = self.wc.get_news(self.user_uid)
        self.init_pi()

    def connect(self):
        #host = "172.16.28.163"
        host = "sd100.iptime.org"
        port = 8099
        self.sock.connect((host, port))
        msg_dict = self.create_dict('/MUID', self.mirror_uid)
        self.send_msg(msg_dict)
        print("Connect to Server Complete")

    def init_pi(self):
        #self.login()
        weather_data = self.wc.get_weather()
        self.gui.setWeather(weather_data)

        news_th = threading.Thread(target=self.update_news)
        news_th.daemon = True
        news_th.start()

        # we have to do => after login start threading
        recv_th = threading.Thread(target=self.receive_msg)
        recv_th.daemon = True
        recv_th.start()

        face_th = threading.Thread(target=self.face_detecting)
        face_th.daemon = True
        face_th.start()

        self.sem = threading.Semaphore(0)

    def create_dict(self, head, body):
        msg_dict = {
            'HEAD': head,
            'BODY': body,
        }
        return msg_dict

    def update_news(self):
        index = 0
        while self.flag:
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
        while self.flag:
            data = self.analyze_msg()
            if data is not None:
                head, body = data
                print(head)
                print(body)
                if head == '/WEATHER':
                    self.gui.setWeather(body)
                elif head == '/NEWS':
                    self.news = self.wc.get_news(self.user_uid)
                elif head == '/SWITCH':
                    self.gui.controlView(body)
                elif head =='/AUTH':
                    self.auth_flag = False
                    self.timer_flag = True
                    auth_dict = self.authenticate()
                    self.send_msg(auth_dict)
                    print('send auth to server')
                    print(self.auth_flag)
                # we have to do => show auth view
                elif head =='/PLAYLIST':
                    if list(body.keys())[0] == "remove":
                        if os.path.exists('music/'+self.user_uid+"/"+list(body.values())[0]):
                            if list(body.values())[0] == self.now_playing:
                                self.music_next = True
                                time.sleep(0.5)
                            os.remove('music/'+self.user_uid+"/"+list(body.values())[0])
                            if list(body.values())[0] in self.playlist:
                                self.playlist.remove(list(body.values())[0])
                                self.playlist_hash[list(body.values())[0]] = False
                            #self.playlist = self.wc.get_playlist(self.mirror_uid, self.user_uid)
                            #self.playlist = sorted(list(self.playlist.values()))
                            #self.playlist_hash = {}
                            #for i in self.playlist:
                            #    self.playlist_hash[i] = True
                            #self.playlist.remove(self.playlist.index(list(body.values())[0]))
                            #self.playlist_hash[list(body.values())[0]] = False
                            print(self.playlist)
                            print(self.playlist_hash)
                    elif list(body.keys())[0] == "update":
                        th = threading.Thread(target=self.wc.get_music, args=(self.mirror_uid, self.user_uid, list(body.values())[0], self.playlist, self.playlist_hash))
                        #th = threading.Thread(target=self.playlist_init)
                        th.daemon = True
                        th.start()
                else:
                    pass

    def authenticate(self):
        start = time.time()
        while self.timer_flag:
            end = time.time()
            if end - start >= 10:
                self.timer_flag = False
        auth_dict=self.create_dict('/AUTH', self.auth_flag)
        return auth_dict
            

    def analyze_msg(self):
        try:
            msg = self.sock.recv(4096)
            msg = msg.decode('utf-8')
            msg_dict = json.loads(msg)
            return msg_dict['HEAD'], msg_dict['BODY']
        except Exception as e:
            # we have to do => here means server socket closed so stop pi or restart pi
            self.flag = False
            print('Web Server Error')
            print(e)
            pass

    def login_request(self):
        user_uid = self.wc.login(self.mirror_uid)
        #user_uid = 'Xrb4lbiAAeUTiyMndUC1eLQWsKI3'
        return user_uid

    def login_success(self):
        self.wc.send_user_info(self.mirror_uid, self.user_uid)
        loc = self.fm.get_location(self.user_uid)
        if loc is not None:
            self.gui.setStartPoint(loc)
        sche = self.fm.get_schedule(self.user_uid, None)
        self.gui.setSchedule(sche)
        pl_th = threading.Thread(target=self.playlist_init)
        pl_th.daemon = True
        pl_th.start()
        
        onoff = self.fm.get_onoff(self.user_uid)
        if onoff is None or type(onoff) is not dict:
            print("onoff : ", end="")
            print(onoff)
            return
        for key in onoff:
            self.gui.controlView({key:onoff[key]})

    def playlist_init(self):
        print('playlist init() start')
        self.playlist = self.wc.get_playlist(self.mirror_uid, self.user_uid)
        self.playlist_hash = {}
        if self.playlist is not None:
            self.playlist = sorted(list(self.playlist.values()))
            for i in self.playlist:
                self.wc.get_music(self.mirror_uid, self.user_uid, i)
                self.playlist_hash[i] = True
        if os.path.exists('music/'+self.user_uid):
            children = os.listdir('music/'+self.user_uid)
            for i in children:
                if not (i in self.playlist):
                    os.remove('music/'+self.user_uid+'/'+i)
        print('playlist init() finished')

    def sign_out(self):
        # we have to do here => set everything false
        self.user_uid = None
        self.wc.send_user_info(self.mirror_uid, None)
        self.gui.controlView({"NewsActivity":"true"})
        self.gui.controlView({"PathActivity":"false"})
        self.gui.controlView({"WeatherActivity":"true"})
        self.gui.controlView({"CalendarActivity":"false"})
        self.gui.controlView({"MusicActivity":"false"})

    def get_playlist(self):
        # we have to do  => we have to set playlist
        playlist = []
        playlist.append(["What is Love?", "TWICE(트와이스)"])
        #return self.fm.get_playlist()

    def play_music(self):
        while self.music_flag:
            for i in self.playlist:
                print(i)
                if i in list(self.playlist_hash.keys()) and self.playlist_hash[i] and self.music_flag:
                    pygame.mixer.music.load('music/'+self.user_uid+'/'+i)
                    pygame.mixer.music.play(0)
                    self.now_playing = i
                    self.gui.setMusic(i)
                    af = eyed3.load('music/'+self.user_uid+'/'+i)
                    duration = af.info.time_secs
                    start_time = time.time()
                    while start_time+duration >= time.time() and self.music_flag:
                        if self.music_next:
                            self.music_next = False
                            break
                    pygame.mixer.music.stop()
                elif not self.music_flag:
                    break
        self.gui.setMusic("")

    def get_schedule(self, uid=None):
        schedules = self.fm.get_schedule(self.user_uid)
        return schedules

    def voice_response(self, msg=None):
        if msg is None:
            return
        self.gui.setInfo(1, msg);
        time.sleep(2.5)
        self.gui.setInfo(0)

    def listen_print_loop(self, responses):
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript

            overwrite_chars = ' ' * (num_chars_printed - len(transcript))

            if not result.is_final:  # print string #
                sys.stdout.write(transcript + overwrite_chars + '\r')
                sys.stdout.flush()

                num_chars_printed = len(transcript)

            else:
                print(transcript + overwrite_chars)

                if self.flag is False:
                    return "EXIT"
                    break
                elif re.search(r'\b안녕\b', transcript, re.I):
                    self.voice_response("안녕하세요")
                elif re.search(r'\b사랑해\b', transcript, re.I):
                    self.voice_response("저두요")
                elif re.search(r'\b배고파\b', transcript, re.I):
                    r = random.randint(0,100)
                    food = ""
                    if r <= 10:
                        self.voice_response("다이어트나 하세요!")
                    else:
                        if r <= 20:
                            food = "치킨"
                        elif r <= 30:
                            food = "피자"
                        elif r <= 40:
                            food = "햄버거"
                        elif r <= 50:
                            food = "떡볶이"
                        elif r <= 60:
                            food = "족발"
                        elif r <= 70:
                            food = "스테이크"
                        elif r <= 80:
                            food = "짜장면"
                        elif r <= 90:
                            food = "카레"
                        else:
                            food = "라멘"
                        self.voice_response(food+" 어때요?")
                elif re.search(r'\b로그인\b', transcript, re.I) and self.user_uid is None:
                    self.cam_flag = True
                    self.gui.setInfo(2)
                    self.sem.acquire()
                    self.user_uid = self.login_request()
                    if self.user_uid is not None:
                        self.user_name = self.wc.get_name(self.user_uid)
                        self.gui.setInfo(3,self.user_name)
                        self.login_success()
                        time.sleep(1)
                        self.gui.setInfo(0)
                    else:
                        self.sem.release()
                        self.gui.setInfo(8)
                        self.cam_flag = False
                        time.sleep(2)
                        self.gui.setInfo(0)
                elif re.search(r'\b로그아웃\b', transcript, re.I) and self.user_uid is not None:
                    self.gui.setInfo(4,self.user_name)
                    self.sign_out()
                    time.sleep(2)
                    self.user_name = ""
                    self.gui.setInfo(0)
                elif re.search(r'\b노래 틀어\b', transcript, re.I) or re.search(r'\b노래 재생\b',transcript, re.I) or re.search(r'\b노래 켜\b',transcript,re.I) or re.search(r'\b노래 시작\b', transcript, re.I):
                    # we have to do => play music
                    if not self.music_flag and self.playlist_hash is not None and len(self.playlist_hash) > 0:
                        self.music_flag = True
                        self.music_th = threading.Thread(target=self.play_music)
                        self.music_th.daemon = True
                        self.music_th.start()
                elif re.search(r'\b노래 꺼\b', transcript, re.I) or re.search(r'\b노래 그만\b', transcript, re.I) or re.search(r'\b노래 종료\b', transcript, re.I) or re.search(r'\b노래 정지\b', transcript, re.I):
                    if self.music_flag:
                        self.music_flag = False
                        pygame.mixer.stop()
                        self.gui.setMusic("")
                elif re.search(r'\b다음 곡\b', transcript, re.I) or re.search(r'\b다음 노래\b', transcript, re.I):
                    # we have to do => play music
                    if self.music_flag:
                        self.music_next = True
                elif re.search(r'\b가는 길\b', transcript, re.I) or re.search(r'\b가는길\b', transcript, re.I) or re.search(r'\b가는 방법\b', transcript, re.I):
                    place = transcript[:re.search(r'\b가는\b', transcript, re.I).span()[0]]
                    self.gui.setInfo(5,place)
                    geocode = self.wc.get_geocode(place)
                    self.gui.setPath(geocode)
                    time.sleep(1)
                    self.gui.setInfo(6)
                    time.sleep(2)
                    self.gui.setInfo(0)
                elif re.search(r'\b지도 꺼\b', transcript, re.I) or re.search(r'\b지도 종료\b', transcript, re.I):
                    self.gui.webView.setVisible(False)
                elif re.search(r'\b등록\b', transcript, re.I):
                    if self.timer_flag is True:
                        self.auth_flag = True
                        self.timer_flag = False
                        print('auth_flag true in sound')
                else:
                    pass

                num_chars_printed = 0

    def listening(self):
        language_code = 'ko-KR'  # a BCP-47 language tag
        RATE = 16000
        CHUNK = int(RATE / 10)  # 100ms
        client = speech.SpeechClient()
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code)

        streaming_config = types.StreamingRecognitionConfig(
            config=config,
            interim_results=True)

        with microphone_stream(RATE, CHUNK) as stream:
            while True:
                audio_generator = stream.generator()
                requests = (types.StreamingRecognizeRequest(audio_content=content)
                            for content in audio_generator)

                responses = client.streaming_recognize(streaming_config, requests)
                try:
                    ret = self.listen_print_loop(responses)
                    if ret == "EXIT":
                        break
                except Exception as e:
                    print(e)
                    pass

    def face_detecting(self):
        face_cascade = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_alt2.xml")
        try:
            cap = cv2.VideoCapture(0)
        except:
            print("cam loading failed")
            return

        while True:
            while self.cam_flag:
                ret, frame = cap.read()
                if not ret:
                    return

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 2, 0, (30, 30))
                if len(faces) == 1:
                    start_x = faces[0][0] - int(faces[0][2] * 0.3)
                    end_x = faces[0][0] + int(faces[0][2] * 1.3)
                    start_y = faces[0][1] - int(faces[0][3] * 0.3)
                    end_y = faces[0][1] + int(faces[0][3] * 1.3)
                    if start_x < 0:
                        start_x = 0
                    if start_y < 0:
                        start_y = 0
                    if end_x >= len(frame[0]):
                        end_x = len(frame[0])
                    if end_y >= len(frame):
                        end_y = len(frame)

                    if end_x - start_x >= 100 and end_y - start_y >= 100:
                        f = frame[start_y:end_y, start_x:end_x]
                        try:
                            file_path = os.path.join('Files', 'test.jpg')
                        except Exception as e:
                            os.makedirs(file_path)
                        finally:
                            cv2.imwrite(file_path, f)
                            self.sem.release()
                            self.cam_flag = False
        cap.release()
        cv2.destroyAllWindows()
