from marshmallow import Schema, fields


class DecimalField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return float(value)


class ItemSchema(Schema):
    price = DecimalField()


products_schema = ItemSchema()
