import os

from flask import Flask, request, abort
from flask_restful import Resource, Api
from flask.ext.sqlalchemy import SQLAlchemy

from flask_restful import reqparse
from sqlalchemy.exc import IntegrityError

def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ.get('PEOPLE_CONFIG', 'config.DevConfig'))
    db = SQLAlchemy(app)
    return app, db

app, db = create_app()
from models import *


class UsersResource(Resource):

    def get(self, userid):
        """Returns the matching user record or 404 if none exist."""
        user = User.query.filter(User.userid == userid).first()
        if user is None:
            abort(404)
        else:
            user_dict = { k: getattr(user, k) for k in ['userid', 'first_name', 'last_name', 'groups'] }
            user_dict['groups'] = [ g.group_name for g in user_dict['groups'] ]
            return user_dict

    def post(self):
        """Creates a new user record.
        
        The body of the request should be a valid user record. POSTs to an existing user are
        treated as errors and flagged with HTTP status code 409 (conflict)."""

        args = request.json
        new_user = User(
            *[ args.get(col, None) for col in ('userid', 'first_name', 'last_name', 'groups') ])
        db.session.add(new_user) 

        try:
            db.session.commit()
            return args, 201
        except IntegrityError:
            abort(409) # trying to add a duplicate user

    def delete(self, userid):
        """Deletes a user record. Returns 404 if the user doesn't exist."""

        user = User.query.filter(User.userid == userid).first()

        if user is None:
            abort(404)
        else:
            db.session.delete(user)
            db.session.commit()
            return userid, 410

    def put(self, userid):
        """Updates an existing user record.
        
        The body of the request should be a valid user record. PUTs to a non-existant user return a
        404."""

        args = request.json
        updated_user = User(
            *[ args.get(col, None) for col in ('userid', 'first_name', 'last_name', 'groups') ])

        self.delete(updated_user.userid)
        db.session.add(updated_user)
        db.session.commit()

class GroupsResource(Resource):

    def get(self, group_name):
        """Returns a JSON list of userids containing the members of that group. Returns a 404 if the
        group doesn't exist."""

        group = Group.query.filter(Group.group_name == group_name).first()
        if group is None:
            abort(404)
        return [ u.userid for u in group.users ]

    def post(self):
        """Creates a empty group.
        
        POSTs to an existing group are treated as errors and flagged with the HTTP status code 409
        (conflict). The body should contain a `name` parameter"""

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, help="The group name")
        args = parser.parse_args()

        new_group = Group(args['name'])
        db.session.add(new_group) 

        try:
            db.session.commit()
            return args, 201
        except IntegrityError:
            abort(409) # trying to add a duplicate group

    def put(self, group_name):
        """Updates the membership list for the group. The body of the request should be a JSON list
        describing the group's members.
        """
        userids = request.json

        # delete all old associations with this group
        self.delete(group_name)

        # re-create the group with all POSTed associations
        group = Group(group_name)
        db.session.add(group)
        for userid in userids:
            member = User.query.filter(User.userid == userid).first()
            member.groups.append(group)
        db.session.commit()

    def delete(self, group_name):
        """Deletes a group. Returns 404 if the group doesn't exist."""

        group = Group.query.filter(Group.group_name == group_name).first()

        if group is None:
            abort(404)
        else:
            db.session.delete(group)
            db.session.commit()
            return group_name, 410

    
api = Api(app)
api.add_resource(UsersResource, '/users/<string:userid>', '/users')
api.add_resource(GroupsResource, '/groups/<string:group_name>', '/groups')

if __name__ == '__main__':
     app.run(debug=True)
