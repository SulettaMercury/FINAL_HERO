# tasks.py

import csv
import os
from firebase_admin import db
from celery import shared_task
#from home.views import export_data_to_csv
from datetime import datetime
from django.conf import settings
from login.models import Iot  # Import your Iot model
from django.conf import settings
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

@shared_task
def fetch_iot_data_to_csv(current_user):
    try:
        # Fetch IoT codes for the current user
        iot_codes = [iot.code for iot in Iot.objects.filter(user=current_user)]

        for iot_code in iot_codes:
            # Initialize a CSV file for each IoT code
            csv_filename = f"iot_data_{iot_code}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
            csv_file_path = os.path.join(settings.MEDIA_ROOT, csv_filename)

            with open(csv_file_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)

                # Write the CSV header
                csv_writer.writerow(["Crop Name", "Date Registered", "Timestamp", "Humidity", "Temperature", "SoilMoisture"])

                # Loop through sensors (S1, S2, S3)
                for sensor_name in ['S1', 'S2', 'S3']:
                    # Fetch data from Firebase
                    crop_name_path = f'IOT/{iot_code}/{sensor_name}/CropDetails/CropName'
                    date_registered_path = f'IOT/{iot_code}/{sensor_name}/CropDetails/DateRegistered'
                    temp_path = f'IOT/{iot_code}/{sensor_name}/TEMP'
                    humid_path = f'IOT/{iot_code}/{sensor_name}/HUMID'
                    soil_moisture_path = f'IOT/{iot_code}/{sensor_name}/SoilMoistureLvl'

                    crop_name_data = database.child(crop_name_path).get()
                    date_registered_data = database.child(date_registered_path).get()
                    temp_data = database.child(temp_path).get()
                    humid_data = database.child(humid_path).get()
                    soil_moisture_data = database.child(soil_moisture_path).get()

                    # Process and save data to the CSV file
                    if crop_name_data:
                        for date, date_data in crop_name_data.items():
                            crop_name = date_data.get("CropName", "")
                            date_registered = date_data.get("DateRegistered", "")

                            # Fetch and process the time entries
                            time_entries = date_data.get("TimeEntries", {})

                            for time, values in time_entries.items():
                                # Combine date and time to create a timestamp
                                timestamp = f"{date}/{time}"  # Modified here

                                temp_value = temp_data.get(timestamp, "")
                                humid_value = humid_data.get(timestamp, "")
                                soil_moisture_value = soil_moisture_data.get(timestamp, "")

                                # Write data to CSV row
                                csv_writer.writerow([crop_name, date_registered, timestamp, temp_value, humid_value, soil_moisture_value])

            print(f"IoT data for {iot_code} fetched and saved to CSV successfully.")

        return None
    except Exception as e:
        print(f"Error: {e}")
        return None