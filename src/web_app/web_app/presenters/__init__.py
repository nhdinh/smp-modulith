#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools

from flask import current_app, jsonify, make_response

from foundation.logger import logger


def log_error():
    def decorated(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                if logger:
                    logger.exception(e)

                if current_app.testing:
                    raise e

                return make_response(jsonify({'messages': e.args})), 400  # type: ignore

        return wrapped

    return decorated
