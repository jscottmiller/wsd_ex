#!/usr/bin/python

from re import compile
from sys import argv
from functools import partial, wraps
from logging import info, basicConfig


ID_RE = compile("\w+")
ARROW_RE = compile("\-\-?>")
WS_RE = compile("[ \t]*")


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
    return one_or_many_parser(
        "statement_list",
        statement_parser,
        diagram)


@logged
def statement_parser(diagram):
    return or_parser(
        "statement",
        diagram,
        signal_parser)


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
        partial(text_parser, "newline", "\n"),
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
        "participant",
        diagram,
        leading_whitespace_parser,
        partial(not_parser, "", arrow_parser, match_empty=False))


@logged
def right_participant_parser(diagram):
    return sequence_parser(
        "participant",
        diagram,
        leading_whitespace_parser,
        partial(not_parser, "", colon_parser, match_empty=False))


@logged
def identifier_parser(diagram):
    return sequence_parser(
        "identifier",
        diagram,
        leading_whitespace_parser,
        partial(re_parser, "", ID_RE))


@logged
def arrow_parser(diagram):
   return sequence_parser(
        "arrow",
        diagram,
        leading_whitespace_parser,
        partial(re_parser, "", ARROW_RE))


@logged
def colon_parser(diagram):
    return text_parser("colon", ":", diagram)


@logged
def one_or_many_parser(name, parser, diagram):
    results = []
    while True:
        result = parser(diagram)
        if not result[0]:
            break
        diagram = result[2]
        results.append(result[1])
    return (len(results) > 0, (name, tuple(results)), diagram)


@logged
def sequence_parser(name, diagram, *parsers):
    result = (True, (name, ""), diagram)
    for parser in parsers:
        result = parser(result[2])
        if not result[0]:
            return (False, (name, ""), diagram)
    return (result[0], (name, result[1][1]), result[2])


@logged
def leading_whitespace_parser(diagram):
    return re_parser("whitespace", WS_RE, diagram)


@logged
def not_parser(name, parser, diagram, match_empty=True):
    if not diagram:
        return (match_empty, (name, diagram), "")
    for i in range(len(diagram)):
        result = parser(diagram[i:])
        if result[0]:
            return (i != 0, (name, diagram[:i]), diagram[i:])
    return (True, (name, diagram), "")


@logged
def or_parser(name, diagram, *parsers):
    for parser in parsers:
        result = parser(diagram)
        if result[0]:
            return result
    return (False, (name, ""), diagram)


@logged
def empty_parser(name, diagram):
    return (diagram=="", (name, ""), diagram)


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


