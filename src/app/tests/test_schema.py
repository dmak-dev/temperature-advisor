import pytest
from marshmallow import ValidationError
from app.schema import (
    TemperatureRequestSchema,
    TemperatureResponseSchema,
    ErrorSchema,
)
from app.service.entities import TemperatureInput
from app.service.enums import RoomType, Season


class TestTemperatureRequestSchema:

    def setup_method(self):
        self.schema = TemperatureRequestSchema()

    def test_load__ok(self):
        data = self.schema.load({"room_type": "office", "season": "winter"})
        assert data == TemperatureInput(room_type=RoomType.OFFICE, season=Season.WINTER)

    def test_load__missing_season__raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load({"room_type": "office"})
        assert "season" in exc_info.value.messages

    def test_load__missing_room_type__raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load({"season": "winter"})
        assert "room_type" in exc_info.value.messages

    def test_load__invalid_room_type__raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load({"room_type": "invalid", "season": "winter"})
        assert "room_type" in exc_info.value.messages

    def test_load__invalid_season__raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load({"room_type": "office", "season": "invalid"})
        assert "season" in exc_info.value.messages

    def test_load__empty_body__raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load({})
        assert "room_type" in exc_info.value.messages
        assert "season" in exc_info.value.messages


class TestTemperatureResponseSchema:

    def setup_method(self):
        self.schema = TemperatureResponseSchema()

    def test_dump__with_data(self):
        data = self.schema.dump({
            "recommended_temperature": 22,
            "season": "winter",
        })
        assert data == {"recommended_temperature": 22, "season": "winter"}

    def test_dump__output_structure(self):
        data = self.schema.dump({
            "recommended_temperature": 24,
            "season": "autumn",
        })
        assert list(data.keys()) == ["recommended_temperature", "season"]
        assert data["recommended_temperature"] == 24
        assert data["season"] == "autumn"


class TestTemperatureRequestSchemaAllValues:

    def test_load__all_valid_combinations(self):
        schema = TemperatureRequestSchema()
        for room_type in RoomType:
            for season in Season:
                data = schema.load({
                    "room_type": room_type,
                    "season": season,
                })
                assert data == TemperatureInput(
                    room_type=room_type,
                    season=season,
                )


class TestErrorSchema:

    def test_dump__validation_error_format(self):
        schema = ErrorSchema()
        result = schema.dump({
            "error": "ValidationError",
            "details": {"season": ["Missing data for required field."]},
        })
        assert result == {
            "error": "ValidationError",
            "details": {"season": ["Missing data for required field."]},
        }

    def test_dump__service_exception_format(self):
        schema = ErrorSchema()
        result = schema.dump({
            "error": "TemperatureException",
            "details": "Неизвестный тип помещения.",
        })
        assert result == {
            "error": "TemperatureException",
            "details": "Неизвестный тип помещения.",
        }

    def test_dump__details_as_string(self):
        schema = ErrorSchema()
        result = schema.dump({
            "error": "TemperatureException",
            "details": "some error text",
        })
        assert result["details"] == "some error text"

    def test_dump__error_field_always_present(self):
        schema = ErrorSchema()
        result = schema.dump({
            "error": "TestError",
            "details": {},
        })
        assert "error" in result
        assert "details" in result
