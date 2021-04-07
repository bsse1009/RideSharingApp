from flask import Flask
from flask_restful import Api, Resource, reqparse, abort

app = Flask(__name__)
api = Api(app)

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


api.add_resource(Rider, "/rider/<int:rider_id>")
api.add_resource(Driver, "/driver/<int:driver_id>")

if __name__ == '__main__':
    app.run(debug=True)
