from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from login.models import Iot, Plants
from login.forms import IotForm
from django.contrib import messages

#import csv
#from django.views import View
#from django.http import HttpResponse
import pyrebase


#for knn import libraries

import pandas as pd
import numpy as np


config = {
    "apiKey": "AIzaSyDy38KwMWgFg5ne1177zPh-Dhou5RVwuXc",
    "authDomain": "ismartph-20943.firebaseapp.com",
    "databaseURL": "https://ismartph-20943-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "ismartph-20943",
    "storageBucket": "ismartph-20943.appspot.com",
    "messagingSenderId": "435893011622",
    "appId": "1:435893011622:web:1fd376ffa647082986a067",
    "measurementId": "G-R98F0BK4RE"
}


import requests
api_url = 'https://api.render.com/deploy/srv-cm1usoq1hbls73bs3550?key=uP3Nt27G2uc'
firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
database=firebase.database()

@login_required
def home(request):
    response = requests.get(api_url)
    if response.status_code == 200:
        print("OK")
        data = response.json()
    else:
        print("NA")
        
    current_user = request.user  # Get the current user
    
    # Fetch the user's first_name and last_name
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email
    
    # Query your IoT model to fetch data
    items = Iot.objects.filter(user=current_user)
    
    context = {
        'email':email,
        'first_name': first_name,
        'last_name': last_name,
        'items': items,

    }
    
    # print(context)

    return render(request, 'home/home.html', context)
  
from datetime import datetime, timedelta

@login_required
def crops(request):
    
    current_user = request.user  # Get the current user

    # Fetch the user's first_name, last_name, and email
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email
        
    # Query the Plants model to fetch crop names
    crops = Plants.objects.all()  # Fetch all crop names from the database

    # Query your IoT model to fetch data
    items = Iot.objects.filter(user=current_user)
        
    form = IotForm()  # Initialize the form
    


    context = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'items': items,
        'crops': crops,  # Pass the crop names to the template
        'form' : form,
    }
    # Query your IoT model to fetch data
    items = Iot.objects.filter(user=current_user)
    if not items.exists():  # Check if there are no registered IoT devices
        no_iot_message = 'No registered IoT devices. Kindly register one first.'
        context['no_iot_message'] = no_iot_message
        
    else:
        # Fetch data from Firebase based on IoT code
        iot_code = items.first().code  # Assuming you want data for the first IoT code
        firebase_path = f'IOT/{iot_code}'
        firebase_data = database.child(firebase_path).get().val()
        iot_code = [iot.code for iot in items]
        
        if iot_code:
            context['iot_code'] = iot_code
  
            if firebase_data:
                
                # Populate dropdown options with S1, S2, S3 values
                sensor_options = [(key, key) for key in firebase_data.keys() if key != 'DATA' and key !='STATIC' and key != 'Notification' and key != 'Notifications' and key != 'CropsHarvested']
                context['sensor_options'] = sensor_options
                # Fetch data from Firebase based on IoT codes
                iot_codes = [iot.code for iot in items]  # Assuming you want data for all IoT codes

                # Initialize the no_crop_message to a default value
                no_crop_message = "You don't have any registered crop yet to your IoT. Kindly register first."

                crop_data = {}  # Dictionary to store crop data for each IoT code
                
                disabled_sensor_options = []

                # Iterate over IoT codes
                for iot_code in iot_codes:
                    firebase_path = f'IOT/{iot_code}'
                    firebase_data = database.child(firebase_path).get().val()
                    
                    
                    if firebase_data:
                        crop_names = {}  # List to store crop names for each sensor
                        disabled_sensors = {}

                        # Iterate over sensors S1, S2, S3
                        for sensor_name, sensor_records in [
                                ('S1', firebase_data.get('S1', {})),
                                ('S2', firebase_data.get('S2', {})),
                                ('S3', firebase_data.get('S3', {}))
                            ]:
                            
                            if isinstance(sensor_records, dict):
                                crop_name = sensor_records.get('CropDetails', {}).get('cropName', '')
                                #print(crop_name)
                                if crop_name:
                                    crop_names[sensor_name] = crop_name
                                    
                                    for sensor_name, sensor_records in [
                                        ('S1', firebase_data.get('S1', {})),
                                        ('S2', firebase_data.get('S2', {})),
                                        ('S3', firebase_data.get('S3', {}))
                                    ]:
                                        
                                        if isinstance(sensor_records, dict):
                                         
                                            # Check if harvest_stat is "NOT YET" for the current crop
                                            harvest_stat = sensor_records.get('CropDetails').get('harvestStat', '')
                                        
                                            if harvest_stat == "NOT YET":
                                                # Append the sensor name to the list of disabled sensor names
                                                disabled_sensor_options.append(sensor_name)                   
                                                
                                                if disabled_sensors:
                                                    disabled_sensors[iot_code] = disabled_sensor_options  # Convert iot_code to an integer            
            

                        if crop_names:
                            crop_data[iot_code] = crop_names  # Store crop names for this IoT code
                            
                                        
                # Set the no_crop_message in the context dictionary after processing all IoT codes
                context['no_crop_message'] = no_crop_message
                context['crop_data'] = crop_data
                context['disabled_sensor_options'] = disabled_sensor_options
                    
        if request.method == "POST":
             # Define harvest days based on crop name
            harvest_days_mapping = {
            "Mustasa": 35,
            "Petchay": 32,
            "Kang-Kong": 30,
            # Add more crops and their corresponding harvest days as needed
            }   
                
            # Get form data from the POST request
            date_registered = request.POST.get("dateRegistered")
            #crop_date_planted = request.POST.get("cropDatePlanted")
            crop_name = request.POST.get("cropName")
            type_of_used_soil = request.POST.get("typeOfUsedSoil")
            print(type_of_used_soil)
            iot_code = request.POST.get("iot_code")
            sensor = request.POST.get("sensor")
            harvest_stat = "NOT YET"
             
            # Set harvest days based on crop name or default to 35 days
            harvest_days = harvest_days_mapping.get(crop_name, 35)

            # Calculate harvest date by adding the determined harvest days to the registration date
            registration_date = datetime.strptime(date_registered, "%Y-%m-%d")
            harvest_date = registration_date + timedelta(days=harvest_days)
            
            # data structure for saving data to Firebase
            data = {
                "dateRegistered": date_registered,
                #"cropDatePlanted": crop_date_planted,
                "cropName": crop_name,
                "typeOfUsedSoil": type_of_used_soil,
                "harvestStat" : harvest_stat,
                "harvestDays": harvest_days,  # Save the determined harvest days
                "harvestDate": harvest_date.strftime("%Y-%m-%d"),  # Save the formatted harvest date
            }
            

            
            # Save the data to Firebase under the selected sensor and CropDetails
            Crops = f"IOT/{iot_code}/{sensor}/CropDetails"
            StaticData = f"IOT/{iot_code}/{sensor}/StaticData"
            SMLSTATIC = f"IOT/{iot_code}/{sensor}/SD"
            WaterIrrig = f"IOT/{iot_code}/{sensor}/WaterIrrigation"
            LastOn = f"IOT/{iot_code}/{sensor}/WaterIrrigation/LastOn"
            LastOff = f"IOT/{iot_code}/{sensor}/WaterIrrigation/LastOff"
            Daily = f"IOT/{iot_code}/{sensor}/{crop_name}/daily_prediction"
            harvest = f"IOT/{iot_code}/{sensor}/{crop_name}/harvestdays_recs"
            
            database.child(Crops).set(data)
            database.child(StaticData).set({'SoilMoistureLvl': ''})
            database.child(SMLSTATIC).set({'SML':'0'})
            database.child(WaterIrrig).set({'LastOn': '', 'WaterTemp': '40', 'Switch': '0','LastOff': ''})
            date = datetime.now().strftime('%Y-%m-%d%H:%M:%S')
            time = datetime.now().strftime('%H:%M:%S')
            date1 = datetime.now().strftime('%Y-%m-%d')
            
            database.child(LastOn).set({date:time})
            database.child(LastOff).set({date:time})
            database.child(Daily).set({date1:'NOT YET DETERMINED'})
            database.child(harvest).set({date1:harvest_days})
            
            # After successfully registering the crop, add a success message
            messages.success(request, 'Successfully registered new crop to ismartph!')
        
            # Redirect to a success page or back to the form page
            return redirect('/crops')        
        
    return render(request, 'home/crops.html', context)


