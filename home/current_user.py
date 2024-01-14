from django.shortcuts import render, redirect
#from django.contrib.auth.models import User 
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

def current_user(request):
    current_user = request.user  # Get the current user
    
    # Fetch the user's first_name and last_name
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email
    
    # Query your IoT model to fetch data
    
    # Assuming you also want to fetch data from Firebase
    #name = database.child('data').child('name').get().val()
    #framework = database.child('data').child('framework').get().val() - "this is how to fetch data from firebase"

    context = {
        'email':email,
        'first_name': first_name,
        'last_name': last_name,

    }

    return render(request, 'home/home.html', context)
