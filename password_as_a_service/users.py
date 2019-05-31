import shelve

# Import the framework
from flask import g as user_g
from flask import request
from flask_restful import Resource, Api, reqparse, request

USERS_FILE_PATH = "/etc/passwd"

def get_db():
    # db = getattr(user_g, '_database', None)
    # if db is None:
    db = user_g._database = shelve.open("users.db")
    return db

def teardown_db(exception):
    db = getattr(user_g, '_database', None)
    if db is not None:
        db.close()

def parse_file_to_json(file_path):
    json_list = []
    try:
        with open(file_path, mode='r') as fh:
            line = fh.readline()
            for line in fh:
                data_chunks = line.split(':')
                if '#' not in line:
                    if len(data_chunks) != 7:
                        raise Exception ("Improper format")
                    # form the json list here unless it is a comment line
                    json_list.append({
                        "name": data_chunks[0],
                        "uid": data_chunks[2],
                        "gid": data_chunks[3],
                        "comment": data_chunks[4],
                        "home": data_chunks[5],
                        "shell": data_chunks[6]
                    })
        return json_list, 'OK', 200
    except FileNotFoundError:
        return json_list, 'File not found in the file path', 404
    except Exception as exc:
        return json_list, 'Unable to parse file contents: Malformed or not in valid format: ' + str(exc), 500
    finally:
        if fh is not None:
            fh.close()

def create_db_on_file_changes():
    teardown_db(Exception)
    shelf = get_db()
    json_list, message, status = parse_file_to_json(USERS_FILE_PATH)
    for json_obj in json_list:
        shelf[json_obj['uid']] = json_obj
    return message, status

class UserList(Resource):
    def get(self):
        shelf = get_db()
        keys = list(shelf.keys())

        users = []

        for key in keys:
            users.append(shelf[key])

        return {'message': 'Success', 'data': users}, 200

    def post(self):
        args = request.json['users']
        shelf = get_db()

        for arg in args:
            shelf[arg['uid']] = arg
        return {'message': 'Users registered', 'data': args}, 201


class User(Resource):
    def get(self, uid):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (uid in shelf):
            return {'message': 'User not found', 'data': {}}, 404

        return {'message': 'User found', 'data': shelf[uid]}, 200

    def delete(self, uid):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (uid in shelf):
            return {'message': 'User not found', 'data': {}}, 404

        del shelf[uid]
        return '', 204

class UserQuery(Resource):

    def get(self):

        args = request.args

        users_list = []

        # form a dictionary of not none params
        request_params = {}
        if args.get('name'):
            request_params ['name'] = args.get('name')
        if args.get('uid'):
            request_params['uid'] = args.get('uid')
        if args.get('gid'):
            request_params ['gid'] = args.get('gid')
        if args.get('comment'):
            request_params['comment'] = args.get('comment')
        if args.get('home'):
            request_params ['home'] = args.get('home')
        if args.get('shell'):
            request_params['shell'] = args.get('shell')

        if len(request_params) == 0:
            return 'query needs atleast one parameter for a match', 400

        shelf = get_db()

        # compare every record in the users database with the query parameter set
        for user_uid in shelf:
            user_data = shelf[user_uid]

            matching_fields = 0

            for param in request_params:
                if user_data[param] == request_params[param]:
                    matching_fields += 1
                else:
                    break

            if matching_fields == len(request_params):
                users_list.append(user_data)


        return {'message': 'Matching users info', 'data': users_list}, 200



