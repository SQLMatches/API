# -*- coding: utf-8 -*-

"""
GNU General Public License v3.0 (GPL v3)
Copyright (c) 2020-2020 WardPearce
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import validators
import re

from .resources import Config
from .exceptions import (
    InvalidWebhook,
    InvalidCommunityName,
    InvalidCommunityType,
    InvalidUploadSize
)


def validate_webhooks(func):
    def _validate(*args, **kwargs):
        for param in ["match_start_webhook", "round_end_webhook",
                      "match_end_webhook"]:
            if param in kwargs and kwargs[param]:
                try:
                    validators.url(kwargs[param])
                except OSError:
                    raise InvalidWebhook()

        return func(*args, **kwargs)

    return _validate


def validate_community_name(func):
    def _validate(*args, **kwargs):
        if not re.match("^[a-zA-Z0-9]{4,32}$", kwargs["community_name"]):
            raise InvalidCommunityName()

        return func(*args, **kwargs)

    return _validate


def validate_community_type(func):
    def _validate(*args, **kwargs):
        if ("community_type" in kwargs and
            (kwargs["community_type"] and kwargs["community_type"] not in
                Config.community_types)):
            raise InvalidCommunityType()

        return func(*args, **kwargs)

    return _validate


def validate_max_upload(func):
    def _validate(*args, **kwargs):
        if "max_upload" in kwargs and kwargs["max_upload"] and (
            kwargs["max_upload"] < Config.free_upload_size or
                kwargs["max_upload"] > Config.max_upload_size):

            raise InvalidUploadSize()

        return func(*args, **kwargs)

    return _validate
