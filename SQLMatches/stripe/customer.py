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

from .card import Card

from .models import SubscriptionModel, CardModel
from .subscription import Subscription


class Customer:
    def __init__(self, id: str, context: object) -> None:
        self.id = id
        self._context = context

    async def create_subscription(self, unit_amount_decimal: float,
                                  currency: str,
                                  product_id: str,
                                  interval_days: int,
                                  cancel_at_period_end: bool = False
                                  ) -> Tuple[SubscriptionModel, Subscription]:
        """Used to create a subscription.

        Parameters
        ----------
        unit_amount_decimal : float
        currency : str
        product_id : str
        interval_days : int
        cancel_at_period_end : bool, optional
            by default False

        Returns
        -------
        SubscriptionModel
        Subscription
        """

        data = await self._context._post(
            "subscriptions",
            data={
                "customer": self.id,
                "cancel_at_period_end": cancel_at_period_end,
                "items[0][price_data][unit_amount_decimal]":
                unit_amount_decimal,
                "items[0][price_data][currency]": currency,
                "items[0][price_data][product]": product_id,
                "items[0][price_data][recurring][interval]": "day",
                "items[0][price_data][recurring][interval_count]":
                interval_days
            }
        )

        return (
            SubscriptionModel(**data),
            self._context.subscription(data["id"])
        )

    def card(self, id: str) -> Card:
        """Used to interact with a card.

        Parameters
        ----------
        id : str

        Returns
        -------
        Card
        """

        return Card(self.id, id, self._context)

    async def _token(self, number: str, exp_month: int,
                     exp_year: int, cvc: int,
                     name: str) -> str:
        """Used to create token.

        Parameters
        ----------
        number : str
        exp_month : int
        exp_year : int
        cvc : int
        name : str

        Returns
        -------
        str
        """

        return (await self._context._post(
            "tokens",
            data={
                "[card]number": number,
                "[card]exp_month": exp_month,
                "[card]exp_year": exp_year,
                "[card]cvc": cvc,
                "[card]name": name
            }
        ))["id"]

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
            Expects full year format.
        cvc : int
        name : str

        Returns
        -------
        CardModel
        Card
        """

        data = await self._context._post(
            "customers/{}/sources".format(self.id),
            data={
                "source": await self._token(
                    number, exp_month, exp_year,
                    cvc, name
                )
            }
        )

        return CardModel(**data), self.card(data["id"])
