from flask import Flask, request, abort
from flask_restful import Resource, Api
from flask.ext.sqlalchemy import SQLAlchemy
from json import dumps

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
            return { k: getattr(user, k) for k in ['userid', 'first_name', 'last_name', 'groups'] }

    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('first_name', type=str, help="The user's first name")
        parser.add_argument('last_name', type=str, help="The user's last name")
        parser.add_argument('userid', type=str, help="The user's identifier")
        parser.add_argument('groups', type=str, help="The groups that this user is a member of")
        args = parser.parse_args()

        new_user = User(args['userid'], args['first_name'], args['last_name'], args['groups'])
        db.session.add(new_user) 

        try:
            db.session.commit()
            return args, 201
        except IntegrityError:
            abort(409)

    def delete(self, userid):
        user = User.query.filter(User.userid == userid).first()

        if user is None:
            abort(404)
        else:
            db.session.delete(user)
            db.session.commit()
            return userid, 201

class Groups_Meta(Resource):

    def get(self, group_name):
        group = Group.query.filter(Group.group_name == group_name).first()

        if group is None:
            abort(404)

        return [ u.userid for u in User.query.join(Group).filter(Group.group_name == group_name) ]

api.add_resource(Users_Meta, '/users/<string:userid>', '/users')
api.add_resource(Groups_Meta, '/groups/<string:group_name>')

if __name__ == '__main__':
     app.run(debug=True)