from datetime import datetime
#from login.forms import IrisPredictionForm
from sklearn.neighbors import KNeighborsClassifier
import joblib
import numpy as np
from django.shortcuts import render
from collections import defaultdict
import os 
from django.conf import settings


def load_knn_model(model_name):
    # Construct the absolute path to the joblib file
    model_path = os.path.join(settings.BASE_DIR, 'static', 'jupyter_notebooks', f'{model_name}_prediction_model.joblib')

    # Load the model
    try:
        knn_model = joblib.load(model_path)
        return knn_model
    except Exception as e:
        return HttpResponse(f"Error loading {model_name} model: {str(e)}", status=500)

# Loading trained model FOR MUSTASA
knn_mustasa = KNeighborsClassifier(n_neighbors=5, metric='euclidean', p=2)
knn_mustasa = load_knn_model('knn_mustasa')

# Loading trained model FOR PETCHAY
knn_petchay = KNeighborsClassifier(n_neighbors=5, metric='euclidean', p=2)
knn_petchay = load_knn_model('knn_petchay')

# Loading trained model FOR KANGKONG
knn_kangkong = KNeighborsClassifier(n_neighbors=5, metric='euclidean', p=2)
knn_kangkong = load_knn_model('knn_kangkong')




# Mapping dictionary for classification
variety_mapping = {0: 'GOOD', 1: 'BAD'}
# Initialize count dictionaries for each day

