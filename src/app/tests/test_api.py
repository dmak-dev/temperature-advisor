from app.service.entities import (
    TemperatureInput,
    TemperatureOutput,
)
from app.service.exceptions import TemperatureException


def test_temperature__ok(client, mocker):

    calc_result = TemperatureOutput(
        recommended_temperature=22,
        season="winter",
    )

    check_mock = mocker.patch(
        "app.service.main.TemperatureService.calc",
        return_value=calc_result,
    )

    response = client.post(
        path="/temperature",
        json={
            "room_type": "office",
            "season": "winter",
        },
    )

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.json["recommended_temperature"] == calc_result["recommended_temperature"]
    assert response.json["season"] == calc_result["season"]
    check_mock.assert_called_once_with(
        data=TemperatureInput(
            room_type="office",
            season="winter",
        ),
    )


def test_temperature__validation_error__bad_request(client, mocker):

    calc_mock = mocker.patch(
        "app.service.main.TemperatureService.calc",
    )

    response = client.post(
        path="/temperature",
        json={
            "room_type": "office",
        },
    )

    assert response.status_code == 400
    assert response.content_type == "application/json"
    calc_mock.assert_not_called()


def test_temperature__service_exception__internal_server_error(client, mocker):

    calc_mock = mocker.patch(
        "app.service.main.TemperatureService.calc",
        side_effect=TemperatureException(details="test error"),
    )

    response = client.post(
        path="/temperature",
        json={
            "room_type": "office",
            "season": "winter",
        },
    )

    assert response.status_code == 500
    assert response.content_type == "application/json"
    calc_mock.assert_called_once_with(
        data=TemperatureInput(
            room_type="office",
            season="winter",
        ),
    )


def test_temperature__unknown_room_type__bad_request(client, mocker):

    calc_mock = mocker.patch(
        "app.service.main.TemperatureService.calc",
    )

    response = client.post(
        path="/temperature",
        json={
            "room_type": "invalid_room",
            "season": "winter",
        },
    )

    assert response.status_code == 400
    assert response.content_type == "application/json"
    calc_mock.assert_not_called()


def test_temperature__empty_body__bad_request(client, mocker):

    calc_mock = mocker.patch(
        "app.service.main.TemperatureService.calc",
    )

    response = client.post(
        path="/temperature",
        data="",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.content_type == "application/json"
    calc_mock.assert_not_called()


def test_temperature__wrong_content_type__bad_request(client, mocker):

    calc_mock = mocker.patch(
        "app.service.main.TemperatureService.calc",
    )

    response = client.post(
        path="/temperature",
        data="not json",
        content_type="text/plain",
    )

    assert response.status_code == 400
    assert response.content_type == "application/json"
    calc_mock.assert_not_called()


def test_temperature__integration(client):

    response = client.post(
        path="/temperature",
        json={
            "room_type": "office",
            "season": "winter",
        },
    )

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.json == {"recommended_temperature": 22, "season": "winter"}


def test_temperature__json_body_not_object__bad_request(client, mocker):

    calc_mock = mocker.patch(
        "app.service.main.TemperatureService.calc",
    )

    response = client.post(
        path="/temperature",
        json=["office", "winter"],
    )

    assert response.status_code == 400
    assert response.content_type == "application/json"
    assert response.json["error"] == "BadRequest"
    assert "объектом JSON" in response.json["details"]
    calc_mock.assert_not_called()


def test_temperature__missing_field__russian_message(client, mocker):

    mocker.patch(
        "app.service.main.TemperatureService.calc",
    )

    response = client.post(
        path="/temperature",
        json={"room_type": "office"},
    )

    assert response.status_code == 400
    assert response.json["details"]["season"] == ["Поле обязательно"]


def test_temperature__unknown_value__russian_message(client, mocker):

    mocker.patch(
        "app.service.main.TemperatureService.calc",
    )

    response = client.post(
        path="/temperature",
        json={"room_type": "garage", "season": "winter"},
    )

    assert response.status_code == 400
    assert response.json["details"]["room_type"] == [
        "Допустимые значения: office, home, warehouse."
    ]


def test_unknown_route__not_found__json(client):

    response = client.get(path="/unknown")

    assert response.status_code == 404
    assert response.content_type == "application/json"
    assert response.json["error"] == "NotFound"


def test_wrong_method__method_not_allowed__json(client):

    response = client.get(path="/temperature")

    assert response.status_code == 405
    assert response.content_type == "application/json"
    assert response.json["error"] == "MethodNotAllowed"


def test_temperature__unexpected_error__internal_server_error(app, client, mocker):

    app.config["PROPAGATE_EXCEPTIONS"] = False
    mocker.patch(
        "app.service.main.TemperatureService.calc",
        side_effect=RuntimeError("внутренний сбой"),
    )

    response = client.post(
        path="/temperature",
        json={
            "room_type": "office",
            "season": "winter",
        },
    )

    assert response.status_code == 500
    assert response.content_type == "application/json"
    assert response.json["error"] == "InternalServerError"
    assert response.json["details"] == "Внутренняя ошибка сервиса."
