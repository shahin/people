from app import db


# association table to model users in groups (many-to-many)
users_groups = db.Table(
    'user_groups',
    db.Column('userid', db.String, db.ForeignKey('users.userid')),
    db.Column('group_name', db.String, db.ForeignKey('groups.name')),
)


class UnknownUserException(Exception):
    pass

class UnknownGroupException(Exception):
    pass

class Group(db.Model):

    __tablename__ = "groups"
    name = db.Column(db.String, primary_key=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Group name={}>'.format(self.name) 


class User(db.Model):

    __tablename__ = "users"

    userid = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    groups = db.relationship(
        'Group',
        secondary=users_groups,
        backref=db.backref('users'),
    )

    def __init__(self, userid, first_name, last_name, group_names):
        self.userid = userid
        self.first_name = first_name
        self.last_name = last_name

        if group_names is None:  # [] goes through the JSON serialization wringer and becomes None
            group_names = []
        self.set_groups(group_names)

    def set_groups(self, group_names):
        groups = []
        for name in group_names:
            group = Group.query.filter(Group.name == name).first()
            if group is None:
                raise UnknownGroupException('Group {} does not exist.'.format(name))
            groups.append(group)

        self.groups = groups

    def __repr__(self):
        return '<User userid={}>'.format(self.userid) 

