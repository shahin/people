from app import db
from models import User, Group

db.create_all()
db.session.add(User("ssaneinejad", "Shahin", "Saneinejad"))
db.session.commit()
