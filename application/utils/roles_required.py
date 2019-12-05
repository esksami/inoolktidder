from functools import wraps
from flask_login import login_required, current_user

from application import login_manager


def roles_required(*role_names):
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            if not current_user or not current_user.is_authenticated:
                return login_manager.unauthorized()

            if not all(role_name in current_user.roles for role_name in role_names):
                return login_manager.unauthorized()

            return f(*args, **kwargs)

        return decorator
    return wrapper