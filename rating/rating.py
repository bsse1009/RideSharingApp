from flask import Flask
from flask_restful import Api, Resource, reqparse
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

cluster = MongoClient(port=27017)
db = cluster["driver"]
collection = db["rating"]


rating_put_args = reqparse.RequestParser()
rating_put_args.add_argument("_id", type=int, help="driver id is required!", required=True)
rating_put_args.add_argument("name", type=str, help="name of a driver is required!", required=True)
rating_put_args.add_argument("rating", type=float, help="car_number of a driver is required!", required=True)


class Rating(Resource):
    def post(self):
        args = rating_put_args.parse_args()
        cols = collection.find_one({"_id": args["_id"]})
        if cols:
            print("updating rating....")
            rating = (float(cols["rating"])+float(args["rating"]))/2.0
            args["rating"] = rating
            collection.delete_one(cols)

        collection.insert_one(args)
        print(args)
        return "Successful", 201


api.add_resource(Rating, "/rating")

if __name__ == '__main__':
    app.run(debug=True, port=5002)
