# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""


from .helpers.models.base import ApiSchema


class Webhook:
    def __init__(self, model: ApiSchema) -> None:
        self._model = model
