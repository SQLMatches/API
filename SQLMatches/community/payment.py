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


from typing import AsyncGenerator
from aiohttp.client_exceptions import ClientError
from sqlalchemy.sql import select, and_
from uuid import uuid4
from datetime import datetime

from ..resources import Sessions, Config

from ..tables import (
    community_table,
    payment_table
)

from ..misc import amount_to_upload_size

from ..exceptions import (
    InvalidCommunity,
    InvalidCard,
    InvalidPaymentID,
    NoActivePayment,
    NoPendingPayment,
    ActivePayment
)

from .models import (
    PaymentModel,
)


class CommunityPayment:
    @property
    def __payment_cols(self) -> list:
        return [
            payment_table.c.payment_id,
            payment_table.c.timestamp,
            payment_table.c.max_upload,
            payment_table.c.expires,
            payment_table.c.amount,
            payment_table.c.subscription_id,
            payment_table.c.receipt_url,
            payment_table.c.payment_status
        ]

    async def active_payment(self) -> PaymentModel:
        """Gets active payment.

        Returns
        -------
        PaymentModel

        Raises
        ------
        NoActivePayment
        """

        query = select(
            self.__payment_cols
        ).select_from(
            payment_table
        ).where(
            and_(
                payment_table.c.community_name == self.community_name,
                payment_table.c.expires >= datetime.now(),
                payment_table.c.payment_status == 1
            )
        )

        row = await Sessions.database.fetch_one(query)
        if row:
            return PaymentModel(**row)
        else:
            raise NoActivePayment()

    async def pending_payment(self) -> PaymentModel:
        """Used to get pending payment.

        Returns
        -------
        PaymentModel

        Raises
        ------
        NoPendingPayment
        """

        query = select(
            self.__payment_cols
        ).select_from(
            payment_table
        ).where(
            and_(
                payment_table.c.community_name == self.community_name,
                payment_table.c.expires >= datetime.now(),
                payment_table.c.payment_status == 0
            )
        )

        row = await Sessions.database.fetch_one(query)
        if row:
            return PaymentModel(**row)
        else:
            raise NoPendingPayment()

    async def payments(self) -> AsyncGenerator[PaymentModel, None]:
        """Used to get payments for a community.

        Yields
        ------
        PaymentModel
        """

        query = select(
            self.__payment_cols
        ).select_from(
            payment_table
        ).where(
            payment_table.c.community_name == self.community_name
        )

        async for row in Sessions.database.iterate(query):
            yield PaymentModel(**row)

    async def create_payment(self, amount: float) -> str:
        """Used to create a stripe subscription.

        Parameters
        ----------
        amount : float

        Returns
        -------
        str
            Payment ID

        Raises
        ------
        ActivePayment
        """

        try:
            community = await self.get()
        except InvalidCommunity:
            raise
        else:
            if community.payment_status not in (None, 2):
                raise ActivePayment()

            subscription, _ = await (Sessions.stripe.customer(
                community.customer_id
            )).create_subscription(
                unit_amount_decimal=amount * 100,
                currency=Config.currency,
                product_id=Config.product_id,
                interval_days=Config.payment_expires.days,
                cancel_at_period_end=False
            )

            payment_id = str(uuid4())
            upload_size = amount_to_upload_size(amount)
            now = datetime.now()

            query = payment_table.insert().values(
                subscription_id=subscription.id,
                payment_id=payment_id,
                amount=amount,
                community_name=self.community_name,
                max_upload=upload_size,
                timestamp=now,
                payment_status=0,
                expires=now + Config.payment_expires
            )

            await Sessions.database.execute(query)

            return payment_id

    async def decline_payment(self, payment_id: str) -> None:
        query = payment_table.update().values(
            payment_status=2
        ).where(
            and_(
                payment_table.c.payment_id == payment_id,
                payment_table.c.community_name == self.community_name
            )
        )

        await Sessions.database.execute(query)

    async def confirm_payment(self, payment_id: str,
                              receipt_url: str) -> PaymentModel:
        """Used to add a payment.

        Parameters
        ----------
        payment_id : str
        receipt_url : str
            Receipt URl given by stripe.

        Returns
        -------
        PaymentModel

        Raises
        ------
        InvalidCommunity
        """

        row = await Sessions.database.fetch_one(
            payment_table.select().where(
                and_(
                    payment_table.c.payment_id == payment_id,
                    payment_table.c.community_name == self.community_name
                )
            )
        )
        if not row:
            raise InvalidPaymentID()

        payment_status = 1

        query = payment_table.update().values(
            payment_status=payment_status,
            receipt_url=receipt_url.replace(Config.receipt_url_base, ""),
            expires=datetime.now() + Config.payment_expires
        ).where(
            and_(
                payment_table.c.payment_id == payment_id,
                payment_table.c.community_name == self.community_name
            )
        )

        await Sessions.database.execute(query)

        return PaymentModel(
            payment_id=row["payment_id"],
            subscription_id=row["subscription_id"],
            max_upload=row["max_upload"],
            timestamp=row["timestamp"],
            expires=row["expires"],
            amount=row["amount"],
            receipt_url=row["receipt_url"],
            payment_status=payment_status
        )

    async def add_card(self, number: str, exp_month: int,
                       exp_year: int, cvc: int,
                       name: str) -> str:
        """Used to create / update a card for a community.

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
            Stripe card ID.
        """

        community = await self.get()

        customer = Sessions.stripe.customer(
            community.customer_id
        )

        if community.card_id:
            # We'll just delete the card if exists.
            await (customer.card(
                community.card_id
            )).delete()

        try:
            data, _ = await customer.create_card(
                number, exp_month, exp_year, cvc, name
            )
        except ClientError:
            raise InvalidCard()
        else:
            await Sessions.database.execute(
                community_table.update().values(
                    card_id=data.id
                ).where(
                    community_table.c.community_name == self.community_name
                )
            )

            return data.id

    async def delete_card(self) -> None:
        community = await self.get()

        if community.card_id:
            await ((Sessions.stripe.customer(community.customer_id)).card(
                community.card_id
            )).delete()

            await Sessions.database.execute(
                community_table.update().values(
                    card_id=None
                ).where(
                    community_table.c.community_name == self.community_name
                )
            )
