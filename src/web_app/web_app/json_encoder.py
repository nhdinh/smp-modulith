import decimal
import json
from datetime import datetime, date
from decimal import Decimal
from functools import singledispatchmethod
from uuid import UUID

from foundation.value_objects import Money


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return '`' + str(o) + '`'  # ` is special, will be removed later
        return super(DecimalEncoder, self).default(o)


class JSONEncoder(json.JSONEncoder):
    @singledispatchmethod
    def default(self, obj: object) -> object:
        try:
            if hasattr(obj, 'serialize'):
                return obj.serialize()
            else:
                raise TypeError(f"Cannot serialize {type(obj)}")
        except:
            raise TypeError(f"Cannot serialize {type(obj)}")

    @default.register(Money)  # noqa: F811
    def serialize_money(self, obj: Money) -> object:
        return {"amount": str(obj.amount), "currency": obj.currency.iso_code}

    @default.register(datetime)  # noqa: F811
    def serialize_datetime(self, obj: datetime) -> str:
        return obj.isoformat()

    @default.register(date)  # noqa: F811
    def serialize_date(self, obj: date) -> str:
        return obj.isoformat()

    @default.register(UUID)  # noqa: F811
    def serialize_uuid(self, obj: UUID) -> str:
        return str(obj)

    @default.register(Decimal)  # noqa: F811
    def serialize_decimal(self, obj: Decimal) -> str:
        return json.dumps(obj, cls=DecimalEncoder).replace("\"`", '').replace("`\"", '')

    # @default.register(AddressType)
    # def serialize_store_address_type(self, obj: AddressType) -> str:
    #     return str(obj.value)

    # @default.register(PurchaseOrderStatus)
    # def serialize_purchase_order_status(self, obj: PurchaseOrderStatus) -> str:
    #     return str(obj.value)
    #
    # @default.register(RegistrationStatus)
    # def serialize_registration_status(self, obj: RegistrationStatus) -> str:
    #     return str(obj.value)
