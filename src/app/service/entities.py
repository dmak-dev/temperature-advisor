from typing import TypedDict
from app.service.enums import RoomType, Season


class TemperatureInput(TypedDict):
    room_type: RoomType
    season: Season


class TemperatureOutput(TypedDict):
    recommended_temperature: int
    season: Season
