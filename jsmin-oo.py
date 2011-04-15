"""
jsmin.c
2011-01-22

Copyright (c) 2002 Douglas Crockford (www.crockford.com)

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

The Software shall be used for Good, not Evil.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys

EOF = ''


def isAlphanum(c):
    """
    isAlphanum -- return true if the character is a letter, digit, underscore,
    dollar sign, or non-ASCII character.
    """
    return c.isalnum() or c in ('_', '$', '\\')


class JSMinError(Exception):
    def __init__(self, msg):
        self.msg = msg


class JSMin(object):

    def __init__(self):
        self.theLookahead = EOF
        self.theA = '\n'
        self.theB = ''

    def get(self):
        """
        get -- return the next character from stdin. Watch out for lookahead. If
        the character is a control character, translate it to a space or
        linefeed.
        """
        c = self.theLookahead
        self.theLookahead = EOF
        if (c == EOF):
            c = self.input.read(1)
        if c >= ' ' or c in ('\n', EOF):
            return c
        if c == '\r':
            return '\n'
        return ' '

    def peek(self):
        """
        peek -- get the next character without getting it.
        """
        self.theLookahead = self.get()
        return self.theLookahead

    def next(self):
        """
        next -- get the next character, excluding comments. peek() is used to see
        if a '/' is followed by a '/' or '*'.
        """
        c = self.get()
        if c == '/':
            x = self.peek()
            if x == '/':
                while c > '\n':
                    c = self.get()
                return c
            if x in ('/', '*'):
                self.get()
                while True:
                    y = self.get()
                    if y == '*':
                        if self.peek() == '/':
                            self.get()
                            return ' '
                    elif y == EOF:
                        raise JSMinError('JSMIN Unterminated comment.')
        return c

    def action(self, d):
        """
        action -- do something! What you do is determined by the argument:
            1 Output A. Copy B to A. Get the next B.
            2 Copy B to A. Get the next B. (Delete A).
            3 Get the next B. (Delete B).
        action treats a string as a single character. Wow!
        action recognizes a regular expression if it is preceded by ( or , or =.
        """
        if d == 1:
            self.output.write(self.theA)
        if d <= 2:
            self.theA = self.theB
            if self.theA in ("'", '"'):
                while True:
                    self.output.write(self.theA)
                    self.theA = self.get()
                    if self.theA == self.theB:
                        break
                    elif self.theA == '\\':
                        self.output.write(self.theA)
                        self.theA = self.get()
                    if self.theA == EOF:
                        raise JSMinError('JSMIN Unterminated string literal.')
        if d <= 3:
            self.theB = self.next()
            if self.theB == '/' and self.theA in ('(', ',', '=', ':', '[', '!', '&', '|', '?', '{', '}', ';', '\n'):
                self.output.write(self.theA)
                self.output.write(self.theB)
                while True:
                    self.theA = self.get()
                    if self.theA == '[':
                        while True:
                            self.output.write(self.theA)
                            self.theA = self.get()
                            if self.theA == ']':
                                break
                            elif self.theA == '\\':
                                self.output.write(self.theA)
                                self.theA = self.get()
                            if self.theA == EOF:
                                raise JSMinError('JSMIN Unterminated set in Regular Expression literal.')
                    elif self.theA == '/':
                        break
                    elif self.theA == '\\':
                        self.output.write(self.theA)
                        self.theA = self.get()
                    if self.theA == EOF:
                        raise JSMinError('JSMIN Unterminated Regular Expression literal.')
                    self.output.write(self.theA)

    def run(self, input, output):
        """
        jsmin -- Copy the input to the output, deleting the characters which are
        insignificant to JavaScript. Comments will be removed. Tabs will be
        replaced with spaces. Carriage returns will be replaced with linefeeds.
        Most spaces and linefeeds will be removed.
        """
        self.theLookahead = EOF
        self.theA = '\n'
        self.theB = ''

        self.input = input
        self.output = output

        self.action(3)
        while self.theA != EOF:
            if self.theA == ' ':
                if isAlphanum(self.theB):
                    self.action(1)
                else:
                    self.action(2)
            elif self.theA == '\n':
                if self.theB in ('{', '[', '(', '+', '-'):
                    self.action(1)
                elif self.theB == ' ':
                    self.action(3)
                else:
                    if isAlphanum(self.theB):
                        self.action(1)
                    else:
                        self.action(2)
            else:
                if self.theB == ' ':
                    if isAlphanum(self.theA):
                        self.action(1)
                    else:
                        self.action(3)
                elif self.theB == '\n':
                    if self.theA in ('}', ']', ')', '+', '-', '"', "'"):
                        self.action(1)
                    else:
                        if isAlphanum(self.theA):
                            self.action(1)
                        else:
                            self.action(3)
                else:
                    self.action(1)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    else:
        for s in argv:
            print('# %s' % s)
    j = JSMin()
    try:
        j.run(sys.stdin, sys.stdout)
    except JSMinError, err:
        print >>sys.stderr, 'Error: %s' % err
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
