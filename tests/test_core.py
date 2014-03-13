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

from __future__ import absolute_import

from .helpers import FlaskTestCase

from flask import Blueprint, Flask, request, url_for, g, current_app
from flask.ext.ratelimiter import RateLimiter, \
    ratelimit, \
    get_backend, \
    DEFAULT_BACKEND
from flask.ext.cache import Cache


class TestRateLimiter(FlaskTestCase):
    """
    Tests of rate limiting.
    """
    def test_rate_limiting_simple_redis_backend(self):
        rl = RateLimiter(self.app)

        @self.app.route('/limit')
        @ratelimit(current_app, 2, 10)
        def test_limit():
            return 'limit'

        with self.app.test_client() as c:
            res = c.get('/limit')
            assert request.endpoint == 'test_limit'
            assert g._rate_limit_info.limit == 2
            assert g._rate_limit_info.remaining == 1
            assert g._rate_limit_info.limit_exceeded == False
            assert g._rate_limit_info.per == 10
            assert g._rate_limit_info.send_x_headers == True
            assert res.status_code == 200

            res = c.get('/limit')
            assert g._rate_limit_info.limit == 2
            assert g._rate_limit_info.remaining == 0
            assert g._rate_limit_info.limit_exceeded == True
            assert g._rate_limit_info.per == 10
            assert g._rate_limit_info.send_x_headers == True
            assert res.get_data() == 'Rate limit was exceeded'
            assert res.status_code == 429

            res = c.get('/limit')
            assert g._rate_limit_info.limit == 2
            assert g._rate_limit_info.remaining == 0
            assert g._rate_limit_info.limit_exceeded == True
            assert res.status_code == 429

    def test_set_backend(self):
        rl = RateLimiter(self.app)
        rl.set_backend('SimpleRedisBackend')

        @self.app.route('/limit2')
        @ratelimit(current_app, 3, 5)
        def test_limit2():
            return 'limit'

        with self.app.test_client() as c:
            res = c.get('/limit2')
            assert request.endpoint == 'test_limit2'
            assert g._rate_limit_info.remaining == 2
            assert res.get_data() == 'limit'

    def test_flask_cache_prefix(self):
        cache = Cache(self.app, config={'CACHE_TYPE': 'redis'})
        prefix = 'flask_cache_prefix'

        self.app.config.setdefault('CACHE_KEY_PREFIX', prefix)
        self.app.config.setdefault('RATELIMITER_BACKEND', 'FlaskCacheRedisBackend')
        self.app.config.setdefault('RATELIMITER_BACKEND_OPTIONS',
                                   {'cache': cache})
        r = RateLimiter(self.app)
        assert self.app.config['RATELIMITER_KEY_PREFIX'] == prefix



class TestGetBackend(FlaskTestCase):
    """
    Tests get_backend function.
    """

    def test_get_correct_backend(self):
        """
        tests get_backend function with correct input
        """
        backend = get_backend('SimpleRedisBackend')
        assert backend.__name__ == 'SimpleRedisBackend'

    def test_get_incorrect_backend(self):
        """
        tests get_backend function with incorrect input
        """
        assert get_backend('CrazyBackendX').__name__ == DEFAULT_BACKEND