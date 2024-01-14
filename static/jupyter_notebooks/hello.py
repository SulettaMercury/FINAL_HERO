from flask import Flask, jsonify, request
import time
#from sklearn.impute import SimpleImputer
from datetime import datetime, timedelta
from sklearn.neighbors import KNeighborsClassifier
import pyrebase
import os
import joblib
import numpy as np
import requests


app = Flask(__name__)


# Initialize Firebase
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

firebase = pyrebase.initialize_app(config)
database = firebase.database()

# Model paths
mustasa_model_path = os.path.join(os.path.dirname(__file__),'knn_mustasa_prediction_model.joblib')
petchay_model_path = os.path.join(os.path.dirname(__file__), 'knn_petchay_prediction_model.joblib')
kangkong_model_path = os.path.join(os.path.dirname(__file__), 'knn_kangkong_prediction_model.joblib')

# irrigation pump prediction
mustasa_model_pump_status = os.path.join(os.path.dirname(__file__), 'knn_mustasa_pump_model.joblib')
petchay_model_pump_status = os.path.join(os.path.dirname(__file__), 'knn_petchay_pump_model.joblib')
kangkong_model_pump_status = os.path.join(os.path.dirname(__file__), 'knn_kangkong_pump_model.joblib')

# Load models
if os.path.exists(mustasa_model_path):
    knn_mustasa = joblib.load(mustasa_model_path)
else:
    print(f"File not found: {mustasa_model_path}")
    knn_mustasa = KNeighborsClassifier(n_neighbors=5, metric='euclidean', p=2)


if os.path.exists(kangkong_model_path):
    knn_kangkong = joblib.load(kangkong_model_path)
else:
    print(f"File not found: {kangkong_model_path}")
    knn_kangkong = KNeighborsClassifier(n_neighbors=5, metric='euclidean', p=2)


if os.path.exists(petchay_model_path):
    knn_petchay = joblib.load(petchay_model_path)
else:
    print(f"File not found: {petchay_model_path}")
    knn_petchay = KNeighborsClassifier(n_neighbors=5, metric='euclidean', p=2)


#pump irrigation
if os.path.exists(mustasa_model_pump_status):
    knn_mustasa_pump = joblib.load(mustasa_model_pump_status)
else:
    print(f"File not found: {mustasa_model_pump_status}")
    knn_mustasa_pump = KNeighborsClassifier(n_neighbors=5, metric='euclidean', p=2)

if os.path.exists(petchay_model_pump_status):
    knn_petchay_pump = joblib.load(petchay_model_pump_status)
else:
    print(f"File not found: {petchay_model_pump_status}")
    knn_petchay_pump = KNeighborsClassifier(n_neighbors=5, metric='euclidean', p=2)

if os.path.exists(kangkong_model_pump_status):
    knn_kangkong_pump = joblib.load(kangkong_model_pump_status)
else:
    print(f"File not found: {kangkong_model_pump_status}")
    knn_kangkong_pump = KNeighborsClassifier(n_neighbors=5, metric='euclidean', p=2)



# Mapping dictionary for classification
variety_mapping = {0: 'GOOD', 1: 'BAD'}


pump_mapping = {0: '0', 1: '1'}

latest_petchay_sd_value = None
latest_petchay_temp_value = None
latest_petchay_humid_value = None


latest_mustasa_sd_value = None
latest_mustasa_temp_value = None
latest_mustasa_humid_value = None


latest_kangkong_sd_value = None
latest_kangkong_temp_value = None
latest_kangkong_humid_value = None


def handle_soil_moisture(crop_type, sd_value):
    

    global latest_petchay_sd_value
    global latest_mustasa_sd_value
    global latest_kangkong_sd_value

    
    if crop_type == 'Petchay' and sd_value != latest_petchay_sd_value:

        latest_petchay_sd_value = sd_value
        print("PETCHAY SD:",latest_petchay_sd_value)
        return latest_petchay_sd_value
    
    if crop_type == 'Mustasa' and sd_value != latest_mustasa_sd_value:

        latest_mustasa_sd_value = sd_value
        print("MUSTASA SD:",latest_mustasa_sd_value)
        return latest_mustasa_sd_value
    
    if crop_type == 'Kangkong' and sd_value != latest_kangkong_sd_value:

        latest_kangkong_sd_value = sd_value
        print("KANGKONG SD:",latest_kangkong_sd_value)
        return latest_kangkong_sd_value
    


