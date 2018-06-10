# -*- coding: utf-8 -*-

import pyrebase
import os;


config = {
  "apiKey": "AIzaSyAByxlclpYZDLQBk5Enmeg7ImrLlfsD9yU",
  "authDomain": "smartmirror-75b89.firebaseapp.com",
  "databaseURL": "https://smartmirror-75b89.firebaseio.com",
  "storageBucket": "smartmirror-75b89.appspot.com",
  "serviceAccount": "Files/Auth/smartmirror-75b89-firebase-adminsdk-vx8is-56d6e1cacc.json"
}

firebase = pyrebase.initialize_app(config)

# Get a reference to the auth service
auth = firebase.auth()


# Get a reference to the database service
db = firebase.database()
users = db.child("user").get()
user_keys = []

# Get user key in database
for user in users.each():
   user_keys.append(user.key())

for key in user_keys:
   print(key)
   dirname = key 
   if not os.path.isdir(key):
      os.mkdir(key)
   user_val = db.child("user").child(key).child("audio").get()
   if user_val.val() is None:
       continue
   artists = user_val.val().keys()
   storage = firebase.storage()

   for artist in artists:
      songs = user_val.val()[artist].values()
      for song in songs:
         print(song)
         storage.child(key + "/" + song).download(dirname + "/" + song)


