from marshmallow import Schema, validate
from marshmallow.fields import (
    Integer,
    String,
    Raw,
)
from marshmallow.decorators import post_load
from app.service.entities import TemperatureInput
from app.service.enums import RoomType, Season


class TemperatureRequestSchema(Schema):

    room_type = String(
        required=True,
        validate=validate.OneOf(
            list(RoomType),
            error=f"Допустимые значения: {', '.join(RoomType)}.",
        ),
        error_messages={"required": "Поле обязательно", "invalid": "Ожидается строка"},
    )
    season = String(
        required=True,
        validate=validate.OneOf(
            list(Season),
            error=f"Допустимые значения: {', '.join(Season)}.",
        ),
        error_messages={"required": "Поле обязательно", "invalid": "Ожидается строка"},
    )

    @post_load
    def make_temperature_input(self, data, **kwargs) -> TemperatureInput:
        return TemperatureInput(**data)


class TemperatureResponseSchema(Schema):

    recommended_temperature = Integer()
    season = String()


class ErrorSchema(Schema):

    error = String(required=True)
    details = Raw(required=True)
