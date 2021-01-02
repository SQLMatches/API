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


import json
from typing import Tuple
from aiohttp import ClientResponse
from functools import wraps

from ..resources import Sessions

from .models import CustomerModel, ProductModel
from .subscription import Subscription
from .customer import Customer


def add_headers(func):
    @wraps(func)
    def _add(*args, **kwargs):
        auth = (args[0]._context.authorization if hasattr(args[0], "_context")
                else args[0].authorization)

        if "headers" in kwargs:
            kwargs["headers"]["Authorization"] = auth
            kwargs["headers"]["Content-Type"] = \
                "application/x-www-form-urlencoded"
        else:
            kwargs["headers"] = {
                "Authorization": auth,
                "Content-Type": "application/x-www-form-urlencoded"
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

    @add_headers
    async def _post(self, path: str, *args, **kwargs) -> dict:
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

    @add_headers
    async def _delete(self, path: str, *args, **kwargs) -> dict:
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

    @add_headers
    async def _get(self, path: str, *args, **kwargs) -> dict:
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

    def customer(self, id: str) -> Customer:
        """Used to interact with customer.

        Parameters
        ----------
        id : str

        Returns
        -------
        Customer
        """

        return Customer(id, self)

    async def create_product(self, name: str) -> ProductModel:
        """Used to create a product.

        Parameters
        ----------
        name : str

        Returns
        -------
        ProductModel
        """

        data = await self._post("products", data={
            "name": name
        })

        return ProductModel(**data)

    async def create_customer(self, **kwargs
                              ) -> Tuple[CustomerModel, Customer]:
        """Used to create a customer.

        Returns
        -------
        CustomerModel
        """

        data = await self._post("customers", data=kwargs)

        return CustomerModel(**data), self.customer(data["id"])
