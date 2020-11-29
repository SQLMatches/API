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


class SQLMatchesException(Exception):
    """Base Exception for SQLMatches.
    """

    def __init__(self, msg="SQLMatches Exception", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class UnSupportedEngine(SQLMatchesException):
    """Raised when the database engine isn't supported.
    """

    def __init__(self, msg="SQL Engine not supported", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class CommunityTaken(SQLMatchesException):
    """Raised when community name is taken.
    """

    def __init__(self, msg="Community name taken", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class AlreadyCommunity(SQLMatchesException):
    """Raised when user already owns a community.
    """

    def __init__(self, msg="User already owns a community", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class InvalidCommunity(SQLMatchesException):
    """Raised when community ID doesn't exist.
    """

    def __init__(self, msg="Invalid Community ID", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class NoOwnership(SQLMatchesException):
    """Raised when steam id doesn't own any communties.
    """

    def __init__(self, msg="User owns no communities", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class InvalidMatchID(SQLMatchesException):
    """Raised when match ID is invalid.
    """

    def __init__(self, msg="Invalid Match ID", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class InvalidAPIKey(SQLMatchesException):
    """Raised when API key is invalid.
    """

    def __init__(self, msg="Invalid API Key", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class DemoAlreadyUploaded(SQLMatchesException):
    """Raised when a demo has already been uploaded.
    """

    def __init__(self, msg="Demo already uploaded", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class InvalidSteamID(SQLMatchesException):
    """Raised when Steam ID isn't valid
    """

    def __init__(self, msg="Invalid Steam ID", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class InvalidCommunityName(SQLMatchesException):
    """Raised when community name isn't alphanumeric
       or character length is above 32 or below 4.
    """

    def __init__(self, msg="Commany Name not alphanumeric", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class InvalidCommunityType(SQLMatchesException):
    """Raised when community type isn't valid.
    """

    def __init__(self, msg="Commany type invalid", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class UserExists(SQLMatchesException):
    """Raised when user exists.
    """

    def __init__(self, msg="User exists", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class InvalidUploadSize(SQLMatchesException):
    """Raised when upload size is incorrect.
    """

    def __init__(self, msg="Must be between 50 & 100 MB", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
