from abc import ABC, abstractmethod
from app.service.enums import RoomType, Season
from app.service.entities import TemperatureInput, TemperatureOutput
from app.service import exceptions, messages


TEMPERATURE_MAP = {
    RoomType.OFFICE: {
        Season.WINTER: 22,
        Season.SPRING: 21,
        Season.SUMMER: 23,
        Season.AUTUMN: 21,
    },
    RoomType.HOME: {
        Season.WINTER: 24,
        Season.SPRING: 22,
        Season.SUMMER: 23,
        Season.AUTUMN: 22,
    },
    RoomType.WAREHOUSE: {
        Season.WINTER: 16,
        Season.SPRING: 14,
        Season.SUMMER: 18,
        Season.AUTUMN: 14,
    },
}


class TemperatureAdvisor(ABC):

    @abstractmethod
    def calculate(self, data: TemperatureInput) -> TemperatureOutput:
        pass

    def _calc_for(self, room_type_key: str, data: TemperatureInput) -> TemperatureOutput:
        return TemperatureOutput(
            recommended_temperature=TEMPERATURE_MAP[room_type_key][data["season"]],
            season=data["season"],
        )


class OfficeTemperature(TemperatureAdvisor):

    def calculate(self, data: TemperatureInput) -> TemperatureOutput:
        return self._calc_for(RoomType.OFFICE, data)


class HomeTemperature(TemperatureAdvisor):

    def calculate(self, data: TemperatureInput) -> TemperatureOutput:
        return self._calc_for(RoomType.HOME, data)


class WarehouseTemperature(TemperatureAdvisor):

    def calculate(self, data: TemperatureInput) -> TemperatureOutput:
        return self._calc_for(RoomType.WAREHOUSE, data)


STRATEGY_MAP = {
    RoomType.OFFICE: OfficeTemperature,
    RoomType.HOME: HomeTemperature,
    RoomType.WAREHOUSE: WarehouseTemperature,
}


class TemperatureService:

    def calc(self, data: TemperatureInput) -> TemperatureOutput:
        room_type: str = data["room_type"]

        strategy_class = STRATEGY_MAP.get(room_type)
        if strategy_class is None:
            raise exceptions.TemperatureException(
                details=messages.MSG_UNKNOWN_ROOM_TYPE
            )

        strategy = strategy_class()
        return strategy.calculate(data)
