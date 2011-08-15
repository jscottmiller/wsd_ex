#!/usr/bin/python

from wsd_ex_parser import wsd_ex_parser
from sys import stdin


def wsd_gen(ast):
    print ast
    return statement_list_gen(ast)


def statement_list_gen(ast):
    return '\n'.join(map(statement_gen, ast[1]))


def statement_gen(ast):
    if ast[0] == "signal":
        return signal_gen(ast)


def signal_gen(ast):
    return "%s:%s" % (
        participants_gen(ast[1][0]),
        signal_body_gen(ast[1][2]))


def participants_gen(ast):
    return "%s%s%s" % (
        participant_gen(ast[1][0]),
        arrow_gen(ast[1][1]),
        participant_gen(ast[1][2]))


def participant_gen(ast):
    return ast[1]


def arrow_gen(ast):
    return ast[1]


def signal_body_gen(ast):
    return '\\n'.join(map(signal_body_line_gen, ast[1]))


def signal_body_line_gen(ast):
    return ast[1]


if __name__ == '__main__':
    status, ast, remainder = wsd_ex_parser(stdin.read())
    if not status:
        print "Failed to parse input."
    else:
        print wsd_gen(ast)

