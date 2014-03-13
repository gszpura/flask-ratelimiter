# -*- coding: utf-8 -*-
##
## This file is part of Flask-RateLimiter
## Copyright (C) 2014 CERN.
##
## Flask-RateLimiter is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Flask-RateLimiter is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Flask-RateLimiter; if not, write to the Free Software Foundation,
## Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.
import time
from redis import Redis


class Backend(object):
    """
    Abstract backend for inheriting purposes.
    """

    def __init__(self, **kwargs):

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def update(self):
        """
        Every new backend needs to implement this function.

        Function needs to return tuple with two values:
        * limit_exceeded - boolean, checks if limit was exceeded
        * remaining - how many request have left to exceed the limit
        """
        raise NotImplementedError


class SimpleRedisBackend(Backend):
    """
    Simple redis backend.
    Directly connects to Redis and uses its pipeline
    to store keys in database.
    """

    expiration_window = 10

    def __init__(self, **kwargs):
        super(SimpleRedisBackend, self).__init__(**kwargs)
        self.redis = Redis()
        self.pipeline = self.redis.pipeline()

    def update(self, key_prefix, limit, per):
        """
        Updates database for specific key_prefix.

        Key prefix is basically an info about endpoint and
        user requesting specific endpoint, for example:

        'rate_limit/127.0.0.1/index_view'

        :param key_prefix: prefix for the key we want to store in redis
        :param limit: max number of request per some time
        :param per: time in seconds during which we count records
        """
        reset = (int(time.time()) // per) * per + per
        key = key_prefix + str(reset)

        self.pipeline.incr(key)
        self.pipeline.expireat(key, reset + self.expiration_window)
        current = min(self.pipeline.execute()[0], limit)

        limit_exceeded = current >= limit
        remaining = limit - current
        return limit_exceeded, remaining


class FlaskCacheRedisBackend(SimpleRedisBackend):
    """
    Backend which uses Flask-Cache to store keys in Redis.
    """
    expiration_window = 10

    def __init__(self, cache=None, **kwargs):
        self.cache = cache
        if self.cache.__class__.__name__ != 'Cache':
            raise ValueError('Incorrect cache was passed as an argument')
        self.pipeline = self.cache.cache._client.pipeline()
        super(SimpleRedisBackend, self).__init__(**kwargs)