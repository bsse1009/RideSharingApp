from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import math
import requests

BASE = "http://172.17.0.1:5003/"
app = Flask(__name__)
app.config['SECRET_KEY'] = '!brahim123'
api = Api(app)

rider_put_args = reqparse.RequestParser()
rider_put_args.add_argument("id", type=int, help="rider id is required!", required=True)
rider_put_args.add_argument("name", type=str, help="name of a rider is required!", required=True)
rider_put_args.add_argument("current_location", action='append', help="current_location of a rider is required!", required=True)
rider_put_args.add_argument("destination", action='append', help="destination of a rider is required!", required=True)

riders = []

driver_put_args = reqparse.RequestParser()
driver_put_args.add_argument("id", type=int, help="driver id is required!", required=True)
driver_put_args.add_argument("name", type=str, help="name of a driver is required!", required=True)
driver_put_args.add_argument("car_number", type=str, help="car_number of a driver is required!", required=True)
driver_put_args.add_argument("current_location", action='append', help="current_location of a driver is required!", required=True)

drivers = []


def abort_if_rider_already_exist(rider_id):
    if rider_id in riders:
        abort(409, message="rider already exist!!")


def abort_if_driver_already_exist(driver_id):
    if driver_id in drivers:
        abort(409, message="driver already exist!!")


def find_best_match():
    for rider in riders:
        x1 = float(rider['current_location'][0])
        y1 = float(rider['current_location'][1])
        x2 = float(rider['destination'][0])
        y2 = float(rider['destination'][1])
        fare = 10.0*math.sqrt(((x2-x1)**2) + ((y2-y1)**2))
        min_distance = math.inf
        best_match = None
        for driver in drivers:
            x2 = float(driver['current_location'][0])
            y2 = float(driver['current_location'][1])
            # print(x2, y2)
            distance = math.sqrt(((x2-x1)**2) + ((y2-y1)**2))
            if distance < min_distance:
                min_distance = distance
                best_match = driver
        match = {
            "driver_id": best_match['id'],
            "rider_name": rider['name'],
            "driver_name": best_match['name'],
            "fare": fare
        }
        response = requests.post(BASE+'communication', match) #'communication'
        print(response.json())
        print(f'passed to communication portal {response}')
        riders.remove(rider)
        drivers.remove(best_match)


scheduler = BackgroundScheduler()
scheduler.add_job(func=find_best_match, trigger="interval", seconds=10)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


class Rider(Resource):
    def post(self):
        args = rider_put_args.parse_args()
        riders.append(args)
        print("Hit Rider end")
        return "recieved rider info.", 201


class Driver(Resource):
    def post(self):
        args = driver_put_args.parse_args()
        drivers.append(args)
        print("Hit driver end")
        return "recieved driver info.", 201


api.add_resource(Rider, "/api/rider")
api.add_resource(Driver, "/api/driver")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    scheduler.start()
