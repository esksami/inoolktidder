# Taken from:
# https://docs.sqlalchemy.org/en/13/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it
from contextlib import contextmanager
from application import db

@contextmanager
def session_scope(*args, **kwargs):
    session = db.session(*args, **kwargs)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
