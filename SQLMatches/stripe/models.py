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


from typing import Dict, List, Any


class RecurringModel:
    aggregate_usage: None
    interval: str
    interval_count: int
    usage_type: str
    metadata: Dict[str, Any]

    def __init__(self, **kwargs) -> None:
        self.aggregate_usage = kwargs.get("aggregate_usage")
        self.interval = kwargs.get("interval")
        self.interval_count = kwargs.get("interval_count")
        self.usage_type = kwargs.get("usage_type")
        self.metadata = kwargs.get("metadata")


class PriceModel:
    id: str
    object: str
    active: bool
    billing_scheme: str
    created: int
    currency: str
    livemode: bool
    lookup_key: None
    nickname: None
    product: str
    recurring: RecurringModel
    tiers_mode: None
    transform_quantity: None
    type: str
    unit_amount: int
    unit_amount_decimal: int
    metadata: Dict[str, Any]

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id")
        self.object = kwargs.get("object")
        self.active = kwargs.get("active")
        self.billing_scheme = kwargs.get("billing_scheme")
        self.created = kwargs.get("created")
        self.currency = kwargs.get("currency")
        self.livemode = kwargs.get("livemode")
        self.lookup_key = kwargs.get("lookup_key")
        self.nickname = kwargs.get("nickname")
        self.product = kwargs.get("product")
        self.recurring = RecurringModel(
            **kwargs["recurring"]
        ) if "recurring" in kwargs else None
        self.tiers_mode = kwargs.get("tiers_mode")
        self.transform_quantity = kwargs.get("transform_quantity")
        self.type = kwargs.get("type")
        self.unit_amount = kwargs.get("unit_amount")
        self.unit_amount_decimal = kwargs.get("unit_amount_decimal")
        self.metadata = kwargs.get("metadata")


class DatumModel:
    id: str
    object: str
    billing_thresholds: None
    created: int
    price: PriceModel
    quantity: int
    subscription: str
    tax_rates: List[Any]
    metadata: Dict[str, Any]

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id")
        self.object = kwargs.get("object")
        self.billing_thresholds = kwargs.get("billing_thresholds")
        self.created = kwargs.get("created")
        self.price = PriceModel(
            **kwargs["price"]
        ) if "price" in kwargs else None
        self.quantity = kwargs.get("quantity")
        self.subscription = kwargs.get("subscription")
        self.tax_rates = kwargs.get("tax_rates")
        self.metadata = kwargs.get("metadata")


class ItemsModel:
    object: str
    data: List[DatumModel]
    has_more: bool
    url: str
    metadata: Dict[str, Any]

    def __init__(self, **kwargs) -> None:
        self.object = kwargs.get("kwargs")
        self.data = [
            DatumModel(**datum) for datum in kwargs["data"]
        ] if "data" in kwargs else None
        self.has_more = kwargs.get("has_more")
        self.url = kwargs.get("url")
        self.metadata = kwargs.get("metadata")


class InvoiceSettingsModel:
    custom_fields: str
    default_payment_method: None
    footer: str
    metadata: Dict[str, Any]

    def __init__(self, **kwargs) -> None:
        self.custom_fields = kwargs.get("custom_fields")
        self.default_payment_method = kwargs.get("default_payment_method")
        self.footer = kwargs.get("footer")
        self.metadata = kwargs.get("metadata")


class CustomerModel:
    id: str
    object: str
    address: str
    balance: int
    created: int
    currency: str
    default_source: str
    delinquent: bool
    description: str
    discount: float
    email: str
    invoice_prefix: str
    invoice_settings: InvoiceSettingsModel
    livemode: bool
    name: str
    next_invoice_sequence: int
    phone: str
    preferred_locales: List[Any]
    shipping: str
    tax_exempt: str
    metadata: Dict[str, Any]

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id")
        self.object = kwargs.get("object")
        self.address = kwargs.get("address")
        self.balance = kwargs.get("balance")
        self.created = kwargs.get("created")
        self.currency = kwargs.get("currency")
        self.default_source = kwargs.get("default_source")
        self.delinquent = kwargs.get("delinquent")
        self.description = kwargs.get("description")
        self.discount = kwargs.get("discount")
        self.email = kwargs.get("email")
        self.invoice_prefix = kwargs.get("invoice_prefix")
        self.invoice_settings = kwargs.get("invoice_settings")
        self.livemode = kwargs.get("livemode")
        self.name = kwargs.get("name")
        self.next_invoice_sequence = kwargs.get("next_invoice_sequence")
        self.phone = kwargs.get("phone")
        self.preferred_locales = kwargs.get("preferred_locales")
        self.shipping = kwargs.get("shipping")
        self.tax_exempt = kwargs.get("tax_exempt")
        self.metadata = kwargs.get("metadata")


