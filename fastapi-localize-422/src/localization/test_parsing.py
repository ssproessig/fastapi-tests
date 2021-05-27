import unittest
from typing import Optional, List

from pydantic import ValidationError, BaseModel, AnyStrMaxLengthError, Field
from pydantic.error_wrappers import ErrorWrapper

from localization import parse_accept_language, localized_validation_exception_handler


class TestParseAcceptLanguageHeader(unittest.TestCase):
    def test_invalid_string_returns_empty_list(self):
        self.assertEqual(parse_accept_language(';'), [])

    def test_one_language(self):
        self.assertEqual(parse_accept_language('it'), [('it', 1.0)])

    def test_three_languages_with_q_value(self):
        self.assertEqual(parse_accept_language('de,it;q=0.9,iw;q=0.1'), [('de', 1.0), ('it', 0.9), ('iw', 0.1)])

    def test_broken_q_leads_to_0_0(self):
        self.assertEqual(parse_accept_language('en;qq=0.1)'), [('en', 0.0)])


class MockRequest:
    headers = dict()


class MockModel(BaseModel):
    name: str = Field(max_length=10)
    tags: Optional[List[str]] = []


class MockException:
    raw_errors = [
        ValidationError(
            errors=[ErrorWrapper(AnyStrMaxLengthError(limit_value=10), ('name',))],
            model=MockModel
        )
    ]


def _get_invocation(accept_language_header: str):
    request = MockRequest()
    request.headers["Accept-Language"] = accept_language_header
    try:
        MockModel(**{'name': '01234567890', 'tags': [None]})
    except Exception as exc:
        return request, exc


class TestLocalizedValidationExceptionHandler(unittest.TestCase):
    def test_requesting_no_language_uses_default(self):
        req, exc = _get_invocation('')
        r = localized_validation_exception_handler(req, exc)
        self.assertEqual(r.body,
                         b'{"detail":['
                         b'{"loc":["name"],"msg":"ensure this value has at most 10 characters",'
                         b'"type":"value_error.any_str.max_length","ctx":{"limit_value":10}'
                         b'},'
                         b'{"loc":["tags",0],"msg":"none is not an allowed value",'
                         b'"type":"type_error.none.not_allowed"}'
                         b']}')

    def test_requesting_unknown_language_uses_default(self):
        req, exc = _get_invocation('iw')
        r = localized_validation_exception_handler(req, exc)
        self.assertEqual(r.body,
                         b'{"detail":['
                         b'{"loc":["name"],"msg":"ensure this value has at most 10 characters",'
                         b'"type":"value_error.any_str.max_length","ctx":{"limit_value":10}'
                         b'},'
                         b'{"loc":["tags",0],"msg":"none is not an allowed value",'
                         b'"type":"type_error.none.not_allowed"}'
                         b']}')

    def test_requesting_known_language_uses_it(self):
        req, exc = _get_invocation('de')
        r = localized_validation_exception_handler(req, exc)
        self.assertEqual(r.body,
                         b'{"detail":['
                         b'{"loc":["name"],"msg":"Wert darf h\xc3\xb6chstens 10 Zeichen haben",'
                         b'"type":"value_error.any_str.max_length","ctx":{"limit_value":10}'
                         b'},'
                         b'{"loc":["tags",0],"msg":"(kein Wert) ist kein erlaubter Wert",'
                         b'"type":"type_error.none.not_allowed"}'
                         b']}')