@login_required
def fetch_firebase_data(request, iot_code, sensor, crop):
    
    current_user = request.user  # Get the current user
    
    items = Iot.objects.filter(user=current_user)
    


    data = {}


    # No need to query the Iot model for sensor_name
    sensor_name = sensor  # Use the sensor value passed as an argument

    if iot_code and sensor_name:
        #path in firebase for cropname and registered date
        crop_name_path = f'IOT/{iot_code}/{sensor}/CropDetails/cropName'
        date_registered_path = f'IOT/{iot_code}/{sensor}/CropDetails/dateRegistered'
        days_to_harvest = f'IOT/{iot_code}/{sensor}/CropDetails/harvestDays'
        
        #water irrigation monitoring part
        waterLastOn_path = f'IOT/{iot_code}/{sensor}/WaterIrrigation/LastOn/'
        waterTempVal_path = f'IOT/{iot_code}/{sensor}/WaterIrrigation/WaterTemp'
        switch_path = f'IOT/{iot_code}/{sensor}/WaterIrrigation/Switch'

        #note kulang pa ng for harvest (algo)
        
        #sml,temperature,humid
               
        temp_path = f'IOT/{iot_code}/STATIC/TEMP'
        humid_path = f'IOT/{iot_code}/STATIC/HUMID'
        soil_moisture_path = f'IOT/{iot_code}/{sensor}/SD/SML'
        
        #getting the value at database based on the path of data
        data['CropName'] = database.child(crop_name_path).get().val()
        data['DateRegistered'] = database.child(date_registered_path).get().val()
        lastOn_data = database.child(waterLastOn_path).order_by_key().limit_to_last(1).get().val()
    
        if lastOn_data:
            lastOn_key = list(lastOn_data.keys())[0]
            lastOn_value = lastOn_data[lastOn_key]
            print("Latest Date:", lastOn_key, "Value:", lastOn_value)
        else:
            print("No data available in the LastOn path.")
            lastOn_key = None
            lastOn_value = None

        data['LastOn'] = {'key': lastOn_key, 'value': lastOn_value}
            
        data['WaterTemp'] = database.child(waterTempVal_path).get().val()
        data['harvestdays'] = database.child(days_to_harvest).get().val()
        data['Switch'] = database.child(switch_path).get().val()

        # Debugging: Print the constructed temp_path
        #print(f'temp_path: {temp_path}')
        #print(f'humid_path: {humid_path}')
        #print(f'soil_moisture_path {soil_moisture_path}')                
        
        # Fetch data from Firebase using the paths (temperature)
        temp_data = database.child(temp_path).get().val()
        #print(f'temp_data: {temp_data}')

       # Ensure temp_data is numeric (either int or float)
        try:
            temp_data = float(temp_data)
        except (ValueError, TypeError):
            temp_data = None  # Set temp_data to None if it can't be converted to a number

        # Temperature classification logic
        classification = "N/A"  # Default classification 
        
        #add 10 since mas mainit daw inside greenhouse

        if crop == "Mustasa" and temp_data is not None:
            if 28 <= temp_data <= 32.9:
                classification = "JUST RIGHT"
            elif temp_data >= 33:
                classification = "TOO HOT"
            elif temp_data <= 27.9: 
                classification = "TOO COLD"
   
        # change the value of temp_data for petchay if meron na data from net         
        if crop == "Petchay" and temp_data is not None:
            if 28 <= temp_data <= 30.9:
                classification = "JUST RIGHT"
            elif temp_data >= 30.9:
                classification = "TOO HOT"
            elif temp_data <= 27.9: 
                classification = "TOO COLD"
                
        # change the value of temp_data for petchay if meron na data from net         
        if crop == "Kangkong" and temp_data is not None:
            if 30 <= temp_data <= 40.9:
                classification = "JUST RIGHT"
            elif temp_data >= 40.9:
                classification = "TOO HOT"
            elif temp_data <= 29.9: 
                classification = "TOO COLD"

        data['TemperatureClassification'] = classification
        
        # Fetch data from Firebase using the paths (humidity)
        humid_data = database.child(humid_path).get().val()
        #print(f'humid_data: {humid_data}')
        
        try:
            humid_data = float(humid_data)
        except (ValueError, TypeError):
            humid_data = None  # Set temp_data to None if it can't be converted to a number

        # Temperature classification logic
        classification = "N/A"  # Default classification

        if crop == "Mustasa" and humid_data is not None:
            if 70 <= humid_data <= 80.9:
                classification = "GOOD"
            elif humid_data >= 81:
                classification = "TOO HIGH"
            elif humid_data <= 69.9:   
                classification = "TOO LOW"
                
        if crop == "Petchay" and humid_data is not None:
            if 70 <= humid_data <= 80.9:
                classification = "GOOD"
            elif humid_data >= 81:
                classification = "TOO HIGH"
            elif humid_data <= 69.9:   
                classification = "TOO LOW"
                
        if crop == "Kangkong" and humid_data is not None:
            if 50 <= humid_data <= 70.9:
                classification = "GOOD"
            elif humid_data >= 71:
                classification = "TOO HIGH"
            elif humid_data <= 49.9:   
                classification = "TOO LOW"

        data['HumidityClassification'] = classification
                
        # Fetch data from Firebase using the paths (soil moisture level)
        soil_moisture_data = database.child(soil_moisture_path).get().val()
        #print(f'soil_moisture_data: {soil_moisture_data}')
        
        try:
            soil_moisture_data = float(soil_moisture_data)
        except (ValueError, TypeError):
            soil_moisture_data = None  # Set temp_data to None if it can't be converted to a number

        classification = "N/A"  # Default classification

        if crop == "Mustasa" and soil_moisture_data is not None:
            if 70 <= soil_moisture_data <= 80.9:
                classification = "SUFFICIENT"
            elif soil_moisture_data >= 81:
                classification = "WET"
            elif soil_moisture_data <=69.9:
                classification = "DRY"
                
        if crop == "Petchay" and soil_moisture_data is not None:
            if 70 <= soil_moisture_data <= 80.9:
                classification = "SUFFICIENT"
            elif soil_moisture_data >= 81:
                classification = "WET"
            elif soil_moisture_data <=69.9:
                classification = "DRY"
                
        if crop == "Kangkong" and soil_moisture_data is not None:
            if 60 <= soil_moisture_data <= 80.9:
                classification = "SUFFICIENT"
            elif soil_moisture_data >= 81:
                classification = "WET"
            elif soil_moisture_data <=59.9:
                classification = "DRY"
        
        data['SMLClassification'] = classification
        
        if iot_code and sensor_name and crop == "Mustasa":
            
            # Use the fetched data to make predictions
            temperature = temp_data
            humidity = humid_data
            soil_moisture = soil_moisture_data

            input_data = np.array([[temperature, humidity, soil_moisture]])
            prediction_label_mustasa = knn_mustasa.predict(input_data)[0]
            # Convert the predicted label to variety name
            
            # Get the current date and time
            current_datetime = datetime.now().strftime("%b-%d-%Y-%H:%M:%S")
            
            
            predicted_classification = variety_mapping.get(prediction_label_mustasa, 'Unknown')
            
            data['predicted_classification'] = predicted_classification
            data['datetime_of_prediction'] = current_datetime
            
            print(f"Prediction made on {current_datetime}: {predicted_classification}")
            
            
            
            
        elif iot_code and sensor_name and crop == "Petchay":
            
            # Use the fetched data to make predictions
            temperature = temp_data
            humidity = humid_data
            soil_moisture = soil_moisture_data
            
            input_data = np.array([[temperature, humidity, soil_moisture]])
            prediction_label_petchay = knn_petchay.predict(input_data)[0]
            # Convert the predicted label to variety name
            
            # Get the current date and time
            current_datetime = datetime.now().strftime("%b-%d-%Y-%H:%M:%S")
            
            
            predicted_classification = variety_mapping.get(prediction_label_petchay, 'Unknown')
            
            data['predicted_classification'] = predicted_classification
            data['datetime_of_prediction'] = current_datetime
            
            print(f"Prediction made on {current_datetime}: {predicted_classification}")
            
            
            
        elif iot_code and sensor_name and crop == "Kangkong":
            
            # Use the fetched data to make predictions
            temperature = temp_data
            humidity = humid_data
            soil_moisture = soil_moisture_data
            
            input_data = np.array([[temperature, humidity, soil_moisture]])
            prediction_label_kangkong = knn_kangkong.predict(input_data)[0]
            # Convert the predicted label to variety name
            
            # Get the current date and time
            current_datetime = datetime.now().strftime("%b-%d-%Y-%H:%M:%S")
            
            
            predicted_classification = variety_mapping.get(prediction_label_kangkong, 'Unknown')
            
            data['predicted_classification'] = predicted_classification
            data['datetime_of_prediction'] = current_datetime
            
            print(f"Prediction made on {current_datetime}: {predicted_classification}")
            
            
        notif_path = f'IOT/{iot_code}/Notifications/WaterPumpOff'
        notif_pathOn = f'IOT/{iot_code}/Notifications/WaterPumpOn'

        snapshot_off = database.child(notif_path).get()

        if snapshot_off.val() is not None:
            unread_count_off = len(snapshot_off.val())
            data['unread_count_off'] = unread_count_off
        else:
            data['unread_count_off'] = 0

        snapshot_on = database.child(notif_pathOn).get()

        if snapshot_on.val() is not None:
            unread_count_on = len(snapshot_on.val())
            data['unread_count_on'] = unread_count_on
        else:
            data['unread_count_on'] = 0

        data['total_unread_count'] = data['unread_count_off'] + data['unread_count_on']
        
        
        
        print("Total Unread Count:", data['total_unread_count'])
            
                        

    else:
        # Handle the case where the user does not have registered iot_code and sensor_name
        data['CropName'] = "N/A"
        data['DateRegistered'] = "N/A"
        data['harvestdays'] = "N/A"
        data['TEMP'] = "N/A"
        data['HUMID'] = "N/A"
        data['SoilMoistureLvl'] = "N/A"
        data['LastOn'] = "Not yet used"
        data['WaterTemp'] = "N/A"
        
    return data


