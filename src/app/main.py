from flask import (
    Flask,
    request,
    render_template,
)
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError
from flasgger import Swagger
from app.service.main import TemperatureService
from app.service import messages
from app.service.exceptions import ServiceException
from app.schema import (
    TemperatureRequestSchema,
    TemperatureResponseSchema,
    ErrorSchema,
)

# Тексты ошибок маршрутизации: у HTTPException они английские по умолчанию.
ROUTING_ERRORS = {
    404: ("NotFound", "Маршрут не найден."),
    405: ("MethodNotAllowed", "Метод не поддерживается для этого маршрута."),
}

# Служебные тексты marshmallow на русском: остальные ответы сервиса русские,
# и англоязычная вставка в теле ошибки выглядит как незакрытый угол.
MARSHMALLOW_MESSAGES = {
    "Missing data for required field.": "Поле обязательно",
    "Not a valid string.": "Ожидается строка",
    "Unknown field.": "Неизвестное поле",
    "Invalid input type.": "Ожидается объект JSON",
}


def _translate_details(details):
    """Переводит тексты marshmallow, сохраняя структуру словаря ошибок."""

    if isinstance(details, dict):
        return {key: _translate_details(value) for key, value in details.items()}
    if isinstance(details, list):
        return [_translate_details(item) for item in details]
    return MARSHMALLOW_MESSAGES.get(details, details)


def create_app():

    app = Flask(__name__)
    # Кириллица в ответах читается без экранирования: удобно и в curl, и в Swagger.
    app.json.ensure_ascii = False
    Swagger(app, template={
        "info": {
            "title": "Подбор температуры в помещении",
            "version": "1.0.0",
            "description": (
                "Сервис рекомендует температуру по типу помещения и сезону. "
                "Открытая документация: POST /temperature."
            ),
        },
    })

    def _error(name: str, details, code: int):
        """Ответ об ошибке: одинаковая форма для всех кодов."""
        return ErrorSchema().dump({"error": name, "details": details}), code

    def _get_json_body():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return None, _error(
                "BadRequest", messages.MSG_BODY_MUST_BE_OBJECT, 400
            )
        return data, None

    @app.errorhandler(HTTPException)
    def handle_routing_error(ex):
        """404 и 405 отдаются той же схемой ошибки, а не страницей HTML."""
        name, details = ROUTING_ERRORS.get(ex.code, ("HttpError", ex.description))
        return _error(name, details, ex.code)

    @app.errorhandler(Exception)
    def handle_unexpected_error(ex):
        """Необработанная ошибка отдаётся в формате API без подробностей."""
        app.logger.exception("Непредвиденная ошибка: %s", ex)
        return _error("InternalServerError", messages.MSG_INTERNAL_ERROR, 500)

    @app.route("/", methods=["GET"])
    def template():
        return render_template("base.html")

    @app.route("/temperature", methods=["POST"])
    def temperature():

        """
        Подбор температуры в помещении
        ---
        tags:
          - Temperature
        consumes:
          - application/json
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [room_type, season]
              properties:
                room_type:
                  type: string
                  example: "office"
                season:
                  type: string
                  example: "winter"
        responses:
          200:
            description: Рекомендуемая температура
            schema:
              type: object
              properties:
                recommended_temperature:
                  type: integer
                  example: 22
                season:
                  type: string
                  example: "winter"
          400:
            description: Ошибка валидации
          500:
            description: Ошибка сервиса
        """

        data, err = _get_json_body()
        if err:
            return err

        service = TemperatureService()
        load_schema = TemperatureRequestSchema()
        dump_schema = TemperatureResponseSchema()

        try:
            result = service.calc(
                data=load_schema.load(data),
            )
        except ValidationError as ex:
            return _error("ValidationError", _translate_details(ex.messages), 400)
        except ServiceException as ex:
            return _error(
                "TemperatureException", ex.details or ex.message, 500
            )
        else:
            return dump_schema.dump(result), 200

    return app


app = create_app()
