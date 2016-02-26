from people.app import db
from people.models import User, Group

db.create_all()
db.session.commit()
