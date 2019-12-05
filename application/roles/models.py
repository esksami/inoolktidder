from application import db

from sqlalchemy.orm import relationship
from sqlalchemy import event


class Role(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(128), unique=True)

class UserRole(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'),
                        nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'),
                           nullable=False) 

    user = relationship("User", backref="UserRole")
    role = relationship("Role", backref="UserRole")

@event.listens_for(Role.__table__, 'after_create')
def insert_initial_values(*args, **kwargs):
    db.session.add(Role(name='APPROVED'))
    db.session.add(Role(name='BANNED'))
    db.session.add(Role(name='ADMIN'))
    db.session.add(Role(name='USER'))
    db.session.commit()