import shelve

# Import the framework
from flask import g as group_g
from flask import request
from flask_restful import Resource, Api, reqparse, request

from password_as_a_service import users

GROUPS_FILE_PATH = "/etc/group"

def get_db():
    # db = getattr(group_g, '_database', None)
    # if db is None:
    db = group_g._database = shelve.open("groups.db")
    return shelve.open("groups.db")

def teardown_db(exception):
    db = getattr(group_g, '_database', None)
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
                    if len(data_chunks) != 4:
                        raise Exception ("Improper format")
                    # form the json list here unless it is a comment line
                    members = data_chunks[3].strip("\n")
                    json_list.append({
                        "name": data_chunks[0],
                        "gid": data_chunks[2],
                        "members": members.split(',') if members else []
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
    json_list, message, status = parse_file_to_json(GROUPS_FILE_PATH)
    for json_obj in json_list:
        shelf[json_obj['gid']] = json_obj
    return message, status

class GroupList(Resource):
    def get(self):
        shelf = get_db()
        keys = list(shelf.keys())

        groups = []

        for key in keys:
            groups.append(shelf[key])

        return {'message': 'Success', 'data': groups}, 200

    def post(self):
        args = request.json['groups']
        shelf = get_db()

        for arg in args:
            shelf[arg['gid']] = arg
        return {'message': 'Groups registered', 'data': args}, 201


class Group(Resource):
    def get(self, gid):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (gid in shelf):
            return {'message': 'Group not found', 'data': {}}, 404

        return {'message': 'Group found', 'data': shelf[gid]}, 200

    def delete(self, gid):
        shelf = get_db()

        # If the key does not exist in the data store, return a 404 error.
        if not (gid in shelf):
            return {'message': 'Group not found', 'data': {}}, 404

        del shelf[gid]
        return '', 204

class UserGroups(Resource):
    def get(self, uid):

        user_groups = []

        user_db = users.get_db()
        user_name = None

        # get the name of the user from uid
        for user_id in user_db:
            if user_id == uid:
                user_data = user_db[user_id]
                user_name = user_data['name']
                break

        shelf = get_db()
        for gid in shelf:
            group_data = shelf[gid]
            if user_name in group_data['members']:
                user_groups.append(group_data)

        return {'message': 'Group list info', 'data': user_groups}, 200


class GroupQuery(Resource):

    def verify_member_params(self, request_member_params,
                             db_member_params):
        for member in request_member_params:
            if member not in db_member_params:
                return 0
        return 1

    def get(self):


        member_args = request.args.getlist('member')
        name_arg = request.args.get('name')
        gid_arg = request.args.get('gid')

        groups_list = []

        # form a dictionary of not none params
        request_params = {}

        if member_args:
            request_params['members'] = member_args
        if name_arg:
            request_params['name'] = name_arg
        if gid_arg:
            request_params['gid'] = gid_arg

        if len(request_params) == 0:
            return 'query needs atleast one parameter for a match', 400

        shelf = get_db()

        # compare every record in the groups database with the query parameter set

        for group_gid in shelf:
            group_data = shelf[group_gid]

            matching_fields = 0

            for param in request_params:
                if param == 'members':
                    matching_fields += self.verify_member_params(request_params[param], group_data[param])
                elif group_data[param] == request_params[param]:
                    matching_fields += 1
                else:
                    break

            if matching_fields == len(request_params):
                groups_list.append(group_data)

        return {'message': 'Matching groups info', 'data': groups_list}, 200
