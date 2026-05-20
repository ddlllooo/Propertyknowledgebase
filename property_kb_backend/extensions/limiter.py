from flask import request as flask_request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["2000 per day", "1000 per hour"])


@limiter.request_filter
def _exempt_options():
    return flask_request.method == "OPTIONS"
