import markdown
import os

# Import the framework
from flask import Flask, g
from flask_restful import Resource, Api
from password_as_a_service.users import User, UserList, UserQuery
from password_as_a_service.groups import Group, GroupList, UserGroups, GroupQuery
# from password_as_a_service.users_watcher import Watcher as UsersWatcher

# Create an instance of Flask
app = Flask(__name__)

# Create the API
api = Api(app)

with app.app_context():
    # user_watch = UsersWatcher()
    # user_watch.run()

    users.create_db_on_file_changes()
    groups.create_db_on_file_changes()

@app.teardown_appcontext
def teardown_all_dbs(exception):
    users.teardown_db(Exception)
    groups.teardown_db(Exception)

@app.route("/")
def index():
    """Present some documentation"""

    # Open the README file
    with open(os.path.dirname(app.root_path) + '/README.md', 'r') as markdown_file:

        # Read the content of the file
        content = markdown_file.read()

        # Convert to HTML
        return markdown.markdown(content)

api.add_resource(UserList, '/users')
api.add_resource(UserQuery, '/users/query',
                 endpoint = '/users/query')
api.add_resource(User, '/users/<string:uid>')

api.add_resource(GroupList, '/groups')
api.add_resource(Group, '/groups/<string:gid>')
api.add_resource(UserGroups, '/users/<string:uid>/groups')
api.add_resource(GroupQuery, '/groups/query',
                 endpoint = '/groups/query')
