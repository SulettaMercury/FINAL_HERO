from flask import Flask, jsonify, request
from sklearn.impute import SimpleImputer
from sklearn.neighbors import KNeighborsClassifier
import pyrebase
import os
import joblib
import numpy as np

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
mustasa_model_path = os.path.join(os.path.dirname(__file__), 'knn_mustasa_prediction_model.joblib')
petchay_model_path = os.path.join(os.path.dirname(__file__), 'knn_petchay_prediction_model.joblib')
kangkong_model_path = os.path.join(os.path.dirname(__file__), 'knn_kangkong_prediction_model.joblib')

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


# Mapping dictionary for classification
variety_mapping = {0: 'GOOD', 1: 'BAD'}


latest_petchay_sd_value = None
latest_petchay_temp_value = None
latest_petchay_humid_value = None

def predict_petchay_status(latest_petchay_sd_value, latest_petchay_temp_value, latest_petchay_humid_value):

    input_petchay_data = np.array([[latest_petchay_sd_value, latest_petchay_temp_value, latest_petchay_humid_value]])
    petchay_prediction_label = knn_petchay.predict(input_petchay_data)[0]
    predicted_output_petchay = variety_mapping.get(petchay_prediction_label, 'Unknown')
    return predicted_output_petchay



latest_mustasa_sd_value = None
latest_mustasa_temp_value = None
latest_mustasa_humid_value = None


def predict_mustasa_status(latest_mustasa_sd_value, latest_mustasa_temp_value, latest_mustasa_humid_value):

    input_mustasa_data = np.array([[latest_mustasa_sd_value, latest_mustasa_temp_value, latest_mustasa_humid_value]])
    mustasa_prediction_label = knn_mustasa.predict(input_mustasa_data)[0]
    predicted_output_mustasa = variety_mapping.get(mustasa_prediction_label, 'Unknown')
    return predicted_output_mustasa

latest_kangkong_sd_value = None
latest_kangkong_temp_value = None
latest_kangkong_humid_value = None

def predict_kangkong_status(latest_kangkong_sd_value, latest_kangkong_temp_value, latest_kangkong_humid_value):

    input_kangkong_data = np.array([[latest_kangkong_sd_value, latest_kangkong_temp_value, latest_kangkong_humid_value]])
    kangkong_prediction_label = knn_kangkong.predict(input_kangkong_data)[0]
    predicted_output_kangkong = variety_mapping.get(kangkong_prediction_label, 'Unknown')
    return predicted_output_kangkong



def handle_soil_moisture(iot_code, sensor, crop_type, sd_value):
    
    print("Handling soil moisture...")
    
    global latest_petchay_humid_value
    global latest_petchay_temp_value
    global latest_petchay_sd_value
    
    global latest_mustasa_sd_value
    global latest_mustasa_temp_value
    global latest_mustasa_humid_value
    
    #kangkong
    global latest_kangkong_sd_value
    global latest_kangkong_temp_value
    global latest_kangkong_humid_value
    
    
    if crop_type == 'Petchay' and sd_value != latest_petchay_sd_value:

        latest_petchay_sd_value = sd_value

        print(f"IOT CODE: {iot_code} | {sensor}")
        print(f"New SOIL MOISTURE LEVEL OF {crop_type} is {sd_value}")
        
        # Check if temperature and soil moisture values are numeric before prediction
        if isinstance(latest_petchay_temp_value, (int, float)) and isinstance(latest_petchay_humid_value, (int, float)):
            # Call predict_petchay_status to get the prediction
            predicted_output_petchay = predict_petchay_status(
                latest_petchay_sd_value,
                latest_petchay_temp_value,
                latest_petchay_humid_value
            )

            # Print the predicted output
            print("Predicted Output for Petchay:", predicted_output_petchay)
            
            # Add the print statements here or wherever you need them
            print("Latest Petchay Soil Moisture Value:", latest_petchay_sd_value)
            print("Latest Petchay Temperature Value:", latest_petchay_temp_value)
            print("Latest Petchay Humidity Value:", latest_petchay_humid_value)
    
    elif crop_type == 'Mustasa' and sd_value != latest_mustasa_sd_value:
        
        latest_mustasa_sd_value = sd_value

        print(f"IOT CODE: {iot_code} | {sensor}")
        print(f"New SOIL MOISTURE LEVEL OF {crop_type} is {sd_value}")
        
        # Check if temperature and soil moisture values are numeric before prediction
        if isinstance(latest_mustasa_temp_value, (int, float)) and isinstance(latest_mustasa_humid_value, (int, float)):
            # Call predict_petchay_status to get the prediction
            predicted_output_mustasa = predict_mustasa_status(
                latest_mustasa_sd_value,
                latest_mustasa_temp_value,
                latest_mustasa_humid_value
            )

            # Print the predicted output
            print("Predicted Output for Mustasa:", predicted_output_mustasa)
            
    elif crop_type == 'Kangkong' and sd_value != latest_kangkong_sd_value:
        
        latest_kangkong_sd_value = sd_value

        print(f"IOT CODE: {iot_code} | {sensor}")
        print(f"New SOIL MOISTURE LEVEL OF {crop_type} is {sd_value}")
        
        # Check if temperature and soil moisture values are numeric before prediction
        if isinstance(latest_kangkong_temp_value, (int, float)) and isinstance(latest_kangkong_humid_value, (int, float)):
            # Call predict_petchay_status to get the prediction
            predicted_output_kangkong = predict_kangkong_status(
                latest_kangkong_sd_value,
                latest_kangkong_temp_value,
                latest_kangkong_humid_value
            )

            # Print the predicted output
            print("Predicted Output for Kangkong:", predicted_output_kangkong)

