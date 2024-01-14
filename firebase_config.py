import pyrebase


config = {
  "apiKey": "AIzaSyDRo3n2Vau04OzvSoi6kPjSH0hdwDvmXBg",
  "authDomain": "smart-6aa8f.firebaseapp.com",
  "databaseURL": "https://smart-6aa8f-default-rtdb.asia-southeast1.firebasedatabase.app",
  "projectId": "smart-6aa8f",
  "storageBucket": "smart-6aa8f.appspot.com",
  "messagingSenderId": "940651613138",
  "appId": "1:940651613138:web:53d4d3e2c3b35317dc160b",
  "measurementId": "G-35KEBDFY60",
}

firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
database=firebase.database()

