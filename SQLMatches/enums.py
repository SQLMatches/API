# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

from enum import Enum


class MatchStatus(Enum):
    finished = 0
    live = 1


class DemoStatus(Enum):
    no_demo = 0
    processing = 1
    ready = 2
    too_large = 3
    expired = 4


class TeamSides(Enum):
    counter_terrorist = 0
    terrorist = 1
