from typing import List, Tuple

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic.error_wrappers import flatten_errors
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY


class Default:
    error_msg_templates = BaseModel.Config.error_msg_templates


class German:
    error_msg_templates = {
        'value_error.any_str.max_length': 'Wert darf höchstens {limit_value} Zeichen haben',
        'type_error.none.not_allowed': '(kein Wert) ist kein erlaubter Wert'
    }


TRANSLATIONS = {
    "de": German,
    "en": Default
}


def parse_accept_language(accept_language_value: str) -> List[Tuple[str, float]]:
    languages = accept_language_value.split(",")
    locale_q_pairs = []

    for language in languages:
        language_split = language.split(";")
        locale = language_split[0].strip()

        if locale:
            if len(language_split) == 1:
                q = 1.0
            else:
                try:
                    q = float(language_split[1][2:])
                except ValueError:
                    q = 0.0

            locale_q_pairs.append((locale, q))

    return sorted(locale_q_pairs, key=lambda p: p[1], reverse=True)


def localized_validation_exception_handler(request, exc):
    config = next(
        (TRANSLATIONS[locale] for locale, q in parse_accept_language(request.headers.get("Accept-Language", "*"))
         if locale in TRANSLATIONS
         ), Default)

    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(list(flatten_errors(exc.raw_errors, config)))},
    )
