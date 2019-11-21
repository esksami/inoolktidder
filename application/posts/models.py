from application import db

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    title = db.Column(db.String(512), nullable=False)
    content = db.Column(db.String(8192), nullable=False)
    likes = db.Column(db.Integer, default=0)

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'),
                           nullable=False)

    def __init__(self, title, content):
        self.title = title
        self.content = content
