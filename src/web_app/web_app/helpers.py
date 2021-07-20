#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from functools import wraps

from flask import request
import werkzeug.exceptions


def validate_request_timestamp(func):
    """Validate the timestamp of the incoming request."""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        request_timestamp = request.json['timestamp']
        is_valid_request = (datetime.now().timestamp() - request_timestamp) < 1 # 100ms

        if is_valid_request:
            return func(*args, **kwargs)
        else:
            raise werkzeug.exceptions.BadRequest(description='Bad timestamp')

    return decorated_function
