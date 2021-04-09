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
rider_put_args.add_argument("name", type=str, help="name of a rider is required!", required=True)
rider_put_args.add_argument("current_location", action='append', help="current_location of a rider is required!", required=True)
rider_put_args.add_argument("destination", action='append', help="destination of a rider is required!", required=True)

riders = {}

driver_put_args = reqparse.RequestParser()
driver_put_args.add_argument("name", type=str, help="name of a driver is required!", required=True)
driver_put_args.add_argument("car_number", type=str, help="car_number of a driver is required!", required=True)
driver_put_args.add_argument("current_location", action='append', help="current_location of a driver is required!", required=True)

drivers = {}


def abort_if_rider_already_exist(rider_id):
    if rider_id in riders:
        abort(409, message="rider already exist!!")


def abort_if_driver_already_exist(driver_id):
    if driver_id in drivers:
        abort(409, message="driver already exist!!")


@socketIo.on('message')
def serve(k1, k2):
    print(f'rider {riders[k1]} is assign to driver {drivers[k2]}')
    socketIo.emit('message', {'rider': riders[k1]['name'], 'driver': drivers[k2]['name']}, namespace='/communication')
    del riders[k1]
    del drivers[k2]


def find_best_match():
    pre_riders = riders.copy()
    pre_drivers = drivers.copy()
    for key in list(pre_riders):
        x1 = float(pre_riders[key]['current_location'][0])
        y1 = float(pre_riders[key]['current_location'][1])
        # print(x1, y1)
        min_distance = math.inf
        best_match = 0
        for k in list(pre_drivers):
            x2 = float(pre_drivers[k]['current_location'][0])
            y2 = float(pre_drivers[k]['current_location'][1])
            # print(x2, y2)
            distance = math.sqrt(((x2-x1)**2) + ((y2-y1)**2))
            if distance < min_distance:
                min_distance = distance
                best_match = k
        serve(key, best_match)
        del pre_riders[key]
        del pre_drivers[best_match]
    pre_drivers.clear()
    pre_riders.clear()


scheduler = BackgroundScheduler()
scheduler.add_job(func=find_best_match, trigger="interval", seconds=30)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())


class Rider(Resource):
    def post(self, rider_id):
        abort_if_rider_already_exist(rider_id)
        args = rider_put_args.parse_args()
        riders[rider_id] = args
        # print(riders[rider_id]["current_location"])
        return riders[rider_id], 201


class Driver(Resource):
    def post(self, driver_id):
        abort_if_driver_already_exist(driver_id)
        args = driver_put_args.parse_args()
        drivers[driver_id] = args
        # print(drivers)
        return drivers[driver_id], 201


class Rating(Resource):
    def post(self):
        pass


api.add_resource(Rider, "/rider/<int:rider_id>")
api.add_resource(Driver, "/driver/<int:driver_id>")
api.add_resource(Rating, "/driver/<int:driver_id>")

if __name__ == '__main__':
    socketIo.run(app, debug=True)
    scheduler.start()
