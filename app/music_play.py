import pygame
import time

def play(file):
    pygame.mixer.init()
    pygame.mixer.music.load("test.mp3")
    pygame.mixer.music.play()
    time.sleep(2)
    pygame.mixer.music.stop()
    time.sleep(100)

if __name__=="__main__":
    play("hi")