@login_required
def get_prediction(request, iot_code, sensor, crop):
    
    current_user = request.user  # Get the current user
    
    items = Iot.objects.filter(user=current_user)
    


    data = {}
    
    
    if crop == 'Petchay':
        # Get the date from yesterday in the format "mm-dd-yyyy"
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        print(yesterday_date)
        # Assuming the daily_prediction format is "mm-dd-yyyy : PREDICTION"
        prediction_path = f'IOT/{iot_code}/{sensor}/{crop}/daily_prediction/{yesterday_date}'
        print(prediction_path)
        predicted_output = database.child(prediction_path).get().val()

        # Convert the date to "December 02, 2023" format
        formatted_date = datetime.strptime(yesterday_date, "%Y-%m-%d").strftime("%B %d, %Y")

        data['predicted_output'] = predicted_output
        data['formatted_date'] = formatted_date
        
    elif crop == 'Mustasa':
        # Get the date from yesterday in the format "mm-dd-yyyy"
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Assuming the daily_prediction format is "mm-dd-yyyy : PREDICTION"
        prediction_path = f'IOT/{iot_code}/{sensor}/{crop}/daily_prediction/{yesterday_date}'
        predicted_output = database.child(prediction_path).get().val()

        # Convert the date to "December 02, 2023" format
        formatted_date = datetime.strptime(yesterday_date, "%Y-%m-%d").strftime("%B %d, %Y")

        data['predicted_output'] = predicted_output
        data['formatted_date'] = formatted_date
        
    elif crop == 'Kangkong':
        # Get the date from yesterday in the format "mm-dd-yyyy"
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Assuming the daily_prediction format is "mm-dd-yyyy : PREDICTION"
        prediction_path = f'IOT/{iot_code}/{sensor}/{crop}/daily_prediction/{yesterday_date}'
        predicted_output = database.child(prediction_path).get().val()

        # Convert the date to "December 02, 2023" format
        formatted_date = datetime.strptime(yesterday_date, "%Y-%m-%d").strftime("%B %d, %Y")

        data['predicted_output'] = predicted_output
        data['formatted_date'] = formatted_date
        
    return data



