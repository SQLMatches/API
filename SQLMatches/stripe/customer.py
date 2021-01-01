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


from typing import Tuple

from .models import CardModel
from .card import Card


class Customer:
    def __init__(self, id: str, context: object) -> None:
        self.id = id
        self._context = context

    def card(self, id: str) -> Card:
        """Used to interact with a card.

        Parameters
        ----------
        id : str

        Returns
        -------
        Card
        """

        return Card(self.id, id, self)

    async def create_card(self, number: str, exp_month: int,
                          exp_year: int, cvc: int,
                          name: str
                          ) -> Tuple[CardModel, Card]:
        """Used to create a card.

        Parameters
        ----------
        number : str
        exp_month : int
        exp_year : int
        cvc : int
        name : str

        Returns
        -------
        CardModel
        Card
        """

        data = await self._context.__post(
            "/customers/{}/sources".format(self.id),
            data={
                "source": {
                    "object": "card",
                    "number": number,
                    "exp_month": exp_month,
                    "exp_year": exp_year,
                    "cvc": cvc,
                    "name": name
                }
            }
        )

        return CardModel(**data), self.card(data["id"])
