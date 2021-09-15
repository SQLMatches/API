# -*- coding: utf-8 -*-

"""
GNU Affero General Public License v3.0
https://github.com/SQLMatches/API/blob/Development/LICENSE
"""

import unittest
import sys

from SQLMatches.tests import *   # noqa: F403, F401


if __name__ == "__main__":
    # We don't want unit test touching cli args.
    unittest.main(argv=[sys.argv[0]])
