#!/usr/bin/python

from re import compile
from sys import argv
from functools import partial, wraps
from logging import info, basicConfig


ID_RE = compile("\w+")
ARROW_RE = compile("\-\-?>")
WS_RE = compile("[ \t]*")
INTER_STATEMENT_WS_RE = compile("[ \t\n\r]*\n")


#basicConfig(level='INFO')
def logged(f):
    @wraps(f)
    def log_call(*args, **kwargs):
        info("Calling %s with (%s, %s)" % (f, args, kwargs))
        result = f(*args, **kwargs)
        info("Returning from %s with %s" % (f, result))
        return result
    return log_call


@logged
def wsd_parser(diagram):
    def rm_whitespace(out):
        status, ast, state = out
        filtered = [
            t for t in ast[1]
            if t[0] not in ["interstatement_ws", "eof"]]
        return (status, (ast[0], tuple(filtered)), state)

    line_ending_or_eof_parser = partial(
        or_parser,
        "ignored",
        [
            eof_parser,
            interstatement_whitespace_parser
        ])

    return rm_whitespace(one_or_many_parser(
        "statement_list",
        [
            statement_parser,
            line_ending_or_eof_parser
        ],
        diagram))


@logged
def statement_parser(diagram):
    return or_parser(
        "statement",
        [
            signal_parser
        ],
        diagram)


@logged
def signal_parser(diagram):
    sp = signal_participants_parser(diagram)
    c = colon_parser(sp[2])
    sb = signal_body_line_parser(c[2])

    if not (sp[0] and c[0] and sb[0]):
        return (False, ("signal", ""), diagram)

    return (True, ("signal", (sp[1], c[1], sb[1])), sb[2])


@logged
def signal_body_line_parser(diagram):
    return not_parser(
        "signal_body_line", 
        partial(
            or_parser,
            "ignored",
            [
                interstatement_whitespace_parser,
                eof_parser 
            ]),
        diagram)


@logged
def signal_participants_parser(diagram):
    p1 = left_participant_parser(diagram)
    arrow = arrow_parser(p1[2])
    p2 = right_participant_parser(arrow[2])

    if not (p1[0] and arrow[0] and p2[0]):
        return (False, ("signal_participants", ""), diagram)

    return (True, ("signal_participants", (p1[1], arrow[1], p2[1])), p2[2])


@logged
def left_participant_parser(diagram):
    return sequence_parser(
        [leading_whitespace_parser,
         partial(not_parser, "participant", arrow_parser)],
        diagram)


@logged
def right_participant_parser(diagram):
    return sequence_parser(
        [leading_whitespace_parser,
         partial(not_parser, "participant", colon_parser)],
        diagram)


@logged
def identifier_parser(diagram):
    return sequence_parser(
        [leading_whitespace_parser,
         partial(re_parser, "identifier", ID_RE)],
        diagram)


@logged
def arrow_parser(diagram):
   return sequence_parser(
        [leading_whitespace_parser,
         partial(re_parser, "arrow", ARROW_RE)],
        diagram)


@logged
def colon_parser(diagram):
    return text_parser("colon", ":", diagram)


@logged
def one_or_many_parser(name, parsers, diagram):
    results = []
    while True:
        result = list_parser(name, parsers, diagram)
        if not result[0]:
            break
        diagram = result[2]
        results.extend(list(result[1][1]))
    return (len(results) > 0, (name, tuple(results)), diagram)


@logged
def list_parser(name, parsers, diagram):
    results = []
    for parser in parsers:
        result = parser(diagram)
        if not result[0]:
            return (False, (name, ()), diagram)
        diagram = result[2]
        results.append(result[1])
    return (True, (name, tuple(results)), diagram)


@logged
def sequence_parser(parsers, diagram):
    result = (False, ("empty_sequence", ""), diagram)
    for parser in parsers:
        result = parser(result[2])
        if not result[0]:
            return (False, (result[1][0], ""), diagram)
    return result


@logged
def interstatement_whitespace_parser(diagram):
    return re_parser("interstatement_ws", INTER_STATEMENT_WS_RE, diagram)


@logged
def leading_whitespace_parser(diagram):
    return re_parser("ws", WS_RE, diagram)


@logged
def not_parser(name, parser, diagram):
    if not diagram:
        return (False, (name, diagram), "")
    for i in range(len(diagram)):
        result = parser(diagram[i:])
        if result[0]:
            return (i != 0, (name, diagram[:i]), diagram[i:])
    return (True, (name, diagram), "")


@logged
def or_parser(name, parsers, diagram):
    for parser in parsers:
        result = parser(diagram)
        if result[0]:
            return result
    return (False, (name, ""), diagram)


@logged
def eof_parser(diagram):
    return (diagram=="", ("eof", ""), diagram)


@logged
def text_parser(name, text, diagram):
    if diagram.startswith(text):
        return (True, (name, text), diagram[len(text):])
    return (False, (name, ""), diagram)


@logged
def re_parser(name, re, diagram):
    match = re.search(diagram)
    if not match or match.start() > 0:
        return (False, (name, ""), diagram)
    return (True, (name, match.group()), diagram[match.end():])