@login_required
def mycrop(request, iot_code, sensor, crop):
        
    current_user = request.user

    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email
    


    # Query the IoT model to fetch data
    items = Iot.objects.filter(user=current_user)

    # Fetch data from Firebase using the function
    firebase_data = fetch_firebase_data(request, iot_code, sensor, crop)
    get_predicted_output = get_prediction(request, iot_code, sensor, crop)
    
    
    predicted_output = get_predicted_output.get('predicted_output', 'Data not available')
    formatted_date = get_predicted_output.get('formatted_date', 'Data not available') 
    
    # Access data directly from the firebase_data dictionary
    crop_name = firebase_data.get('CropName', 'Data not available')
    date_registered = firebase_data.get('DateRegistered', 'Data not available')
    harvest_days = firebase_data.get('harvestdays', 'Data not available')
    
    lastOn_key = firebase_data['LastOn']['key']
    
    # Parse the datetime from lastOn_key
    last_on_datetime = datetime.strptime(lastOn_key, '%Y-%m-%d%H:%M:%S')


    # Extract only the date part
    last_on_date = last_on_datetime.strftime('%Y-%m-%d')
    
    lastOn_value = firebase_data['LastOn']['value']
    
    
    waterTemp = firebase_data.get('WaterTemp', 'Data not available')
    Switch = firebase_data.get('Switch', 'Data not available')
    
    
    total_counts = firebase_data.get('total_unread_count', 'No Notifications')

    
    # Get the temperature classification from the fetch_firebase_data function
    temperature_classification = firebase_data.get('TemperatureClassification', 'Data not available')
    
    humidity_classification = firebase_data.get('HumidityClassification', 'Data not available')
    
    sml_classification = firebase_data.get('SMLClassification', 'Data not available')
    
    
    datePrediction = firebase_data.get('datetime_of_prediction', 'N/A')
    
    ClassificationPred = firebase_data.get('predicted_classification', 'N/A')

    
    # Access data directly from the firebase_data dictionary
    #good_count = firebase_data.get('good_count', 'Data not available')
    #bad_count = firebase_data.get('bad_count', 'Data not available')
    #current_classification_report = firebase_data.get('crop_growth_health', 'Not Determined')
    

    # Construct the Firebase paths
    #today_date = datetime.now().strftime("%b-%d-%Y")
    
    temp_path = f'IOT/{iot_code}/STATIC/TEMP'
    humid_path = f'IOT/{iot_code}/STATIC/HUMID'
    
    soil_moisture_path = f'IOT/{iot_code}/{sensor}/SD/SML'

    # Fetch data from Firebase using the paths
    temp_data = database.child(temp_path).get().val()
    #print("TESTING:", temp_data)
    humid_data = database.child(humid_path).get().val()
    soil_moisture_data = database.child(soil_moisture_path).get().val()
    
        
    #temperature_wdate = f'IOT/{iot_code}/DATA/TEMP/{today_datetime}'
    #temperature_data = database.child(temperature_wdate).get().val()
    #print ('date and time today: ', today_datetime, ': ' ,temperature_data)
                
    context = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'items': items,
        'iot_code': iot_code,
        'sensor': sensor,
        'crop': crop,
        'crop_name': crop_name,
        'date_registered': date_registered,
        'harvest_days': harvest_days,
        'last_on_date': last_on_date, 
        'lastOn_value': lastOn_value,
        'switch': Switch,
        'waterTemp': waterTemp,
        'temp': temp_data,
        'humid': humid_data,
        'soil_moisture': soil_moisture_data,
        'temperature_classification': temperature_classification,
        'humidity_classification': humidity_classification,  # Add the temperature classification to the context
        'sml_classification': sml_classification,  # Add the temperature classification to the context
        'datetime_of_prediction': datePrediction,
        'predicted_classification': ClassificationPred,
        'predicted_output' : predicted_output,
        'formatted_date' : formatted_date,
        'total_unread_count' : total_counts,
    }
    
    
    return render(request, 'home/mycrop.html', context)


@login_required
def iot_reg(request):
    
    current_user = request.user  # Get the current user

    # Fetch the user's first_name, last_name, and email
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email

    # Query your IoT model to fetch data
    items = Iot.objects.filter(user=current_user)
    
    form = IotForm()  # Initialize the form
    
    
    context = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'items': items,
        'form': form,
    }

    if request.method == 'POST':
        
        form = IotForm(request.POST)
        
        if form.is_valid():
            
            iot_code = form.cleaned_data['code']  # Get the IoT code from the form
        
            # Check if the IoT code already exists in the database for any user
            existing_iot = Iot.objects.filter(code=iot_code).first()
        
    
            if existing_iot:
                # IoT code already exists in the database
                if existing_iot.user == request.user:
                    # IoT code belongs to the current user
                    messages.error(request, 'The entered IoT code already exists in your account.')
                else:
                    # IoT code belongs to another user
                    messages.error(request, 'The entered IoT code is already registered to another user.')
            else:
                # IoT code doesn't exist, save to Django DB and Firebase
                new_iot_code = form.save(commit=False)
                new_iot_code.user = request.user
                new_iot_code.save()
                firebase_path = f'IOT/{iot_code}'
                
                data = {
                    'STATIC': {
                        'TEMP': '60',
                        'HUMID': '60'  
                    },
                    'DATA': {
                        'TEMP': '',
                        'HUMID': ''
                    },
                    'S1': '',
                    'S2': '',
                    'S3': '',
                    'CropsHarvested': ''
                }
                
                database.child(firebase_path).set(data)
                
                # Add a success message
                messages.success(request, 'IoT code successfully registered')

                return redirect('/reg_iot',context)  # Redirect to a success page
            
        else:
            # Form is not valid; display the error message
            messages.error(request, 'IoT code is invalid')
    
    return redirect('/crops',context)  # Redirect to a success page