class CardModel:
    id: str
    object: str
    address_city: str
    address_country: str
    address_line1: str
    address_line1_check: str
    address_line2: str
    address_state: str
    address_zip: int
    address_zip_check: str
    brand: str
    country: str
    customer: str
    cvc_check: str
    dynamic_last4: str
    exp_month: int
    exp_year: int
    fingerprint: str
    funding: str
    last4: int
    metadata: Dict[str, Any]
    name: str
    tokenization_method: str

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id")
        self.object = kwargs.get("object")
        self.address_city = kwargs.get("address_city")
        self.address_country = kwargs.get("address_country")
        self.address_line1 = kwargs.get("address_line1")
        self.address_line1_check = kwargs.get("address_line1_check")
        self.address_line2 = kwargs.get("address_line2")
        self.address_state = kwargs.get("address_state")
        self.address_zip = kwargs.get("address_zip")
        self.address_zip_check = kwargs.get("address_zip_check")
        self.brand = kwargs.get("brand")
        self.country = kwargs.get("country")
        self.customer = kwargs.get("customer")
        self.cvc_check = kwargs.get("cvc_check")
        self.dynamic_last4 = kwargs.get("dynamic_last4")
        self.exp_month = kwargs.get("exp_month")
        self.exp_year = kwargs.get("exp_year")
        self.fingerprint = kwargs.get("fingerprint")
        self.funding = kwargs.get("funding")
        self.last4 = kwargs.get("last4")
        self.metadata = kwargs.get("metadata")
        self.name = kwargs.get("name")
        self.tokenization_method = kwargs.get("tokenization_method")


class ProductModel:
    id: str
    object: str
    active: bool
    attributes: List[str]
    created: int
    description: str
    images: List[Any]
    livemode: bool
    metadata: Dict[str, Any]
    name: str
    statement_descriptor: None
    type: str
    unit_label: None
    updated: int

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id")
        self.object = kwargs.get("object")
        self.active = kwargs.get("active")
        self.type = kwargs.get("type")
        self.attributes = kwargs.get("attributes")
        self.created = kwargs.get("created")
        self.description = kwargs.get("description")
        self.images = kwargs.get("images")
        self.livemode = kwargs.get("livemode")
        self.metadata = kwargs.get("metadata")
        self.name = kwargs.get("name")
        self.statement_descriptor = kwargs.get("statement_descriptor")
        self.unit_label = kwargs.get("unit_label")
        self.updated = kwargs.get("updated")


class PlanModel:
    id: str
    object: str
    active: bool
    aggregate_usage: None
    amount: int
    amount_decimal: int
    billing_scheme: str
    created: int
    currency: str
    interval: str
    interval_count: int
    livemode: bool
    metadata: Dict[str, Any]
    nickname: str
    product: str
    tiers_mode: str
    transform_usage: None
    trial_period_days: int
    usage_type: str

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id")
        self.object = kwargs.get("object")
        self.active = kwargs.get("active")
        self.aggregate_usage = kwargs.get("aggregate_usage")
        self.amount = kwargs.get("amount")
        self.amount_decimal = kwargs.get("amount_decimal")
        self.billing_scheme = kwargs.get("billing_scheme")
        self.created = kwargs.get("created")
        self.currency = kwargs.get("currency")
        self.interval = kwargs.get("interval")
        self.interval_count = kwargs.get("interval_count")
        self.livemode = kwargs.get("livemode")
        self.metadata = kwargs.get("metadata")
        self.nickname = kwargs.get("nickname")
        self.product = kwargs.get("product")
        self.tiers_mode = kwargs.get("tiers_mode")
        self.transform_usage = kwargs.get("transform_usage")
        self.trial_period_days = kwargs.get("trial_period_days")
        self.usage_type = kwargs.get("usage_type")


class RecurringModel:
    aggregate_usage: None
    interval: str
    interval_count: int
    trial_period_days: int
    usage_type: str

    def __init__(self, **kwargs) -> None:
        self.aggregate_usage = kwargs.get("aggregate_usage")
        self.interval = kwargs.get("interval")
        self.interval_count = kwargs.get("interval_count")
        self.trial_period_days = kwargs.get("trial_period_days")
        self.usage_type = kwargs.get("usage_type")


class PriceModel:
    id: str
    object: str
    active: bool
    billing_scheme: str
    created: int
    currency: str
    livemode: bool
    lookup_key: str
    metadata: Dict[str, Any]
    nickname: str
    product: str
    recurring: RecurringModel
    tiers_mode: bool
    transform_quantity: None
    type: str
    unit_amount: int
    unit_amount_decimal: int

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id")
        self.object = kwargs.get("object")
        self.active = kwargs.get("active")
        self.billing_scheme = kwargs.get("billing_scheme")
        self.created = kwargs.get("created")
        self.currency = kwargs.get("currency")
        self.livemode = kwargs.get("livemode")
        self.lookup_key = kwargs.get("lookup_key")
        self.metadata = kwargs.get("metadata")
        self.nickname = kwargs.get("nickname")
        self.product = kwargs.get("product")
        self.recurring = kwargs.get("recurring")
        self.tiers_mode = kwargs.get("tiers_mode")
        self.transform_quantity = kwargs.get("transform_quantity")
        self.type = kwargs.get("type")
        self.unit_amount = kwargs.get("unit_amount")
        self.unit_amount_decimal = kwargs.get("unit_amount_decimal")


