from flask import Flask, request, abort
from flask_restful import Resource, Api
from flask.ext.sqlalchemy import SQLAlchemy
import json

from flask_restful import reqparse
from sqlalchemy.exc import IntegrityError

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///people.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db = SQLAlchemy(app)
    return app, db

app, db = create_app()
from models import *

api = Api(app)

class Users_Meta(Resource):

    def get(self, userid):
        user = User.query.filter(User.userid == userid).first()
        if user is None:
            abort(404)
        else:
            user_dict = { k: getattr(user, k) for k in ['userid', 'first_name', 'last_name', 'groups'] }
            user_dict['groups'] = [ g.group_name for g in user_dict['groups'] ]
            return user_dict

    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=str, help="The user's first name")
        parser.add_argument('last_name', type=str, help="The user's last name")
        parser.add_argument('userid', type=str, help="The user's identifier")
        parser.add_argument('groups', action='append', help="The groups that this user is a member of")
        args = parser.parse_args()

        new_user = User(
            *[ args.get(col, None) for col in ('userid', 'first_name', 'last_name', 'groups') ])
        db.session.add(new_user) 

        try:
            db.session.commit()
            return args, 201
        except IntegrityError:
            abort(409) # trying to add a duplicate user

    def delete(self, userid):
        user = User.query.filter(User.userid == userid).first()

        if user is None:
            abort(404)
        else:
            db.session.delete(user)
            db.session.commit()
            return userid, 410

    def put(self, userid):

        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=str, help="The user's first name")
        parser.add_argument('last_name', type=str, help="The user's last name")
        parser.add_argument('userid', type=str, help="The user's identifier")
        parser.add_argument('groups', action='append', help="The groups that this user is a member of")
        args = parser.parse_args()

        updated_user = User(
            *[ args.get(col, None) for col in ('userid', 'first_name', 'last_name', 'groups') ])

        self.delete(updated_user.userid)
        db.session.add(updated_user)
        db.session.commit()

class Groups_Meta(Resource):

    def get(self, group_name):
        group = Group.query.filter(Group.group_name == group_name).first()
        if group is None:
            abort(404)
        return [ u.userid for u in group.users ]

    def post(self):

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

        parser = reqparse.RequestParser()
        parser.add_argument('userids', type=str,
                help="A list of userids for all members of this group")
        args = parser.parse_args()

        # delete all old associations with this group
        self.delete(group_name)

        # re-create the group with all POSTed associations
        db.session.add(group_name)
        for userid in args['userids']:
            member = User.query.filter(User.userid == userid).first()
            member.groups.append(group_name)
        db.session.commit()

    def delete(self, group_name):
        group = Group.query.filter(Group.group_name == group_name).first()

        if group is None:
            abort(404)
        else:
            db.session.delete(group)
            db.session.commit()
            return group_name, 410

    
api.add_resource(Users_Meta, '/users/<string:userid>', '/users')
api.add_resource(Groups_Meta, '/groups/<string:group_name>', '/groups')

if __name__ == '__main__':
     app.run(debug=True)
