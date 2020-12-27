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


from typing import Any, Dict, Tuple
from aiohttp import ClientResponse
from functools import wraps

from ..resources import Sessions

from .models import SubscriptionModel, CustomerModel
from .subscription import Subscription


def add_auth(func):
    @wraps(func)
    def _add(*args, **kwargs):
        auth = args[0].authorization

        if "headers" in kwargs:
            kwargs["headers"]["Authorization"] = auth
        else:
            kwargs["headers"] = {
                "Authorization": auth
            }

        return func(*args, **kwargs)

    return _add


class Stripe:
    BASE_URL = "https://api.stripe.com/v1/"

    def __init__(self, api_key: str, testing: bool = False) -> None:
        """Used to interact with Stripe.

        Parameters
        ----------
        api_key : str
        testing : bool, optional
            Enable test mode, by default False
        """

        self.authorization = "Bearer sk_{}_{}".format(
            "test" if testing else "live", api_key
        )

    async def __handle(self, resp: ClientResponse) -> dict:
        resp.raise_for_status()
        return await resp.json()

    @add_auth
    async def __post(self, path: str, *args, **kwargs) -> dict:
        """Used to post to Stripe.

        Parameters
        ----------
        path : str
            Path to append to stripe API route.

        Returns
        -------
        dict
        """

        async with Sessions.aiohttp.post(url=self.BASE_URL + path,
                                         *args, **kwargs) as resp:
            return await self.__handle(resp)

    @add_auth
    async def __delete(self, path: str, *args, **kwargs) -> dict:
        """Used to delete something from Stripe.

        Parameters
        ----------
        path : str
            Path to append to stripe API route.

        Returns
        -------
        dict
        """

        async with Sessions.aiohttp.delete(url=self.BASE_URL + path,
                                           *args, **kwargs) as resp:
            return await self.__handle(resp)

    @add_auth
    async def __get(self, path: str, *args, **kwargs) -> dict:
        """Used to get Stripe data.

        Parameters
        ----------
        path : str
            Path to append to stripe API route.

        Returns
        -------
        dict
        """

        async with Sessions.aiohttp.get(url=self.BASE_URL + path,
                                        *args, **kwargs) as resp:
            return await self.__handle(resp)

    def subscription(self, id: str) -> Subscription:
        """Interact with a subscription.

        Parameters
        ----------
        id : str

        Returns
        -------
        Subscription
        """

        return Subscription(id, self)

    async def create_subscription(self, customer: str,
                                  items: Dict[str, Any],
                                  cancel_at_period_end: bool = False
                                  ) -> Tuple[SubscriptionModel, Subscription]:
        """Used to create a subscription.

        Parameters
        ----------
        customer : str
        items : Dict[str, Any]
        cancel_at_period_end : bool, optional
            by default False

        Returns
        -------
        SubscriptionModel
        """

        data = await self.__post(
            "subscriptions",
            json={
                "customer": customer,
                "items": items,
                "cancel_at_period_end": cancel_at_period_end
            }
        )

        return SubscriptionModel(**data), self.subscription(data["id"])

    async def create_customer(self, **kwargs) -> CustomerModel:
        """Used to create a customer.

        Returns
        -------
        CustomerModel
        """

        return CustomerModel(**(
            await self.__post("customers", json=kwargs)
        ))
