from application import db
from datetime import datetime

class Base(db.Model):
    __abstract__ = True
  
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_modified = db.Column(db.DateTime, default=datetime.now(),
        onupdate=db.func.current_timestamp())