def handle_temperature(temp_value):
    
    global latest_petchay_temp_value
    global latest_mustasa_temp_value
    global latest_kangkong_temp_value
    
    if temp_value != latest_petchay_temp_value:
        latest_petchay_temp_value = temp_value
        print("PETCHAY TEMP:",latest_petchay_temp_value)
        return latest_petchay_temp_value
    
    if temp_value != latest_mustasa_temp_value:
        latest_mustasa_temp_value = temp_value
        print("MUSTASA TEMP:",latest_mustasa_temp_value)
        return latest_mustasa_temp_value
    
    if temp_value != latest_kangkong_temp_value:
        latest_kangkong_temp_value = temp_value
        print("MUSTASA TEMP:",latest_kangkong_temp_value)
        return latest_kangkong_temp_value

        


def handle_humidity(humid_value):
    
    global latest_petchay_humid_value
    global latest_mustasa_humid_value
    global latest_kangkong_humid_value
    
    if humid_value != latest_petchay_humid_value:
        latest_petchay_humid_value = humid_value
        print("PETCHAY HUMID:", latest_petchay_humid_value)
        return latest_petchay_humid_value
    
    if humid_value != latest_mustasa_humid_value:
        latest_mustasa_humid_value = humid_value
        print("MUSTASA HUMID:", latest_mustasa_humid_value)
        return latest_mustasa_humid_value

    if humid_value != latest_kangkong_humid_value:
        latest_kangkong_humid_value = humid_value
        print("MUSTASA HUMID:", latest_kangkong_humid_value)
        return latest_kangkong_humid_value



   