from django.http import HttpResponse

#TEMP AND ON OFF BUTTON

@login_required
def onButton(request):
    if request.method == 'POST':
        
        # Access form data including the hidden field 'iot_code'
        iot_code = request.POST.get('iot_code')
        sensor = request.POST.get('sensor')
        crop = request.POST.get('crop')
        # Get current date and time (you may need to import datetime)
        import datetime
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        time = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Save the data to Firebase under the selected sensor and CropDetails
        WaterIrrig = f"IOT/{iot_code}/{sensor}/WaterIrrigation"
        LastOn = f"IOT/{iot_code}/{sensor}/WaterIrrigation/LastOn"
        dateAndTime = date + time
        database.child(WaterIrrig).update({'Switch': 1})
        database.child(LastOn).update({dateAndTime: time})

        # Redirect to a success page or back to the form page
    
    return redirect('mycrop-user', iot_code=iot_code, sensor=sensor, crop=crop)        


@login_required
def offButton(request):
    if request.method == 'POST':
        # Access form data including the hidden field 'iot_code'
        iot_code = request.POST.get('iot_code')
        sensor = request.POST.get('sensor')
        crop = request.POST.get('crop')
        # Get current date and time (you may need to import datetime)
        import datetime
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        time = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Save the data to Firebase under the selected sensor and CropDetails
        WaterIrrig = f"IOT/{iot_code}/{sensor}/WaterIrrigation"
        LastOn = f"IOT/{iot_code}/{sensor}/WaterIrrigation/LastOff"
        dateAndTime = date + time
        database.child(WaterIrrig).update({'Switch': 0})
        database.child(LastOn).update({dateAndTime: time})
            
        # Redirect to a success page or back to the form page

    return redirect('mycrop-user', iot_code=iot_code, sensor=sensor, crop=crop) 
from django.contrib import messages

@login_required
def temp(request):
    if request.method == 'POST':
        iot_code = request.POST.get('iot_code')
        sensor = request.POST.get('sensor')
        crop = request.POST.get('crop')
        
        # Get the value from the 'celsius' input
        temp_str = request.POST.get('celcius')
        print(temp_str)
        
        # Check if the value is not empty and not None
        if temp_str is not None and temp_str != '':
            # Convert the value to an integer
            temp_int = int(temp_str)

            # Check if the integer value is between 40 and 90
            if 40 <= temp_int <= 90:
                temp = str(temp_int)
                # Save the data to Firebase under the selected sensor and CropDetails
                WaterIrrig = f"IOT/{iot_code}/{sensor}/WaterIrrigation"
                database.child(WaterIrrig).update({'WaterTemp': temp})
            else:
                # Handle the case where the value is not between 40 and 90
                messages.error(request, 'Temperature should be between 40 and 90 degrees Celsius.')
        else:
            # Handle the case where the input is empty or None
            messages.error(request, 'Temperature input cannot be empty.')

    return redirect('mycrop-user', iot_code=iot_code, sensor=sensor, crop=crop)


from .forms import UpdateUser

@login_required
def settings(request):
    
    current_user = request.user

    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email
    


    # Query the IoT model to fetch data
    items = Iot.objects.filter(user=current_user)
    
    if request.method == 'POST':
        u_form = UpdateUser(request.POST, instance=request.user)

        if u_form.is_valid():
            u_form.save()
            return redirect('settings')
    else:
        u_form = UpdateUser(instance=request.user)

    current_user = request.user  # Get the current user

    # Fetch the user's first_name and last_name
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email
    date = current_user.date_joined
    #update form
    context = {
        'email':email,
        'first_name': first_name,
        'last_name': last_name,
        'u_form' : u_form,
        'date' : date
    }
    
    return render(request, 'home/settings.html', context)


@login_required
def password(request):
    
    current_user = request.user

    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email
    


    # Query the IoT model to fetch data
    items = Iot.objects.filter(user=current_user)
    
    if request.method == 'POST':
        u_form = UpdateUser(request.POST, instance=request.user)

        if u_form.is_valid():
            u_form.save()
            return redirect('settings')
    else:
        u_form = UpdateUser(instance=request.user)

    current_user = request.user  # Get the current user

    # Fetch the user's first_name and last_name
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email
    date = current_user.date_joined
    #update form
    context = {
        'email':email,
        'first_name': first_name,
        'last_name': last_name,
        'u_form' : u_form,
        'date' : date
    }
    
    return render(request, 'home/password.html', context)


def notifCount(request, iot_code, sensor, crop):
    
    current_user = request.user
    items = Iot.objects.filter(user=current_user)
    
    firebase_data = fetch_firebase_data(request, iot_code, sensor, crop)
    total_counts = firebase_data.get('total_unread_count', 'No Notifications')

    context = {
        'total_unread_count' : total_counts,
    }
    
    
    return render(request, 'home/base.html', context)

