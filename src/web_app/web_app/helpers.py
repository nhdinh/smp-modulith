#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from functools import wraps

import werkzeug.exceptions
from flask import request


def validate_request_timestamp(func):
    """Validate the timestamp of the incoming request."""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        # raise BadRequest error if no timestamp field in the request
        if hasattr(request.json, 'timestamp') or hasattr(request.data, 'timestamp'):
            raise werkzeug.exceptions.BadRequest(description='Bad timestamp')

        # else, check if the timestamp field is existed but the time span was tooo long
        request_timestamp = request.json['timestamp']
        is_valid_request = (datetime.now().timestamp() - request_timestamp) < timedelta(microseconds=100).seconds

        if is_valid_request:
            return func(*args, **kwargs)
        else:
            raise werkzeug.exceptions.BadRequest(description='Bad timestamp')

    return decorated_function
