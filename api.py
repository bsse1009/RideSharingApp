from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
from flask_socketio import SocketIO, emit
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = '!brahim123'
api = Api(app)
socketIo = SocketIO(app)

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


@socketIo.on('message')
def serve(rider, driver):
    print(f'rider {rider} is assign to driver {driver}')
    socketIo.emit('message', {'rider': rider['name'], 'driver': driver['name']}, namespace='/communication')
    riders.remove(rider)
    drivers.remove(driver)


def find_best_match():
    for rider in riders:
        x1 = float(rider['current_location'][0])
        y1 = float(rider['current_location'][1])
        # print(x1, y1)
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
        serve(rider, best_match)


scheduler = BackgroundScheduler()
scheduler.add_job(func=find_best_match, trigger="interval", seconds=20)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


class Rider(Resource):
    def post(self):
        # abort_if_rider_already_exist()
        args = rider_put_args.parse_args()
        riders.append(args)
        # print(riders[rider_id]["current_location"])
        return args['name'], 201


class Driver(Resource):
    def post(self):
        # abort_if_driver_already_exist(driver_id)
        args = driver_put_args.parse_args()
        drivers.append(args)
        return args['name'], 201


class Rating(Resource):
    def post(self):
        pass


api.add_resource(Rider, "/rider")
api.add_resource(Driver, "/driver")
api.add_resource(Rating, "/rating")

if __name__ == '__main__':
    socketIo.run(app, debug=True)
    scheduler.start()
