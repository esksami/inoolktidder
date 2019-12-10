from sqlalchemy import event
from sqlalchemy.orm import relationship

from application import db
from application.models import Base
from application.utils import session_scope


class Role(Base):
    name = db.Column(db.String(128), unique=True)

class UserRole(Base):
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'),
                        nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    role = relationship('Role', backref='user_role')
    user = relationship('User', backref='user_role')


@event.listens_for(Role.__table__, 'after_create')
def insert_initial_values(*args, **kwargs):
    ROLE_NAMES = ['APPROVED', 'BANNED', 'MODERATOR', 'USER']

    with session_scope() as session:
        roles = Role.query.filter(Role.name.in_(['APPROVED', 'USER'])).all()
        session.bulk_save_objects(
            [Role(name=role_name) for role_name in ROLE_NAMES]
        )

        session.commit()