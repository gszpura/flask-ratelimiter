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

"""
Flask extension
===============

Flask-RateLimiter is initialized like this:

>>> from flask import Flask
>>> from flask_ratelimiter import RateLimiter
>>> app = Flask('myapp')
>>> ext = RateLimiter(app=app)
"""

from __future__ import absolute_import

from flask import current_app


class RateLimiter(object):
    """
    Flask extension

    Initialization of the extension:

    >>> from flask import Flask
    >>> from flask_ratelimiter import RateLimiter
    >>> app = Flask('myapp')
    >>> ext = RateLimiter(app=app)

    or alternatively using the factory pattern:

    >>> app = Flask('myapp')
    >>> ext = RateLimiter()
    >>> ext.init_app(app)
    """
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize a Flask application.
        """
        # Follow the Flask guidelines on usage of app.extensions
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        if 'ratelimiter' in app.extensions:
            raise RuntimeError("Flask application already initialized")
        app.extensions['ratelimiter'] = self


# Version information
from .version import __version__

__all__ = [
    'RateLimiter', '__version__'
]
