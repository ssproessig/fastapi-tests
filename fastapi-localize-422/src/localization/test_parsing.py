import unittest

from localization import parse_accept_language


class TestParseAcceptLanguageHeader(unittest.TestCase):
    def test_invalid_string_returns_empty_list(self):
        self.assertEqual(parse_accept_language(';'), [])

    def test_one_language(self):
        self.assertEqual(parse_accept_language('it'), [('it', 1.0)])

    def test_three_languages_with_q_value(self):
        self.assertEqual(parse_accept_language('de,it;q=0.9,iw;q=0.1'), [('de', 1.0), ('it', 0.9), ('iw', 0.1)])

    def test_broken_q_leads_to_0_0(self):
        self.assertEqual(parse_accept_language('en;qq=0.1)'), [('en', 0.0)])
