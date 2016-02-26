from app import db


# association table to model users in groups (many-to-many)
users_groups = db.Table(
    'user_groups',
    db.Column('userid', db.String, db.ForeignKey('user.userid')),
    db.Column('group_name', db.String, db.ForeignKey('group.group_name')),
)


class Group(db.Model):

    group_name = db.Column(db.String, primary_key=True)

    def __init__(self, group_name):
        self.group_name = group_name

    def __repr__(self):
        return '<Group group_name={}>'.format(self.group_name) 


class User(db.Model):

    userid = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    groups = db.relationship(
        'Group',
        secondary=users_groups,
        backref=db.backref('user'),
    )

    def __init__(self, userid, first_name, last_name, group_names):
        self.userid = userid
        self.first_name = first_name
        self.last_name = last_name
        if group_names is None:
            group_names = []
        self.groups = self.add_groups(group_names)

    def add_groups(self, group_names):
        groups = []
        for name in group_names:
            group = Group.query.filter(Group.group_name == name).first()
            groups.append(group)

        return groups

    def __repr__(self):
        return '<User userid={}>'.format(self.userid) 

