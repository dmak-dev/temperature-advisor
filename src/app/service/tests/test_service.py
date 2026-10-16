import pytest
from app.service.main import (
    TemperatureService,
    OfficeTemperature,
    HomeTemperature,
    WarehouseTemperature,
    TEMPERATURE_MAP,
    STRATEGY_MAP,
)
from app.service.enums import RoomType, Season
from app.service.entities import TemperatureInput, TemperatureOutput
from app.service.exceptions import TemperatureException


class TestStrategySelection:

    def test_calc__calls_office_strategy(self, mocker):
        mock = mocker.patch("app.service.main.OfficeTemperature.calculate")
        service = TemperatureService()
        service.calc(TemperatureInput(room_type="office", season="winter"))
        mock.assert_called_once()

    def test_calc__calls_home_strategy(self, mocker):
        mock = mocker.patch("app.service.main.HomeTemperature.calculate")
        service = TemperatureService()
        service.calc(TemperatureInput(room_type="home", season="summer"))
        mock.assert_called_once()

    def test_calc__calls_warehouse_strategy(self, mocker):
        mock = mocker.patch("app.service.main.WarehouseTemperature.calculate")
        service = TemperatureService()
        service.calc(TemperatureInput(room_type="warehouse", season="spring"))
        mock.assert_called_once()

    def test_strategy_map_has_all_room_types(self):
        assert set(STRATEGY_MAP.keys()) == set(list(RoomType))


class TestTemperatureService:

    def test_calc__office(self):
        service = TemperatureService()
        data = TemperatureInput(room_type="office", season="winter")
        result = service.calc(data)
        assert result == TemperatureOutput(recommended_temperature=22, season="winter")

    def test_calc__home(self):
        service = TemperatureService()
        data = TemperatureInput(room_type="home", season="summer")
        result = service.calc(data)
        assert result == TemperatureOutput(recommended_temperature=23, season="summer")

    def test_calc__warehouse(self):
        service = TemperatureService()
        data = TemperatureInput(room_type="warehouse", season="spring")
        result = service.calc(data)
        assert result == TemperatureOutput(recommended_temperature=14, season="spring")

    def test_calc__unknown_room_type__raises_exception(self):
        service = TemperatureService()
        data = TemperatureInput(room_type="unknown", season="winter")
        with pytest.raises(TemperatureException):
            service.calc(data)

    def test_calc__all_room_types_all_seasons(self):
        service = TemperatureService()
        for room_type in RoomType:
            for season in Season:
                data = TemperatureInput(room_type=room_type, season=season)
                result = service.calc(data)
                expected_temp = TEMPERATURE_MAP[room_type][season]
                assert result == TemperatureOutput(
                    recommended_temperature=expected_temp,
                    season=season,
                )


class TestConcreteStrategies:

    def test_office_temperature(self):
        strategy = OfficeTemperature()
        data = TemperatureInput(room_type="office", season="winter")
        result = strategy.calculate(data)
        assert result == TemperatureOutput(recommended_temperature=22, season="winter")

    def test_home_temperature(self):
        strategy = HomeTemperature()
        data = TemperatureInput(room_type="home", season="autumn")
        result = strategy.calculate(data)
        assert result == TemperatureOutput(recommended_temperature=22, season="autumn")

    def test_warehouse_temperature(self):
        strategy = WarehouseTemperature()
        data = TemperatureInput(room_type="warehouse", season="summer")
        result = strategy.calculate(data)
        assert result == TemperatureOutput(recommended_temperature=18, season="summer")


class TestTemperatureMap:

    def test_office_temperatures(self):
        assert TEMPERATURE_MAP[RoomType.OFFICE] == {
            Season.WINTER: 22,
            Season.SPRING: 21,
            Season.SUMMER: 23,
            Season.AUTUMN: 21,
        }

    def test_home_temperatures(self):
        assert TEMPERATURE_MAP[RoomType.HOME] == {
            Season.WINTER: 24,
            Season.SPRING: 22,
            Season.SUMMER: 23,
            Season.AUTUMN: 22,
        }

    def test_warehouse_temperatures(self):
        assert TEMPERATURE_MAP[RoomType.WAREHOUSE] == {
            Season.WINTER: 16,
            Season.SPRING: 14,
            Season.SUMMER: 18,
            Season.AUTUMN: 14,
        }
