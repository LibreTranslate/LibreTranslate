from functools import wraps


class Limiter:
    def exempt(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    def init_app(self, app):
        pass
