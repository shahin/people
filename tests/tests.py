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

class FlaskTestCase(PeopleTestCase):

    def test_get_user_for_userid(self):
        response = self.client.get('/users/a')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self.test_user_a)

    def test_get_user_returns_404_on_nonexistent_userid(self):
        response = self.client.get('/user/nonexistent')
        self.assertEqual(response.status_code, 404)

    def test_post_user_creates_new_user(self):
        new_user = '''
            {"userid": "b", "first_name": "Beatrice", "last_name": "Portinari", "groups": []}'''
        response = self.client.post('/users', data=new_user, content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_post_user_returns_error_status_on_duplicate_userid(self):
        new_user = '''
            {"userid": "a", "first_name": "Beatrice", "last_name": "Portinari", "groups": []}'''
        response = self.client.post('/users', data=new_user, content_type='application/json')
        self.assertEqual(response.status_code, 409)

    def test_delete_user_deletes_user(self):
        response = self.client.delete('/users/a')
        self.assertEqual(response.status_code, 410)
        self.assertIsNone(User.query.filter(User.userid == 'a').first())

    def test_delete_user_returns_404_on_nonexistent_userid(self):
        response = self.client.delete('/users/nonexistent')
        self.assertEqual(response.status_code, 404)

    def test_put_user_replaces_existing_user_record(self):
        user_last_name = User.query.filter(User.userid == 'a').first().last_name
        self.assertEqual('Pennyworth', user_last_name)

        updated_user = '''
            {"userid": "a", "first_name": "Alfred", "last_name": "Brendel", "groups": []}'''
        response = self.client.put('/users/a', data=updated_user, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        user_last_name = User.query.filter(User.userid == 'a').first().last_name
        self.assertEqual('Brendel', user_last_name)

    def test_put_user_returns_404_on_nonexistent_userid(self):
        updated_user = '''
            {"userid": "c", "first_name": "Alfred", "last_name": "Brendel", "groups": []}'''
        response = self.client.put('/users/c', data=updated_user, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_get_group_returns_list_of_member_userids(self):
        response = self.client.get('/groups/famous', content_type='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, ['a'])

    def test_get_group_returns_404_on_nonexistent_group(self):
        response = self.client.get('/groups/nonexistent', content_type='text/html')
        self.assertEqual(response.status_code, 404)

    def test_post_group_creates_new_group(self):
        response = self.client.post('/groups', data={'name': 'new'})
        self.assertEqual(response.status_code, 201)

    def test_post_group_returns_error_status_on_duplicate_group_name(self):
        response = self.client.post('/groups', data={'name': 'famous'})
        self.assertEqual(response.status_code, 409)

    def test_put_group_replaces_membership_list(self):
        response = self.client.get('/groups/famous')
        self.assertEqual(response.json, ['a'])

        response = self.client.put('/groups/famous', data='["p"]', content_type='application/json')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/groups/famous')
        self.assertEqual(response.json, ['p'])

    def test_put_group_returns_404_on_nonexistent_group(self):
        response = self.client.put('/groups/nonexistent', data={'users': ['a']})
        self.assertEqual(response.status_code, 404)

    def test_delete_group_deletes_group(self):
        response = self.client.get('/users/a')
        self.assertEqual(response.json['groups'], ['famous'])

        response = self.client.delete('/groups/famous')
        self.assertEqual(response.status_code, 410)

        response = self.client.get('/groups/famous')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/users/a')
        self.assertEqual(response.json['groups'], [])

    def test_delete_group_returns_404_on_nonexistent_group(self):
        response = self.client.delete('/groups/nonexistent')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
