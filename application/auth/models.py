from application import db
from application.models import Base

from application.roles.models import Role, UserRole

class User(Base):
    __tablename__ = 'account'

    username = db.Column(db.String(144), unique=True, nullable=False)
    phash = db.Column(db.String(60), nullable=False)

    def __init__(self, username, phash):
        self.username = username
        self.phash = phash
  
    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    @property
    def roles(self):
        userRoles = (UserRole.query
            .join(User, User.id == UserRole.account_id)
            .join(Role, Role.id == UserRole.role_id)
            .filter(UserRole.account_id == self.id)
            .all())

        return [userRole.role.name for userRole in userRoles]