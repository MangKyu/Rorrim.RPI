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
        # we have to do => after login, socket connect should start
        self.connect()
        self.user_uid = None
        self.sem = None
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
            head, body = self.analyze_msg()
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
        return user_uid

    def login_success(self):
        self.wc.send_user_info(self.mirror_uid, self.user_uid)
        print(self.user_uid)
        onoff = self.fm.get_onoff()
        if onoff is None or type(onoff) is not dict:
            print("onoff : ", end="")
            print(onoff)
            return
        for i in onoff:
            if i is "NewsActivity":
                self.news = self.wc.get_news(self.user_uid)
                self.gui.newsLB.setVisible(onoff[i])
            elif i is "PathActivity":
                self.gui.webView.setVisible(onoff[i])
            elif i is "WeatherActivity":
                self.gui.weatherWidget.setVisible(onoff[i])
            elif i is "CalendarActivity":
                sche = self.get_schedule()
                if sche is not None and len(sche) >= 1:
                    pass
                self.gui.scheLB[0].setVisible(onoff[i])
                self.gui.scheLB[1].setVisible(onoff[i])
                self.gui.scheLB[2].setVisible(onoff[i])
            elif i is "MusicActivity":
                self.gui.musicLB[0].setVisible(onoff[i])
                self.gui.musicLB[1].setVisible(onoff[i])

    def sign_out(self):
        # we have to do here => set everything false
        self.user_uid = None
        self.wc.send_user_info(self.mirror_uid, None)

    def get_playlist(self):
        # we have to do  => we have to set playlist
        playlist = []
        playlist.append(["What is Love?", "TWICE(트와이스)"])
        #return self.fm.get_playlist()

    def get_schedule(self, uid=None):
        schedules = self.fm.get_schedule(self.user_uid)
        return schedules

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
                elif re.search(r'\b로그인\b', transcript, re.I):
                    self.cam_flag = True
                    self.sem.acquire()
                    self.user_uid = self.login_request()
                    if self.user_uid is not None:
                        self.login_success()
                elif re.search(r'\b로그아웃\b', transcript, re.I):
                    self.sign_out()
                elif re.search(r'\b노래 틀어줘\b', transcript, re.I):
                    # we have to do => play music
                    pass
                elif re.search(r'\b다음 곡\b', transcript, re.I):
                    # we have to do => play music
                    pass
                elif re.search(r'\b이전 곡\b', transcript, re.I):
                    # we have to do => play music
                    pass
                elif re.search(r'\b길 안내해줘\b', transcript, re.I):
                    pass
                elif re.search(r'\b노래 틀어줘\b', transcript, re.I):
                    pass
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