from prettytable import PrettyTable
@login_required
def crop_progress_report_view(request, iot_code, sensor, crop):
    current_user = request.user

    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email
    


    # Query the IoT model to fetch data
    items = Iot.objects.filter(user=current_user)

    # Fetch data from Firebase using the function
    firebase_data = fetch_firebase_data(request, iot_code, sensor, crop)
        
    # Access data directly from the firebase_data dictionary
    crop_name = firebase_data.get('CropName', 'Data not available')
    date_registered = firebase_data.get('DateRegistered', 'Data not available')
    
    # ...

    harvest_days_path = f'IOT/{iot_code}/{sensor}/CropDetails/harvestDays'
    harvest_days_val = database.child(harvest_days_path).get().val()

    daily_pred_path = f'IOT/{iot_code}/{sensor}/{crop}/daily_prediction'
    daily_pred_val = database.child(daily_pred_path).get().val()

    # Get today's date and yesterday's date
    today_date = datetime.now().date()
    yesterday_date = today_date - timedelta(days=1)

    # Get the last recorded predictive harvest range value
    last_recorded_harvest_range = harvest_days_val if isinstance(harvest_days_val, int) else harvest_days_val.get(yesterday_date, 'N/A')

    # Update harvest_days_val based on today's prediction
    today_prediction = daily_pred_val.get(str(today_date), 'N/A')

    if today_prediction == 'GOOD':
        # If the prediction is GOOD, subtract 1 from harvest_days_val
        harvest_days_val -= 1
    elif today_prediction == 'BAD':
        # If the prediction is BAD, add 1 to harvest_days_val
        harvest_days_val += 1

    # Retrieve predictive harvest range values from Firebase
    harvest_days_recs_path = f'IOT/{iot_code}/{sensor}/{crop}/harvestdays_recs'
    harvest_days_recs_val = database.child(harvest_days_recs_path).get().val()

    # Create a dictionary for each day's data
    data = [{'date': date,
            'prediction': prediction,
            'days_progress': '-1 day' if prediction == 'GOOD' else '+1 day' if prediction == 'BAD' else 'No change',  # Adjust for the previous day
            'predictive_harvest_range': harvest_days_recs_val.get(date, 'N/A')}  # Get value from harvestdays_recs for the current date
            for date, prediction in daily_pred_val.items()]

    context = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'items': items,
        'iot_code': iot_code,
        'sensor': sensor,
        'crop': crop,
        'crop_name': crop_name,
        'date_registered': date_registered,
        'data': data,
    }

    return render(request, 'home/crop_progress_report.html', context)

@login_required
def irrigation_records_view(request, iot_code, sensor, crop):
    
    current_user = request.user

    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email
    


    # Query the IoT model to fetch data
    items = Iot.objects.filter(user=current_user)

    # Fetch data from Firebase using the function
    firebase_data = fetch_firebase_data(request, iot_code, sensor, crop)
        
    # Access data directly from the firebase_data dictionary
    crop_name = firebase_data.get('CropName', 'Data not available')
    
    # Fetch LastOn data
    onPump_path = f'IOT/{iot_code}/{sensor}/WaterIrrigation/LastOn'
    onPump_data = database.child(onPump_path).get().val()

    # Fetch LastOff data
    offPump_path = f'IOT/{iot_code}/{sensor}/WaterIrrigation/LastOff'
    offPump_data = database.child(offPump_path).get().val()

    # Convert timestamped entries to a list of tuples (date, time)
    onPump_entries = [(date[:10], time) for date, time in onPump_data.items()]  # Extract only the date part
    offPump_entries = [(date[:10], time) for date, time in offPump_data.items()]  # Extract only the date part

    # Create a dictionary to store a list of Last Off entries by date
    off_entries_dict = {}
    for date, time in offPump_entries:
        if date in off_entries_dict:
            off_entries_dict[date].append(time)
        else:
            off_entries_dict[date] = [time]

    # Add Last Off entries to the onPump entries
    combined_entries = []
    for on_date, on_time in onPump_entries:
        off_times = off_entries_dict.get(on_date, [])
        if off_times:
            # Find the closest Last Off time to the Last On time
            closest_off_time = min(off_times, key=lambda x: abs(int(x.split(":")[0]) - int(on_time.split(":")[0])))
            combined_entries.append((on_date, on_time, on_date, closest_off_time))
        else:
            combined_entries.append((on_date, on_time, '', ''))



    context = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'items': items,
        'iot_code': iot_code,
        'sensor': sensor,
        'crop': crop,
        'crop_name': crop_name,
        'combined_entries': combined_entries,
    }

    return render(request, 'home/irrigation_records.html', context)

@login_required
def remove(request):
    if request.method == 'POST':
        # Access form data including the hidden field 'iot_code'
        iot_code = request.POST.get('iot_code')
        sensor = request.POST.get('sensor')
        crop = request.POST.get('crop')
        crop_name = f"IOT/{iot_code}/{sensor}"
        database.child(crop_name).remove()
        update = f"IOT/{iot_code}/"
        database.child(update).update({sensor:""})
        # Redirect to a success page or back to the form page

    return redirect('crops-user') 

#NOT COMPLETE
@login_required
def harvest1(request):
    if request.method == 'POST':
        # Access form data including the hidden field 'iot_code'
        iot_code = request.POST.get('iot_code')
        sensor = request.POST.get('sensor')
        crop = request.POST.get('crop')

        #check number
        check = f"IOT/{iot_code}/CropsHarvested/"
        check = database.child(check).get()
        count = len(check.val())
        count = count + 1
        print (count)

        #get data
        path = f"IOT/{iot_code}/{sensor}/CropDetails"
        #print(database.child(path).get().val())
        oks = database.child(path).get().val()

        #get data
        path = f"IOT/{iot_code}/{sensor}/{crop}"
        #print(database.child(path).get().val())
        crop1 = database.child(path).get().val()
        date = datetime.now().strftime('%Y-%m-%d')
        
        #get data
        path = f"IOT/{iot_code}/{sensor}/WaterIrrigation"
        #print(database.child(path).get().val())
        water = database.child(path).get().val()
        crop_name = date + "_" + str(count) + "_" + crop

        #set
        update = f"IOT/{iot_code}/CropsHarvested/{crop_name}/CropDetails"
        update1 = f"IOT/{iot_code}/CropsHarvested/{crop_name}/{crop}"
        update2 = f"IOT/{iot_code}/CropsHarvested/{crop_name}/WaterIrrigation"
        database.child(update).set(oks)
        database.child(update1).set(crop1)
        database.child(update2).update(water)


    #delete in sensor
        crop_name = f"IOT/{iot_code}/{sensor}"
        database.child(crop_name).remove()
        update = f"IOT/{iot_code}/"
        database.child(update).update({sensor:""})

        # Redirect to a success page or back to the form page

    return redirect('crops-user') 

