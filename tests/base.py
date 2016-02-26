import unittest
from flask.ext.testing import TestCase
from people.app import app, db
from people.models import User, Group

class PeopleTestCase(TestCase):

    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        self.client = app.test_client(self)
        self.test_group = {'group_name': 'famous'}
        self.test_user_a = {
            'userid': 'a',
            'first_name': 'Alfred',
            'last_name': 'Pennyworth',
            'groups': ['famous']
        }
        self.test_user_p = {
            'userid': 'p',
            'first_name': 'Philip',
            'last_name': 'Glass',
            'groups': []
        }

        db.create_all()
        db.session.add(Group(*[self.test_group[col] for col in ['group_name']]))
        db.session.add(User(
            *[self.test_user_a[col] for col in ['userid', 'first_name', 'last_name', 'groups']]))
        db.session.add(User(
            *[self.test_user_p[col] for col in ['userid', 'first_name', 'last_name', 'groups']]))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
