from application import db
from application.models import Base

class User(Base):
    __tablename__ = "account"

    username = db.Column(db.String(144), unique=True, nullable=False)
    phash = db.Column(db.String(60), nullable=False)
    salt = db.Column(db.String(29), nullable=False)

    def __init__(self, username, phash, salt):
        self.username = username
        self.phash = phash
        self.salt = salt
  
    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True