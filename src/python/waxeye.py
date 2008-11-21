# Waxeye Parser Generator
# www.waxeye.org
# Copyright (C) 2008 Orlando D. A. R. Hill
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class Edge:
    def __init__(self, trans, state, voided):
        self.trans = trans
        self.state = state
        self.voided = voided


class State:
    def __init__(self, edges, match):
        self.edges = edges
        self.match = match


class FA:
    def __init__(self, type, states, mode):
        self.type = type
        self.states = states
        self.mode = mode


class ParseError:
    def __init__(self, pos, line, col, nt):
        self.pos = pos
        self.line = line
        self.col = col
        self.nt = nt

    def __str__(self):
        return "parse error: failed to match '%s' at line=%s, col=%s, pos=%s" % (self.nt, self.line, self.col, self.pos)


class AST:
    def __init__(self, type, children, pos):
        self.type = type
        self.children = children
        self.pos = pos

    def str_iter(self, ast, indent, acc):
        for i in range(0, indent[0] - 1):
            acc.append('    ')
        if indent[0] > 0:
            acc.append('->  ')
        acc.append(ast.type)
        indent[0] += 1
        for a in ast.children:
            acc.append('\n')
            if isinstance(a, AST):
                self.str_iter(a, indent, acc)
            else:
                for i in range(0, indent[0] - 1):
                    acc.append('    ')
                if indent[0] > 0:
                    acc.append('|   ')
                acc.append(a)
        indent[0] -= 1

    def __str__(self):
        acc = []
        self.str_iter(self, [0], acc)
        return ''.join(acc)


class WaxeyeParser:
    def __init__(self, start, eof_check, automata):
        self.start = start
        self.eof_check = eof_check
        self.automata = automata

    def parse(self, input):
        return WaxeyeParser.InnerParser(self.start, self.eof_check, self.automata, input).parse()

    class InnerParser:
        def __init__(self, start, eof_check, automata, input):
            self.start = start
            self.eof_check = eof_check
            self.automata = automata
            self.input = input
            self.input_len = len(input)
            self.input_pos = 0
            self.line = 1
            self.column = 0
            self.last_cr = False
            self.error_pos = 0
            self.error_line = 1
            self.error_col = 0
            self.error_nt = automata[start].type
            self.fa_stack = []
            self.cache = {}

        def parse(self):
            return self.do_eof_check(self.match_automaton(self.start))


        def match_automaton(self, index):
#            self.input_pos = self.input_len
            return self.input


        def restore_pos(self, pos, line, col, cr):
            self.input_pos = pos
            self.line = line
            self.column = col
            self.last_cr = cr


        def update_error(self):
            if self.error_pos < self.input_pos:
                self.error_pos = self.input_pos
                self.error_line = self.line
                self.error_col = self.column
                self.error_nt = self.fa_stack[len(self.fa_stack) - 1].type
            return False


        def mv(self):
            ch = self.input[self.input_pos]
            self.input_pos += 1

            if ch == '\r':
                self.line += 1
                self.column = 0
                self.last_cr = True
            else:
                if ch == '\n':
                    if not self.last_cr:
                        self.line += 1
                        self.column = 0
                else:
                    self.column += 1
                self.last_cr = False

            return ch

        def do_eof_check(self, res):
            if res:
                if self.eof_check and self.input_pos < self.input_len:
                    # Create a parse error - Not all input consumed
                    return ParseError(self.error_pos, self.error_line, self.error_col, self.error_nt)
                else:
                    return res
            else:
                # Create a parse error
                return ParseError(self.error_pos, self.error_line, self.error_col, self.error_nt)



p = WaxeyeParser(0, True, [FA('test', [], 0)])
print p.parse('1+2-3*4')

c = AST('num', ['1', '2', '3'], (0, 4))
a = AST('calc', [c, '+', c], (0, 6))
print a
