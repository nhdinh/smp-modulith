#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools

from flask import jsonify, make_response

from foundation import ThingGoneInBlackHoleError
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

                # if current_app.testing or current_app.debug:
                #     raise e

                if isinstance(e, ThingGoneInBlackHoleError):
                    return make_response(jsonify({'message': e.args})), 404  # type: ignore
                else:
                    return make_response(jsonify({'message': e.args})), 400  # type: ignore

        return wrapped

    return decorated
