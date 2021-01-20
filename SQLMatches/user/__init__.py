# -*- coding: utf-8 -*-

"""
GNU General Public License v3.0 (GPL v3)
Copyright (c) 2020-2021 WardPearce
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


from datetime import datetime

from ..tables import user_table
from ..resources import Sessions

from ..exceptions import UserExists
from .models import UserModel


async def create_user(steam_id: int, name: str) -> UserModel:
    """Used to create a user.

    Parameters
    ----------
    steam_id : int
    name : str

    Returns
    -------
    UserModel

    Raises
    ------
    UserExists
    """

    now = datetime.now()

    query = user_table.insert().values(
        steam_id=steam_id,
        name=name,
        timestamp=now
    )

    try:
        await Sessions.database.execute(query=query)
    except Exception:
        raise UserExists()
    else:
        return UserModel(data={
            "steam_id": steam_id,
            "name": name,
            "timestamp": now
        })
