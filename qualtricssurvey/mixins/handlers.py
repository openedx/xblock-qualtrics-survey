"""
This module defines all of the Mixins that provide components of XBlock-family
functionality, such as ScopeStorage, RuntimeServices, and Handlers.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import functools
import logging
import json
import urllib

import six
from webob import Response

from xblock.exceptions import JsonHandlerError

def parse_body_to_json(body_data):
    """
    Parse the request body and return JSON data.
    """
    split_data = body_data.split("&")
    body_data_json = {}
    for i in split_data:
        field, value = i.split("=")
        body_data_json[field] = value

    if body_data_json.get('CompletedDate') != "":
        body_data_json['CompletedDate'] = urllib.parse.unquote(body_data_json['CompletedDate'])

    return body_data_json

class QualtricsHandlersMixin:
    """
    A mixin provides all of the machinery needed for working with XBlock-style handlers.
    """

    @classmethod
    def x_www_form_handler(cls, func):
        """
        Wrap a handler to consume `application/x-www-form-urlencoded` data and produce JSON.

        Rather than a Request object, the method will now be passed the
        `application/x-www-form-urlencoded` body of the request. The request should be a POST request
        in order to use this method. Any data returned by the function
        will be JSON-encoded and returned as the response.

        The wrapped function can raise JsonHandlerError to return an error
        response with a non-200 status code.

        This decorator will return a 405 HTTP status code if the method is not
        POST.
        This decorator will return a 400 status code if the body contains
        invalid JSON.
        """
        @cls.handler
        @functools.wraps(func)
        def wrapper(self, request, suffix=''):
            """The wrapper function `json_handler` returns."""
            if request.method != "POST":
                return JsonHandlerError(405, "Method must be POST").get_response(allow=["POST"])
            try:
                request_json = parse_body_to_json(request.body.decode('utf-8'))
            except ValueError: 
                return JsonHandlerError(400, "Invalid `application/x-www-form-urlencoded` data in request body.").get_response()
            try:
                response = func(self, request_json, suffix)
            except JsonHandlerError as err:
                return err.get_response()
            if isinstance(response, Response):
                return response
            else:
                return Response(json.dumps(response), content_type='application/json', charset='utf8')
        return wrapper

    @classmethod
    def handler(cls, func):
        """
        A decorator to indicate a function is usable as a handler.

        The wrapped function must return a `webob.Response` object.
        """
        func._is_xblock_handler = True      # pylint: disable=protected-access
        return func

