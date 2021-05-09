from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
from flask_socketio import SocketIO


app = Flask(__name__)
api = Api(app)
socketIo = SocketIO(app)

match_put_args = reqparse.RequestParser()
match_put_args.add_argument("driver_id", type=int, help="driver id is required!", required=True)
match_put_args.add_argument("rider_name", type=str, help="name of a rider is required!", required=True)
match_put_args.add_argument("driver_name", type=str, help="name of a driver is required!", required=True)
match_put_args.add_argument("fare", type=float, help="fare of a ride is required!", required=True)


@socketIo.on('serve')
def serve(match):
    socketIo.emit('message', match, namespace='/communication')


class Communication(Resource):
    def post(self):
        args = match_put_args.parse_args()
        serve(args)
        return "recieved", 201


api.add_resource(Communication, "/communication")

if __name__ == '__main__':
    socketIo.run(app, debug=True, port=5003)
