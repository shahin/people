from flask import request, abort
from flask_restful import Resource, reqparse
from sqlalchemy.exc import IntegrityError
import werkzeug

from app import db, api
from models import User, Group, UnknownUserException, UnknownGroupException

class UsersResource(Resource):

    @staticmethod
    def _serialize_user(user):
        user_dict = { k: getattr(user, k) for k in ['userid', 'first_name', 'last_name', 'groups'] }
        user_dict['groups'] = [ g.name for g in user_dict['groups'] ]
        return user_dict

    def get(self, userid):
        """Returns the matching user record or 404 if none exist."""
        user = User.query.filter(User.userid == userid).first()
        if user is None:
            abort(404)
        else:
            return self._serialize_user(user), 200

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
        """Deletes a user record. Returns 404 if the user doesn't exist, or 410 on success."""

        user = User.query.filter(User.userid == userid).first()

        if user is None:
            abort(404)
        else:
            db.session.delete(user)
            db.session.commit()
            return userid, 410

    def put(self, userid):
        """Updates an existing user record.
        
        The body of the request should be a valid user record. PUTs to a non-existant user return
        a 404, and PUTs containing a non-existent group return 422."""

        args = request.json

        try:

            # delete original record and all associations
            original_user = User.query.filter(User.userid == args['userid']).first()
            if original_user is None:
                abort(404)
            else:
                db.session.delete(original_user)

            # insert updated record with its associations
            updated_user = User(
                *[args.get(col, None) for col in ('userid', 'first_name', 'last_name', 'groups')])

            db.session.add(updated_user)
            db.session.commit()
            return self._serialize_user(updated_user), 200

        except UnknownGroupException as e:
            db.session.rollback()
            abort(422)

        except werkzeug.exceptions.HTTPException as e:
            db.session.rollback()
            raise e

        except Exception as e:
            db.session.rollback()
            abort(500)

class GroupsResource(Resource):

    def get(self, group_name):
        """Returns a JSON list of userids containing the members of that group. Returns a 404 if
        the group doesn't exist."""

        group = Group.query.filter(Group.name == group_name).first()
        if group is None:
            abort(404)
        return [ u.userid for u in group.users ]

    def post(self):
        """Creates a empty group.
        
        POSTs to an existing group are treated as errors and flagged with the HTTP status code
        409 (conflict). The body should contain a `name` parameter"""

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
        """Updates the membership list for the group. The body of the request should be a JSON
        list describing the group's members.

        Returns 404 if the group does not exist or 422 if a user in the membership list does not
        exist.
        """
        userids = request.json

        try:

            # delete all old associations with this group
            group = Group.query.filter(Group.name == group_name).first()
            if group is None:
                abort(404)
            else:
                db.session.delete(group)

            # re-create the group with associations to all PUT users
            group = Group(group_name)
            for userid in userids:
                member = User.query.filter(User.userid == userid).first()
                if member is None:
                    raise UnknownUserException('User {} not found.'.format(userid))
                member.groups.append(group)
            db.session.add(group)
            db.session.commit()

        except werkzeug.exceptions.HTTPException as e:
            db.session.rollback()
            raise e

        except UnknownUserException as e:
            db.session.rollback()
            abort(422)

        except Exception as e:
            db.session.rollback()
            abort(500)

    def delete(self, group_name):
        """Deletes a group. Returns 404 if the group doesn't exist, or 410 on success."""

        group = Group.query.filter(Group.name == group_name).first()

        if group is None:
            abort(404)
        else:
            db.session.delete(group)
            db.session.commit()
            return group_name, 410

api.add_resource(UsersResource, '/users/<string:userid>', '/users')
api.add_resource(GroupsResource, '/groups/<string:group_name>', '/groups')