def handle_temperature(temp_value):
    
    global latest_petchay_humid_value
    global latest_petchay_temp_value
    global latest_petchay_sd_value
    
    global latest_mustasa_sd_value
    global latest_mustasa_temp_value
    global latest_mustasa_humid_value
    
    #kangkong
    global latest_kangkong_sd_value
    global latest_kangkong_temp_value
    global latest_kangkong_humid_value

    
    if temp_value != latest_petchay_temp_value:
        latest_petchay_temp_value = temp_value
        print("TEMPERATURE:", temp_value)
        
        
        # Check if temperature and soil moisture values are numeric before prediction
        if isinstance(latest_petchay_humid_value, (int, float)) and isinstance(latest_petchay_sd_value, (int, float)):
            # Call predict_petchay_status to get the prediction
            predicted_output_petchay = predict_petchay_status(
                latest_petchay_sd_value,
                latest_petchay_temp_value,
                latest_petchay_humid_value
            )

            # Print the predicted output
            print("Predicted Output for Petchay:", predicted_output_petchay)
            
    if temp_value != latest_mustasa_temp_value:
        latest_mustasa_temp_value = temp_value
        print("TEMPERATURE:", temp_value)
        
        
        # Check if temperature and soil moisture values are numeric before prediction
        if isinstance(latest_mustasa_humid_value, (int, float)) and isinstance(latest_mustasa_sd_value, (int, float)):
            # Call predict_petchay_status to get the prediction
            predicted_output_mustasa = predict_mustasa_status(
                latest_mustasa_sd_value,
                latest_mustasa_temp_value,
                latest_mustasa_humid_value
            )
            # Print the predicted output
            print("Predicted Output for Mustasa:", predicted_output_mustasa)
            
    if temp_value != latest_kangkong_temp_value:
        latest_kangkong_temp_value = temp_value
        print("TEMPERATURE:", temp_value)
        
        
        # Check if temperature and soil moisture values are numeric before prediction
        if isinstance(latest_kangkong_humid_value, (int, float)) and isinstance(latest_kangkong_sd_value, (int, float)):
            # Call predict_petchay_status to get the prediction
            predicted_output_kangkong = predict_kangkong_status(
                latest_kangkong_sd_value,
                latest_kangkong_temp_value,
                latest_kangkong_humid_value
            )

            # Print the predicted output
            print("Predicted Output for Kangkong:", predicted_output_kangkong)
        


def handle_humidity(humid_value):
    
    global latest_petchay_humid_value
    global latest_petchay_temp_value
    global latest_petchay_sd_value
    
    global latest_mustasa_sd_value
    global latest_mustasa_temp_value
    global latest_mustasa_humid_value
    
    
    #kangkong
    global latest_kangkong_sd_value
    global latest_kangkong_temp_value
    global latest_kangkong_humid_value


    if humid_value != latest_petchay_humid_value:
        latest_petchay_humid_value = humid_value
        print("HUMIDITY:", humid_value)

        # Check if temperature and soil moisture values are numeric before prediction
        if isinstance(latest_petchay_temp_value, (int, float)) and isinstance(latest_petchay_sd_value, (int, float)):
            # Call predict_petchay_status to get the prediction
            predicted_output_petchay = predict_petchay_status(
                latest_petchay_sd_value,
                latest_petchay_temp_value,
                latest_petchay_humid_value
            )

            # Print the predicted output
            print("Predicted Output for Petchay:", predicted_output_petchay)
            
    
    if humid_value != latest_mustasa_humid_value:
        latest_mustasa_humid_value = humid_value
        print("HUMIDITY:", humid_value)
        
        # Check if temperature and soil moisture values are numeric before prediction
        if isinstance(latest_mustasa_temp_value, (int, float)) and isinstance(latest_mustasa_sd_value, (int, float)):
            # Call predict_petchay_status to get the prediction
            predicted_output_mustasa = predict_mustasa_status(
                latest_mustasa_sd_value,
                latest_mustasa_temp_value,
                latest_mustasa_humid_value
            )
            # Print the predicted output
            print("Predicted Output for Mustasa:", predicted_output_mustasa)
            
            
    if humid_value != latest_kangkong_humid_value:
        latest_kangkong_humid_value = humid_value
        print("HUMIDITY:", humid_value)

        # Check if temperature and soil moisture values are numeric before prediction
        if isinstance(latest_kangkong_temp_value, (int, float)) and isinstance(latest_kangkong_sd_value, (int, float)):
            # Call predict_petchay_status to get the prediction
            predicted_output_kangkong = predict_kangkong_status(
                latest_kangkong_sd_value,
                latest_kangkong_temp_value,
                latest_kangkong_humid_value
            )

            # Print the predicted output
            print("Predicted Output for Kangkong:", predicted_output_kangkong)

def stream_handler(iot_code, sensor, data_type, message):
    
    crop_type = database.child('IOT').child(iot_code).child(sensor).child('CropDetails').child('cropName').get().val()

    if 'data' in message and message['data'] is not None:
        
        if data_type == 'SD':
            handle_soil_moisture(iot_code, sensor, crop_type, message['data'])
        elif data_type == 'TEMP':
            handle_temperature(message['data'])
        elif data_type == 'HUMID':
            handle_humidity(message['data'])
            
            



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