class DatumPriceModel:
    id: str
    object: str
    billing_thresholds: None
    created: int
    metadata: Dict[str, Any]
    plan: PlanModel
    price: PriceModel
    quantity: int
    subscription: str
    tax_rates: List[Any]

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id")
        self.object = kwargs.get("object")
        self.billing_thresholds = kwargs.get("billing_thresholds")
        self.created = kwargs.get("created")
        self.metadata = kwargs.get("metadata")
        self.plan = kwargs.get("plan")
        self.price = kwargs.get("price")
        self.quantity = kwargs.get("quantity")
        self.subscription = kwargs.get("subscription")
        self.tax_rates = kwargs.get("tax_rates")


class ItemsPriceModel:
    object: str
    data: List[DatumPriceModel]
    has_more: bool
    total_count: int
    url: str

    def __init__(self, **kwargs) -> None:
        self.object = kwargs.get("kwargs")
        self.data = [
            DatumPriceModel(**item) for item in kwargs["data"]
        ] if "data" in kwargs else None
        self.has_more = kwargs.get("has_more")
        self.total_count = kwargs.get("total_count")
        self.url = kwargs.get("url")


class SubscriptionModel:
    id: str
    object: str
    application_fee_percent: None
    billing_cycle_anchor: int
    billing_thresholds: None
    cancel_at: None
    cancel_at_period_end: bool
    canceled_at: None
    collection_method: str
    created: int
    current_period_end: int
    current_period_start: int
    customer: str
    days_until_due: None
    default_payment_method: None
    default_source: None
    default_tax_rates: List[Any]
    discount: None
    ended_at: None
    items: ItemsModel
    latest_invoice: str
    livemode: bool
    metadata: Dict[str, Any]
    next_pending_invoice_item_invoice: None
    pause_collection: None
    pending_invoice_item_interval: None
    pending_setup_intent: None
    pending_update: None
    plan: PlanModel
    quantity: int
    schedule: None
    start_date: int
    status: str
    transfer_data: None
    trial_end: None
    trial_start: None

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id")
        self.object = kwargs.get("object")
        self.application_fee_percent = kwargs.get("application_fee_percent")
        self.billing_cycle_anchor = kwargs.get("billing_cycle_anchor")
        self.billing_thresholds = kwargs.get("billing_thresholds")
        self.cancel_at = kwargs.get("cancel_at")
        self.cancel_at_period_end = kwargs.get("cancel_at_period_end")
        self.canceled_at = kwargs.get("canceled_at")
        self.collection_method = kwargs.get("collection_method")
        self.created = kwargs.get("created")
        self.current_period_end = kwargs.get("current_period_end")
        self.current_period_start = kwargs.get("current_period_start")
        self.customer = kwargs.get("customer")
        self.days_until_due = kwargs.get("days_until_due")
        self.default_payment_method = kwargs.get("default_payment_method")
        self.default_source = kwargs.get("default_source")
        self.default_tax_rates = kwargs.get("default_tax_rates")
        self.discount = kwargs.get("discount")
        self.ended_at = kwargs.get("ended_at")
        self.items = kwargs.get("items")
        self.latest_invoice = kwargs.get("latest_invoice")
        self.livemode = kwargs.get("livemode")
        self.metadata = kwargs.get("metadata")
        self.next_pending_invoice_item_invoice = (
            kwargs.get("next_pending_invoice_item_invoice")
        )
        self.pause_collection = kwargs.get("pause_collection")
        self.pending_invoice_item_interval = (
            kwargs.get("pending_invoice_item_interval")
        )
        self.pending_setup_intent = kwargs.get("pending_setup_intent")
        self.pending_update = kwargs.get("pending_update")
        self.plan = kwargs.get("plan")
        self.quantity = kwargs.get("quantity")
        self.schedule = kwargs.get("schedule")
        self.start_date = kwargs.get("start_date")
        self.status = kwargs.get("status")
        self.transfer_data = kwargs.get("transfer_data")
        self.trial_end = kwargs.get("trial_end")
        self.trial_start = kwargs.get("trial_start")


class SessionModel:
    id: str
    object: str
    created: int
    customer: str
    livemode: bool
    return_url: str
    url: str

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get("id")
        self.object = kwargs.get("object")
        self.created = kwargs.get("created")
        self.customer = kwargs.get("customer")
        self.livemode = kwargs.get("livemode")
        self.return_url = kwargs.get("return_url")
        self.url = kwargs.get("url")