@login_required
def history(request):
    response = requests.get(api_url)
    if response.status_code == 200:
        #print("OK")
        data = response.json()
    else:
        print("NA")
        
    current_user = request.user  # Get the current user
    
    # Fetch the user's first_name and last_name
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email
    context = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
    }
    # Query your IoT model to fetch data
    items = Iot.objects.filter(user=current_user)
    if not items.exists():  # Check if there are no registered IoT devices
        no_iot_message = 'No registered IoT devices. Kindly register one first at the Crops page.'
        context['no_iot_message'] = no_iot_message
        
    else:
        # Fetch data from Firebase based on IoT code
        iot_code = items.first().code  # Assuming you want data for the first IoT code
        #print(iot_code)
        check_path = f"IOT/{iot_code}/CropsHarvested/"
        check_data = database.child(check_path).get().val()
        
        if check_data == "" :
            no_iot_message = 'No Harvested Crops yet'
            context['no_iot_message'] = no_iot_message
        else:
            # Get the keys
            keys_list = list(check_data.keys())

            # Print the keys
            print(keys_list)
            context['data'] = keys_list

    # Include the check_data in the context
    context['items'] = items
    
    return render(request, 'home/history.html', context)


@login_required
def crop_history(request, iot, data):
    response = requests.get(api_url)
    if response.status_code == 200:
        #print("OK")
        datas = response.json()
    else:
        print("NA")
        
    current_user = request.user  # Get the current user
    
    # Fetch the user's first_name and last_name
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email
    context = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
    }

    check_path = f"IOT/{iot}/CropsHarvested/{data}/CropDetails"
    check_data = database.child(check_path).get().val()
    context['details'] = check_data
    harvest = data[:10]
    context['harvest'] = harvest
    crop = check_data['cropName']
    print(crop)
    #ON OFF TABLE
    # Fetch LastOn data
    onPump_path = f"IOT/{iot}/CropsHarvested/{data}/WaterIrrigation/LastOn"
    onPump_data = database.child(onPump_path).get().val()

    # Fetch LastOff data
    offPump_path = f"IOT/{iot}/CropsHarvested/{data}/WaterIrrigation/LastOff"
    offPump_data = database.child(offPump_path).get().val()

    # Convert timestamped entries to a list of tuples (date, time)
    onPump_entries = [(date[:10], time) for date, time in onPump_data.items()]  # Extract only the date part
    offPump_entries = [(date[:10], time) for date, time in offPump_data.items()]  # Extract only the date part

    # Create a dictionary to store a list of Last Off entries by date
    off_entries_dict = {}
    for date, time in offPump_entries:
        if date in off_entries_dict:
            off_entries_dict[date].append(time)
        else:
            off_entries_dict[date] = [time]

    # Add Last Off entries to the onPump entries
    combined_entries = []
    for on_date, on_time in onPump_entries:
        off_times = off_entries_dict.get(on_date, [])
        if off_times:
            # Find the closest Last Off time to the Last On time
            closest_off_time = min(off_times, key=lambda x: abs(int(x.split(":")[0]) - int(on_time.split(":")[0])))
            combined_entries.append((on_date, on_time, on_date, closest_off_time))
        else:
            combined_entries.append((on_date, on_time, '', ''))

    context['combined_entries'] = combined_entries


    #PROGRESS REPORT

    harvest_days_path = f'IOT/{iot}/CropsHarvested/{data}/CropDetails/harvestDays'
    harvest_days_val = database.child(harvest_days_path).get().val()

    daily_pred_path = f'IOT/{iot}/CropsHarvested/{data}/{crop}/daily_prediction'
    daily_pred_val = database.child(daily_pred_path).get().val()
    # Get today's date and yesterday's date
    today_date = datetime.now().date()
    yesterday_date = today_date - timedelta(days=1)

    # Get the last recorded predictive harvest range value
    last_recorded_harvest_range = harvest_days_val if isinstance(harvest_days_val, int) else harvest_days_val.get(yesterday_date, 'N/A')

    # Update harvest_days_val based on today's prediction
    today_prediction = daily_pred_val.get(str(today_date), 'N/A')
    if today_prediction == 'GOOD':
        # If the prediction is GOOD, subtract 1 from harvest_days_val
        harvest_days_val -= 1
    elif today_prediction == 'BAD':
        # If the prediction is BAD, add 1 to harvest_days_val
        harvest_days_val += 1

    # Retrieve predictive harvest range values from Firebase
    harvest_days_recs_path = f'IOT/{iot}/CropsHarvested/{data}/{crop}/harvestdays_recs'
    harvest_days_recs_val = database.child(harvest_days_recs_path).get().val()
    # Create a dictionary for each day's data
    predict = [{'date': dates,
            'prediction': prediction,
            'days_progress': '-1 day' if prediction == 'GOOD' else '+1 day' if prediction == 'BAD' else 'No change',  # Adjust for the previous day
            'predictive_harvest_range': harvest_days_recs_val.get(dates, 'N/A')}  # Get value from harvestdays_recs for the current date
            for dates, prediction in daily_pred_val.items()]
    
    context['data'] = predict
    return render(request, 'home/crop_history.html', context)
