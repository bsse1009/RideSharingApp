import requests
import random
import time
import socketio

BASE1 = "http://127.0.0.1:5000/"
BASE2 = "http://127.0.0.1:5003/"

rider_data = ["Ibrahim", "Purbo", "mahdee", "Nirab", "Yasin", "Ahsan", "Sobah", "Sakib"]
driver_data = [["Ikram", "Dhaka1009"], ["Moaj", "Dhaka1111"], ["Karim", "CHA122"], ["Basir", "SYL111032"],
               ["Ifti", "SYL9001"], ["Pranto", "RAJ1026"]]


sio = socketio.Client()
sio.connect(BASE2, namespaces=['/communication'])


@sio.event(namespace='/communication')
def message(data):
    print('received message: Rider ' + data['rider_name'] + 'is assigned to Driver ' + data['driver_name'])
    print(f'Your Fare is: {data["fare"]}')
    driver_rating = {
        "_id": data['driver_id'],
        "name": data['driver_name'],
        "rating": random.randint(0, 5),
    }
    response = requests.post(BASE1+'rating', driver_rating)
    print(response.json())


for i in range(10):
    rider_id = i % len(rider_data)
    driver_id = i % len(driver_data)
    rider_name = rider_data[rider_id]
    driver_name = driver_data[driver_id][0]
    car_number = driver_data[driver_id][1]

    current_location = [random.random()*10, random.random()*10]
    destination = [random.random()*30, random.random()*30]
    driver_coordinate = [random.random()*25, random.random()*25]

    rider = {
        "id": rider_id,
        "name": rider_name,
        "current_location": current_location,
        "destination": destination
    }

    driver = {
        "id": driver_id,
        "name": driver_name,
        "car_number": car_number,
        "current_location": driver_coordinate
    }

    response = requests.post(BASE1+'api/rider', rider)
    print(response.json())
    response = requests.post(BASE1+'api/driver', driver)
    print(response.json())
    time.sleep(2)