def stream_handler(iot_code, sensor, data_type, message):
    
    global current_good_class_count_petchay, current_bad_class_count_petchay, latest_petchay_temp_value, latest_petchay_humid_value, latest_petchay_sd_value
    global current_good_class_count_mustasa, current_bad_class_count_mustasa, latest_mustasa_temp_value, latest_mustasa_humid_value, latest_mustasa_sd_value
    global current_good_class_count_kangkong, current_bad_class_count_kangkong, latest_kangkong_temp_value, latest_kangkong_humid_value, latest_kangkong_sd_value


    
    
    crop_type = database.child('IOT').child(iot_code).child(sensor).child('CropDetails').child('cropName').get().val()
    soil_level = database.child('IOT').child(iot_code).child(sensor).child('SD').child('SML').get().val()
    
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    notif_stat = "UNREAD"
    
    data = {
        "cropName" : crop_type,
        "datetime" : current_date,
        "soil_level" : soil_level,
        "notif_stat" : notif_stat,
        "sensor_no" : sensor,
    }

    if 'data' in message and message['data'] is not None:
        data_value = message['data']

        if isinstance(data_value, (int, float)):
            # If data is already a number, use it directly
            value = data_value
        elif isinstance(data_value, dict):
            # If data is a dictionary, extract the first numeric value
            for key, value in data_value.items():
                if isinstance(value, (int, float)):
                    break
        else:
            # If data is not a number, handle it accordingly (modify as needed)
            value = 0  # Replace with your desired default value or handling

        if data_type == 'SD':
            handle_soil_moisture(crop_type, value)
        elif data_type == 'TEMP':
            handle_temperature(value)
        elif data_type == 'HUMID':
            handle_humidity(value)
            
            
         
    if crop_type == 'Mustasa':
        
        class_path = f'IOT/{iot_code}/{sensor}/{crop_type}/classification_report'
        daily_pred_path = f'IOT/{iot_code}/{sensor}/{crop_type}/daily_prediction'
        harvesrdays_records = f'IOT/{iot_code}/{sensor}/{crop_type}/harvestdays_recs'

        

        harvest_days_path = f'IOT/{iot_code}/{sensor}/CropDetails/harvestDays'
        
        water_pump_path = f'IOT/{iot_code}/{sensor}/WaterIrrigation'

        current_good_class_count_mustasa = database.child(class_path).child('good_class_count').get().val() or 0
        current_bad_class_count_mustasa = database.child(class_path).child('bad_class_count').get().val() or 0
        
        

        # Check if there's new input from temperature or humidity or soil moisture
        if latest_mustasa_temp_value is not None or latest_mustasa_humid_value is not None or latest_mustasa_sd_value is not None:
            # Check if any of the values is None and fetch the latest values from the database if needed
            latest_mustasa_temp_value = latest_mustasa_temp_value or database.child('IOT').child(iot_code).child('STATIC').child('TEMP').get().val()
            latest_mustasa_humid_value = latest_mustasa_humid_value or database.child('IOT').child(iot_code).child('STATIC').child('HUMID').get().val()
            latest_mustasa_sd_value = latest_mustasa_sd_value or database.child('IOT').child(iot_code).child(sensor).child('SD').child('SML').get().val()

            # Check if soil moisture is 0
            if latest_mustasa_sd_value == 0:
                print("No soil moisture detected. Please check your sensors.")
            else:
                input_mustasa_data = np.array([[latest_mustasa_temp_value, latest_mustasa_humid_value, latest_mustasa_sd_value]])
                mustasa_prediction_label = knn_mustasa.predict(input_mustasa_data)[0]
                predicted_output_mustasa = variety_mapping.get(mustasa_prediction_label, 'Unknown')
                
                # Predict pump irrigation status for petchay
                mustasa_pump_status = knn_mustasa_pump.predict(input_mustasa_data)[0]
                predicted_pumpStat_mustasa = pump_mapping.get(mustasa_pump_status, 'Unknown')
        
                print("Predicted Pump Irrigation Status for Mustasa:", predicted_pumpStat_mustasa)
                
                # Get the current date as a string
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if predicted_pumpStat_mustasa == 1:
                    # Update Firebase path to 1
                    database.child(water_pump_path).child('Switch').set(predicted_pumpStat_mustasa)
                else:
                    # If the prediction is not 1, update Firebase path to the predicted value
                    database.child(water_pump_path).child('Switch').set(predicted_pumpStat_mustasa)
                
                # Update counts based on prediction
                if predicted_output_mustasa == 'GOOD':
                    current_good_class_count_mustasa += 1
                elif predicted_output_mustasa == 'BAD':
                    current_bad_class_count_mustasa += 1

                # Store counts in Firebase under the correct user's path
                class_path = f'IOT/{iot_code}/{sensor}/{crop_type}/classification_report'
                database.child(class_path).child('good_class_count').set(current_good_class_count_mustasa)
                database.child(class_path).child('bad_class_count').set(current_bad_class_count_mustasa)
                    
                initial_date = datetime.now().strftime("%Y-%m-%d")

                # Get the current date
                current_date = datetime.now()
                formatted_current_date = current_date.strftime("%Y-%m-%d")  # Corrected format to "mm-dd-yyyy"
                
                # Get the date of yesterday
                yesterday_date = current_date - timedelta(days=1)
                formatted_yesterday_date = yesterday_date.strftime("%Y-%m-%d")
                
                # Calculate the date for tomorrow
                tomorrow_date = current_date + timedelta(days=1)

                # Format the date as "mm-dd-yyyy"
                formatted_tomorrow_date = tomorrow_date.strftime("%Y-%m-%d")
                
                date_yesterday = database.child(daily_pred_path).order_by_key().limit_to_last(1).get().val()

                
                if date_yesterday:
                    date_yesterday_key = list(date_yesterday.keys())[0]
                    print("Latest Date:", date_yesterday_key)
                else:
                    print("No data available in the daily_prediction path.")
                

                # Compare counts and set crop_growth_health if the day has ended
                if date_yesterday_key != formatted_yesterday_date:
                    
                    mustasa_good_class_count = database.child(class_path).child('good_class_count').get().val() or 0
                    mustasa_bad_class_count = database.child(class_path).child('bad_class_count').get().val() or 0
                    
                    # Compare counts and set crop_growth_health
                    if mustasa_good_class_count > mustasa_bad_class_count:
                        mustasa_crop_growth_health = 'GOOD'
                        database.child(class_path).child('crop_growth_health').set(mustasa_crop_growth_health)
                    elif mustasa_bad_class_count > mustasa_good_class_count:
                        mustasa_crop_growth_health = 'BAD'
                        database.child(class_path).child('crop_growth_health').set(mustasa_crop_growth_health)
                    else:
                        # If counts are equal, keep the current value mustasa
                        mustasa_current_growth_health = database.child(class_path).child('crop_growth_health').get().val()
                        mustasa_crop_growth_health = 'UNKNOWN' if mustasa_current_growth_health is None else mustasa_current_growth_health
                        
                    # Set daily prediction in the format "12-03-2023 : GOOD"
                    mustasa_prediction_for_day = f"{formatted_yesterday_date}"
                    output = f"{mustasa_crop_growth_health}"
                    database.child(daily_pred_path).child(mustasa_prediction_for_day).set(output)
                    
                    # Get the prediction from yesterday
                    yesterday_date_mustasa_prediction = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                    mustasa_prediction_yesterday = database.child(daily_pred_path).child(yesterday_date_mustasa_prediction).get().val()
                    print(mustasa_prediction_yesterday)
                
                
                    # Update harvestDays based on the result
                    current_harvest_days = database.child(harvest_days_path).get().val()
                    if current_harvest_days is not None:
                        if mustasa_crop_growth_health == 'GOOD':
                            current_harvest_days -= 1  # Minus 1 if crop_growth_health is GOOD
                        elif mustasa_crop_growth_health == 'BAD':
                            current_harvest_days += 1  # Add 1 if crop_growth_health is BAD
                        database.child(harvest_days_path).set(current_harvest_days)
                        day = f"{formatted_yesterday_date}"
                        database.child(harvesrdays_records).child(day).set(current_harvest_days)

                    # Reset counts for the new day
                    database.child(class_path).child('good_class_count').set(0)
                    database.child(class_path).child('bad_class_count').set(0)
                    
                    initial_date = formatted_current_date
                
                else:
                    mustasa_pump_status = knn_mustasa_pump.predict(input_mustasa_data)[0]
                    predicted_pumpStat_mustasa = pump_mapping.get(mustasa_pump_status, 'Unknown')

                    print("Predicted Pump Irrigation Status for Mustasa:", predicted_pumpStat_mustasa)

                    # Check if the prediction is 1
                    if predicted_pumpStat_mustasa != "1":
                        # Update the water pump status
                        database.child(water_pump_path).child('Switch').set(0)
                        
                        # Reset the notification flag when the prediction changes to 0
                        database.child('IOT').child(iot_code).child('Notification').child('PumpOnNotified').set(False)

                        # Check if the notification has already been sent
                        if not database.child('IOT').child(iot_code).child('Notification').child('PumpOffNotified').get().val():
                            # Set the notification flag to true
                            database.child('IOT').child(iot_code).child('Notification').child('PumpOffNotified').set(True)
                            
                            
                            
                            # Send the notification for PumpOff
                            current_timestamp = int(time.time())
                            firebase_path = f'IOT/{iot_code}/Notifications/WaterPumpOff/{current_timestamp}'
                            
                            # Set data at the new path
                            database.child(firebase_path).set(data)
                    
                    
                    else:
                        
                        # Reset the notification flag when the prediction changes to 0
                        database.child('IOT').child(iot_code).child('Notification').child('PumpOffNotified').set(False)

                        
                        # Check if the notification flag is not set
                        if not database.child('IOT').child(iot_code).child('Notification').child('PumpOnNotified').get().val():
                            # Set the notification flag to true
                            database.child('IOT').child(iot_code).child('Notification').child('PumpOnNotified').set(True)
                            
                            # Update the water pump status
                            database.child(water_pump_path).child('Switch').set(predicted_pumpStat_mustasa)
                            
                            # Send the notification for PumpOn
                            current_timestamp = int(time.time())
                            firebase_path = f'IOT/{iot_code}/Notifications/WaterPumpOn/{current_timestamp}'
                            
                            # Set data at the new path
                            database.child(firebase_path).set(data)
                    
    
    elif crop_type == 'Petchay':
        

        
        
        class_path = f'IOT/{iot_code}/{sensor}/{crop_type}/classification_report'
        daily_pred_path = f'IOT/{iot_code}/{sensor}/{crop_type}/daily_prediction'
        harvesrdays_records = f'IOT/{iot_code}/{sensor}/{crop_type}/harvestdays_recs'
        
        
        
        harvest_days_path = f'IOT/{iot_code}/{sensor}/CropDetails/harvestDays'
        
        water_pump_path = f'IOT/{iot_code}/{sensor}/WaterIrrigation'


        current_good_class_count_petchay = database.child(class_path).child('good_class_count').get().val() or 0
        current_bad_class_count_petchay = database.child(class_path).child('bad_class_count').get().val() or 0

        # Check if there's new input from temperature or humidity or soil moisture
        if latest_petchay_temp_value is not None or latest_petchay_humid_value is not None or latest_petchay_sd_value is not None:
            # Check if any of the values is None and fetch the latest values from the database if needed
            latest_petchay_temp_value = latest_petchay_temp_value or database.child('IOT').child(iot_code).child('STATIC').child('TEMP').get().val()
            latest_petchay_humid_value = latest_petchay_humid_value or database.child('IOT').child(iot_code).child('STATIC').child('HUMID').get().val()
            latest_petchay_sd_value = latest_petchay_sd_value or database.child('IOT').child(iot_code).child(sensor).child('SD').child('SML').get().val()

            # Check if soil moisture is 0
                    
            if latest_petchay_sd_value == 0:
                print("No soil moisture detected. Please check your sensors.")
            else:
                input_petchay_data = np.array([[latest_petchay_temp_value, latest_petchay_humid_value, latest_petchay_sd_value]])
                petchay_prediction_label = knn_petchay.predict(input_petchay_data)[0]
                predicted_output_petchay = variety_mapping.get(petchay_prediction_label, 'Unknown')
                
                # Predict pump irrigation status for petchay
                petchay_pump_status = knn_petchay_pump.predict(input_petchay_data)[0]
                predicted_pumpStat_petchay = pump_mapping.get(petchay_pump_status, 'Unknown')
        
                print("Predicted Pump Irrigation Status for Petchay:", predicted_pumpStat_petchay)
                
                # Get the current date as a string
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if predicted_pumpStat_petchay == 1:
                    # Update Firebase path to 1
                    database.child(water_pump_path).child('Switch').set(predicted_pumpStat_petchay)
                else:
                    # If the prediction is not 1, update Firebase path to the predicted value
                    database.child(water_pump_path).child('Switch').set(predicted_pumpStat_petchay)

                # Update counts based on prediction
                if predicted_output_petchay == 'GOOD':
                    current_good_class_count_petchay += 1
                elif predicted_output_petchay == 'BAD':
                    current_bad_class_count_petchay += 1

                # Store counts in Firebase under the correct user's path
                class_path = f'IOT/{iot_code}/{sensor}/{crop_type}/classification_report'
                database.child(class_path).child('good_class_count').set(current_good_class_count_petchay)
                database.child(class_path).child('bad_class_count').set(current_bad_class_count_petchay)
                
                initial_date = datetime.now().strftime("%Y-%m-%d")

                # Get the current date
                current_date = datetime.now()
                formatted_current_date = current_date.strftime("%Y-%m-%d")  # Corrected format to "mm-dd-yyyy"
                
                # Get the date of yesterday
                yesterday_date = current_date - timedelta(days=1)
                formatted_yesterday_date = yesterday_date.strftime("%Y-%m-%d")
                
                # Calculate the date for tomorrow
                tomorrow_date = current_date + timedelta(days=1)

                # Format the date as "mm-dd-yyyy"
                formatted_tomorrow_date = tomorrow_date.strftime("%Y-%m-%d")
    
                date_yesterday = database.child(daily_pred_path).order_by_key().limit_to_last(1).get().val()

                
                if date_yesterday:
                    date_yesterday_key = list(date_yesterday.keys())[0]
                    print("Latest Date:", date_yesterday_key)
                else:
                    print("No data available in the daily_prediction path.")
                

                # Compare counts and set crop_growth_health if the day has ended
                if date_yesterday_key != formatted_yesterday_date:
                    
                    petchay_good_class_count = database.child(class_path).child('good_class_count').get().val() or 0
                    petchay_bad_class_count = database.child(class_path).child('bad_class_count').get().val() or 0
                    
                    # Compare counts and set crop_growth_health
                    if petchay_good_class_count > petchay_bad_class_count:
                        petchay_crop_growth_health = 'GOOD'
                        database.child(class_path).child('crop_growth_health').set(petchay_crop_growth_health)
                    elif petchay_bad_class_count > petchay_good_class_count:
                        petchay_crop_growth_health = 'BAD'
                        database.child(class_path).child('crop_growth_health').set(petchay_crop_growth_health)
                    else:
                        # If counts are equal, keep the current value
                        petchay_current_growth_health = database.child(class_path).child('crop_growth_health').get().val()
                        petchay_crop_growth_health = 'UNKNOWN' if petchay_current_growth_health is None else petchay_current_growth_health
                        
                    # Set daily prediction in the format "12-03-2023 : GOOD"
                    petchay_prediction_for_day = f"{formatted_yesterday_date}"
                    output = f"{petchay_crop_growth_health}"
                    database.child(daily_pred_path).child(petchay_prediction_for_day).set(output)
                    
                    # Get the prediction from yesterday
                    yesterday_date_petchay_prediction = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                    petchay_prediction_yesterday = database.child(daily_pred_path).child(yesterday_date_petchay_prediction).get().val()
                    print(petchay_prediction_yesterday)
                
                
                    # Update harvestDays based on the result
                    current_harvest_days = database.child(harvest_days_path).get().val()
                    if current_harvest_days is not None:
                        if petchay_crop_growth_health == 'GOOD':
                            current_harvest_days -= 1  # Minus 1 if crop_growth_health is GOOD
                            
                        elif petchay_crop_growth_health == 'BAD':
                            current_harvest_days += 1  # Add 1 if crop_growth_health is BAD
                        database.child(harvest_days_path).set(current_harvest_days)                        
                        day = f"{formatted_yesterday_date}"
                        database.child(harvesrdays_records).child(day).set(current_harvest_days)

                    # Reset counts for the new day
                    database.child(class_path).child('good_class_count').set(0)
                    database.child(class_path).child('bad_class_count').set(0)
                    
                    initial_date = formatted_current_date
                else:
                    
                    petchay_pump_status = knn_petchay_pump.predict(input_petchay_data)[0]
                    predicted_pumpStat_petchay = pump_mapping.get(petchay_pump_status, 'Unknown')

                    print("Predicted Pump Irrigation Status for Mustasa:", predicted_pumpStat_petchay)

                    # Check if the prediction is 1
                    if predicted_pumpStat_petchay != "1":
                        # Update the water pump status
                        database.child(water_pump_path).child('Switch').set(0)
                        
                        # Reset the notification flag when the prediction changes to 0
                        database.child('IOT').child(iot_code).child('Notification').child('PumpOnNotified').set(False)

                        # Check if the notification has already been sent
                        if not database.child('IOT').child(iot_code).child('Notification').child('PumpOffNotified').get().val():
                            # Set the notification flag to true
                            database.child('IOT').child(iot_code).child('Notification').child('PumpOffNotified').set(True)
                            
                            
                            
                            # Send the notification for PumpOff
                            current_timestamp = int(time.time())
                            firebase_path = f'IOT/{iot_code}/Notifications/WaterPumpOff/{current_timestamp}'
                            
                            # Set data at the new path
                            database.child(firebase_path).set(data)
                    
                    
                    else:
                        
                        # Reset the notification flag when the prediction changes to 0
                        database.child('IOT').child(iot_code).child('Notification').child('PumpOffNotified').set(False)

                        
                        # Check if the notification flag is not set
                        if not database.child('IOT').child(iot_code).child('Notification').child('PumpOnNotified').get().val():
                            # Set the notification flag to true
                            database.child('IOT').child(iot_code).child('Notification').child('PumpOnNotified').set(True)
                            
                            # Update the water pump status
                            database.child(water_pump_path).child('Switch').set(predicted_pumpStat_petchay)
                            
                            # Send the notification for PumpOn
                            current_timestamp = int(time.time())
                            firebase_path = f'IOT/{iot_code}/Notifications/WaterPumpOn/{current_timestamp}'
                            
                            # Set data at the new path
                            database.child(firebase_path).set(data)    
        
    elif crop_type == 'Kangkong':
        
        class_path = f'IOT/{iot_code}/{sensor}/{crop_type}/classification_report' 
        daily_pred_path = f'IOT/{iot_code}/{sensor}/{crop_type}/daily_prediction'
        harvesrdays_records = f'IOT/{iot_code}/{sensor}/{crop_type}/harvestdays_recs'

        

        harvest_days_path = f'IOT/{iot_code}/{sensor}/CropDetails/harvestDays'
        
        water_pump_path = f'IOT/{iot_code}/{sensor}/WaterIrrigation'

        current_good_class_count_kangkong = database.child(class_path).child('good_class_count').get().val() or 0
        current_bad_class_count_kangkong = database.child(class_path).child('bad_class_count').get().val() or 0

        # Check if there's new input from temperature or humidity or soil moisture
        if latest_kangkong_temp_value is not None or latest_kangkong_humid_value is not None or latest_kangkong_sd_value is not None:
            # Check if any of the values is None and fetch the latest values from the database if needed
            latest_kangkong_temp_value = latest_kangkong_temp_value or database.child('IOT').child(iot_code).child('STATIC').child('TEMP').get().val()
            latest_kangkong_humid_value = latest_kangkong_humid_value or database.child('IOT').child(iot_code).child('STATIC').child('HUMID').get().val()
            latest_kangkong_sd_value = latest_kangkong_sd_value or database.child('IOT').child(iot_code).child(sensor).child('SD').child('SML').get().val()

            # Check if soil moisture is 0
            if latest_kangkong_sd_value == 0:
                print("No soil moisture detected. Please check your sensors.")
            else:
                input_kangkong_data = np.array([[latest_kangkong_temp_value, latest_kangkong_humid_value, latest_kangkong_sd_value]])
                kangkong_prediction_label = knn_kangkong.predict(input_kangkong_data)[0]
                predicted_output_kangkong = variety_mapping.get(kangkong_prediction_label, 'Unknown')
                
                # Predict pump irrigation status for petchay
                kangkong_pump_status = knn_kangkong_pump.predict(input_kangkong_data)[0]
                predicted_pumpStat_kangkong = pump_mapping.get(kangkong_pump_status, 'Unknown')
        
                print("Predicted Pump Irrigation Status for Petchay:", predicted_pumpStat_kangkong)
                
                # Get the current date as a string
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if predicted_pumpStat_kangkong == 1:
                    # Update Firebase path to 1
                    database.child(water_pump_path).child('Switch').set(predicted_pumpStat_kangkong)
                else:
                    # If the prediction is not 1, update Firebase path to the predicted value
                    database.child(water_pump_path).child('Switch').set(predicted_pumpStat_kangkong)
                
                # Update counts based on prediction
                if predicted_output_kangkong == 'GOOD':
                    current_good_class_count_kangkong += 1
                elif predicted_output_kangkong == 'BAD':
                    current_bad_class_count_kangkong += 1

                # Store counts in Firebase under the correct user's path
                class_path = f'IOT/{iot_code}/{sensor}/{crop_type}/classification_report'
                database.child(class_path).child('good_class_count').set(current_good_class_count_kangkong)
                database.child(class_path).child('bad_class_count').set(current_bad_class_count_kangkong)
                
                
                initial_date = datetime.now().strftime("%Y-%m-%d")
        
                # Get the current date
                current_date = datetime.now()
                formatted_current_date = current_date.strftime("%Y-%m-%d")  # Corrected format to "mm-dd-yyyy"
                
                # Get the date of yesterday
                yesterday_date = current_date - timedelta(days=1)
                formatted_yesterday_date = yesterday_date.strftime("%Y-%m-%d")

                # Calculate the date for tomorrow
                tomorrow_date = current_date + timedelta(days=1)

                # Format the date as "mm-dd-yyyy"
                formatted_tomorrow_date = tomorrow_date.strftime("%Y-%m-%d")
                
                date_yesterday = database.child(daily_pred_path).order_by_key().limit_to_last(1).get().val()

                
                if date_yesterday:
                    date_yesterday_key = list(date_yesterday.keys())[0]
                    print("Latest Date:", date_yesterday_key)
                else:
                    print("No data available in the daily_prediction path.")
                

                # Compare counts and set crop_growth_health if the day has ended
                if date_yesterday_key != formatted_yesterday_date:
            
                    kangkong_good_class_count = database.child(class_path).child('good_class_count').get().val() or 0
                    kangkong_bad_class_count = database.child(class_path).child('bad_class_count').get().val() or 0
                    
                    # Compare counts and set crop_growth_health
                    if kangkong_good_class_count > kangkong_bad_class_count:
                        kangkong_crop_growth_health = 'GOOD'
                        database.child(class_path).child('crop_growth_health').set(kangkong_crop_growth_health)
                    elif kangkong_bad_class_count > kangkong_good_class_count:
                        kangkong_crop_growth_health = 'BAD'
                        database.child(class_path).child('crop_growth_health').set(kangkong_crop_growth_health)
                    else:
                        # If counts are equal, keep the current value mustasa
                        kangkong_current_growth_health = database.child(class_path).child('crop_growth_health').get().val()
                        kangkong_crop_growth_health = 'UNKNOWN' if kangkong_current_growth_health is None else kangkong_current_growth_health
                        
                    # Set daily prediction in the format "12-03-2023 : GOOD"
                    kangkong_prediction_for_day = f"{formatted_yesterday_date}"
                    output = f"{kangkong_crop_growth_health}"
                    database.child(daily_pred_path).child(kangkong_prediction_for_day).set(output)
                    
                    # Get the prediction from yesterday
                    yesterday_date_kangkong_prediction = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                    kangkong_prediction_yesterday = database.child(daily_pred_path).child(yesterday_date_kangkong_prediction).get().val()
                    print(kangkong_prediction_yesterday)
                
                
                    # Update harvestDays based on the result
                    current_harvest_days = database.child(harvest_days_path).get().val()
                    if current_harvest_days is not None:
                        if kangkong_crop_growth_health == 'GOOD':
                            current_harvest_days -= 1  # Minus 1 if crop_growth_health is GOOD
                        elif kangkong_crop_growth_health == 'BAD':
                            current_harvest_days += 1  # Add 1 if crop_growth_health is BAD
                        database.child(harvest_days_path).set(current_harvest_days)
                        day = f"{formatted_yesterday_date}"
                        database.child(harvesrdays_records).child(day).set(current_harvest_days)

                    # Reset counts for the new day
                    database.child(class_path).child('good_class_count').set(0)
                    database.child(class_path).child('bad_class_count').set(0)
                    
                    initial_date = formatted_current_date
                else:
                    kangkong_pump_status = knn_kangkong_pump.predict(input_kangkong_data)[0]
                    predicted_pumpStat_kangkong = pump_mapping.get(kangkong_pump_status, 'Unknown')

                    print("Predicted Pump Irrigation Status for Mustasa:", predicted_pumpStat_kangkong)

                    # Check if the prediction is 1
                    if predicted_pumpStat_kangkong != "1":
                        # Update the water pump status
                        database.child(water_pump_path).child('Switch').set(0)
                        
                        # Reset the notification flag when the prediction changes to 0
                        database.child('IOT').child(iot_code).child('Notification').child('PumpOnNotified').set(False)

                        # Check if the notification has already been sent
                        if not database.child('IOT').child(iot_code).child('Notification').child('PumpOffNotified').get().val():
                            # Set the notification flag to true
                            database.child('IOT').child(iot_code).child('Notification').child('PumpOffNotified').set(True)
                            
                            
                            
                            # Send the notification for PumpOff
                            current_timestamp = int(time.time())
                            firebase_path = f'IOT/{iot_code}/Notifications/WaterPumpOff/{current_timestamp}'
                            
                            # Set data at the new path
                            database.child(firebase_path).set(data)
                    
                    
                    else:
                        
                        # Reset the notification flag when the prediction changes to 0
                        database.child('IOT').child(iot_code).child('Notification').child('PumpOffNotified').set(False)

                        
                        # Check if the notification flag is not set
                        if not database.child('IOT').child(iot_code).child('Notification').child('PumpOnNotified').get().val():
                            # Set the notification flag to true
                            database.child('IOT').child(iot_code).child('Notification').child('PumpOnNotified').set(True)
                            
                            # Update the water pump status
                            database.child(water_pump_path).child('Switch').set(predicted_pumpStat_kangkong)
                            
                            # Send the notification for PumpOn
                            current_timestamp = int(time.time())
                            firebase_path = f'IOT/{iot_code}/Notifications/WaterPumpOn/{current_timestamp}'
                            
                            # Set data at the new path
                            database.child(firebase_path).set(data)            
            
                    



def setup_listener(iot_code, sensor, data_type):
    return database.child('IOT').child(iot_code).child(sensor).child(data_type).stream(
        lambda message, iot_code=iot_code, sensor=sensor, data_type=data_type: stream_handler(iot_code, sensor, data_type, message)
    )


@app.route('/')
def test_firebase_connection():
    try:
        # Fetch the list of registered IoT devices
        iot_devices = database.child('IOT').shallow().get().val()

        if iot_devices:
            for iot_code in iot_devices:
                # Fetch the list of sensors for each IoT device
                sensors = database.child('IOT').child(iot_code).shallow().get().val()

                if sensors:
                    for sensor in sensors:
                        # Set up listeners for changes in the specified paths
                        setup_listener(iot_code, sensor, 'SD')
                        setup_listener(iot_code, sensor, 'TEMP')
                        setup_listener(iot_code, sensor, 'HUMID')

        # Try reading a sample data from Firebase to test the connection
        data = database.child('IOT/').get().val()
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"An error occurred: {str(e)}")