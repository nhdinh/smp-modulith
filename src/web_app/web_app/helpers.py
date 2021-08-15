#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta
from functools import wraps

import werkzeug.exceptions
from flask import request


def validate_request_timestamp(func):
    """Validate the timestamp of the incoming request."""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        # raise BadRequest error if no timestamp field in the request
        if 'timestamp' not in request.json.keys():
            request_json = bytes_to_json(request.data)
            if 'timestamp' not in request_json:
                raise werkzeug.exceptions.BadRequest(description='Need specified timestamp in request')

        # else, check if the timestamp field is existed but the time span was tooo long
        request_timestamp = request.json['timestamp']
        is_valid_request = (datetime.now().timestamp() - request_timestamp) < timedelta(seconds=5).seconds

        if is_valid_request:
            return func(*args, **kwargs)
        else:
            raise werkzeug.exceptions.BadRequest(description='Bad timestamp')

    return decorated_function


def bytes_to_json(bytes_data):
    """
    Convert bytes object to json string

    :param bytes_data: bytes object data
    :return: well formated json string
    """
    return json.loads(bytes_data.decode('utf8').replace("'", '"'))


def json_to_bytes(json_data):
    """
    Convert json string to bytes object

    :param json_data: a json string
    :return: bytes object
    """
    return json.dumps(json_data.encode('utf8'))
