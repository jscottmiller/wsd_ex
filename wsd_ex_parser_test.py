#!/usr/bin/python

from unittest import TestCase, main
from functools import partial
from wsd_ex_parser import * 


EXAMPLE_SIGNAL = "alice->bob:test"
EXAMPLE_SIGNAL_PARSED = (
    "signal",
    (("signal_participants",
     (("participant", "alice"),
      ("arrow", "->"),
      ("participant", "bob"))),
      ("colon", ":"),
      ("signal_body_line", "test")))


class WsdParserTests(TestCase):

    def __init__(self, *args, **kwargs):
        super(WsdParserTests, self).__init__(*args, **kwargs)
        self.maxDiff = None

    def test_can_parse_text(self):
        expectations = [
            ("", (False, ("test", ""), "")),
            ("test", (True, ("test", "test"), "")),
            ("test1", (True, ("test", "test"), "1")),
            (" test", (False, ("test", ""), " test")),
            ("testtest", (True, ("test", "test"), "test"))]
        self._check_expectations(
            expectations,
            partial(text_parser, "test", "test"))

    def test_can_parse_leading_whitespace(self):
        expectations = [
            ("", (True, ("ws", ""), "")),
            ("foo", (True, ("ws", ""), "foo")),
            (" foo", (True, ("ws", " "), "foo")),
            ("\tfoo", (True, ("ws", "\t"), "foo")),
            ("  foo", (True, ("ws", "  "), "foo")),
            ("\t\tfoo", (True, ("ws", "\t\t"), "foo")),
            ("\t foo", (True, ("ws", "\t "), "foo")),
            ("foo ", (True, ("ws", ""), "foo ")),
            ("foo\t", (True, ("ws", ""), "foo\t"))]
        self._check_expectations(
            expectations, 
            leading_whitespace_parser)

    def test_can_parse_one_or_many(self):
        expectations = [
            ("", (False, ("test", ()), "")),
            (":", (True, ("test", (("colon", ":"),)), "")),
            (":::",
             (True, 
              ("test",
               (("colon", ":"),
                ("colon", ":"),
                ("colon", ":"))), ""))]
        self._check_expectations(
            expectations,
            partial(one_or_many_parser, "test", [colon_parser]))

    def test_can_parse_arrow(self):
        expectations = [
            ("", (False, ("arrow", ""), "")),
            ("->", (True, ("arrow", "->"), "")),
            ("-->", (True, ("arrow", "-->"), "")),
            ("a->", (False, ("arrow", ""), "a->")),
            ("->the rest", (True, ("arrow", "->"), "the rest")),
            (" ->", (True, ("arrow", "->"), "")),
            ("- >", (False, ("arrow", ""), "- >"))]
        self._check_expectations(
            expectations, 
            arrow_parser)

    def test_can_parse_identifier(self):
        expectations = [
            ("foo", (True, ("identifier", "foo"), "")),
            ("foo ", (True, ("identifier", "foo"), " ")),
            (" foo", (True, ("identifier", "foo"), "")),
            ("", (False, ("identifier", ""), ""))]
        self._check_expectations(
            expectations,
            identifier_parser)

    def test_can_parse_left_participant(self):
        expectations = [
            ("", (False, ("participant", ""), "")),
            ("alice", (True, ("participant", "alice"), "")),
            (" alice", (True, ("participant", "alice"), "")),
            (" alice ", (True, ("participant", "alice "), "")),
            ("alice->", (True, ("participant", "alice"), "->")),
            ("alice ->", (True, ("participant", "alice"), " ->"))]
        self._check_expectations(
            expectations,
            left_participant_parser)

    def test_can_parse_signal_participants(self):
        expectations = [
            ("", (False, ("signal_participants", ()), "")),
            ("alice->", (False, ("signal_participants", ()), "alice->")),
            ("->bob", (False, ("signal_participants", ()), "->bob")),
            ("alice->bob", 
             (True, 
              ("signal_participants",
               (("participant", "alice"),
                ("arrow", "->"),
                ("participant", "bob"))), "")),
            ("  alice  ->bob", 
             (True, 
              ("signal_participants",
               (("participant", "alice"),
                ("arrow", "->"),
                ("participant", "bob"))), "")),
            ("alice->   bob ", 
             (True, 
              ("signal_participants",
               (("participant", "alice"),
                ("arrow", "->"),
                ("participant", "bob "))), ""))]
        self._check_expectations(
            expectations,
            signal_participants_parser)

    def test_can_parse_signal_body_line(self):
        expectations = [
            ("", (False, ("signal_body_line", ""), "")),
            ("test", (True, ("signal_body_line", "test"), "")),
            (" test ", (True, ("signal_body_line", " test "), "")),
            ("test\n", (True, ("signal_body_line", "test"), "\n")),
            ("test\nmore", (True, ("signal_body_line", "test"), "\nmore"))]
        self._check_expectations(
            expectations,
            signal_body_line_parser)

    def test_can_parse_signal(self):
        expectations = [
            ("", (False, ("signal", ()), "")),
            (EXAMPLE_SIGNAL, (True, EXAMPLE_SIGNAL_PARSED, ""))]
        self._check_expectations(
            expectations,
            signal_parser)

    def test_can_parse_statement(self):
        expectations = [
            ("", (False, ("statement", ""), "")),
            (EXAMPLE_SIGNAL, (True, EXAMPLE_SIGNAL_PARSED, ""))]
        self._check_expectations(
            expectations,
            statement_parser)

    def test_can_parse_wsd(self):
        expectations = [
            ("", (False, ("statement_list", ()), "")),
            ('\n'.join([EXAMPLE_SIGNAL] * 2), 
             (True, 
              ("statement_list",
               (EXAMPLE_SIGNAL_PARSED,
                EXAMPLE_SIGNAL_PARSED)), "")),
            ('\n'.join([EXAMPLE_SIGNAL] * 3), 
             (True, 
              ("statement_list",
               (EXAMPLE_SIGNAL_PARSED,
                EXAMPLE_SIGNAL_PARSED,
                EXAMPLE_SIGNAL_PARSED)), ""))]
        self._check_expectations(
            expectations,
            wsd_parser)

    def _check_expectations(self, expectations, function):
        for input, expected in expectations:
            actual = function(input)
            self.assertEqual(actual, expected)


if __name__ == '__main__':
    main()
