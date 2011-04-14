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

#EOF = chr(26)
EOF = ''

theLookahead = EOF
theA = '\n'
theB = ''


class JSMinError(Exception):
    def __init__(self, msg):
        self.msg = msg


def isAlphanum(c):
    """
    isAlphanum -- return true if the character is a letter, digit, underscore,
    dollar sign, or non-ASCII character.
    """
    return c.isalnum() or c in ('_', '$', '\\')

def get():
    """
    get -- return the next character from stdin. Watch out for lookahead. If
    the character is a control character, translate it to a space or
    linefeed.
    """
    global theLookahead
    c = theLookahead
    theLookahead = EOF
    if (c == EOF):
        c = sys.stdin.read(1)
    if c != EOF:
        ordc = ord(c)
    if c in ('\n', EOF) or ordc >= 0x20:
        return c
    if ordc == '\r':
        return '\n'
    return ' '

def peek():
    """
    peek -- get the next character without getting it.
    """
    global theLookahead
    theLookahead = get()
    return theLookahead

def next():
    """
    next -- get the next character, excluding comments. peek() is used to see
    if a '/' is followed by a '/' or '*'.
    """
    c = get()
    if c == '/':
        x = peek()
        if x == '/':
            while True:
                c = get()
                if c <= '\n':
                    return c
        if x in ('/', '*'):
            get()
            while True:
                y = get()
                if y == '*':
                    if peek() == '/':
                        get()
                        return ' '
                elif y == EOF:
                    raise JSMinError('JSMIN Unterminated comment.')
    return c

def action(d):
    """
    action -- do something! What you do is determined by the argument:
        1 Output A. Copy B to A. Get the next B.
        2 Copy B to A. Get the next B. (Delete A).
        3 Get the next B. (Delete B).
    action treats a string as a single character. Wow!
    action recognizes a regular expression if it is preceded by ( or , or =.
    """
    global theA
    global theB
    if d == 1:
        sys.stdout.write(theA)
    if d <= 2:
        theA = theB
        if theA in ("'", '"'):
            while True:
                sys.stdout.write(theA)
                theA = get()
                if theA == theB:
                    break
                if theA == '\\':
                    sys.stdout.write(theA)
                    theA = get()
                if theA == EOF:
                    raise JSMinError('JSMIN Unterminated string literal.')
    if d <= 3:
        theB = next()
        if theB == '/' and theA in ('(', ',', '=', ':', '[', '!', '&', '|', '?', '{', '}', ';', '\n'):
            sys.stdout.write(theA)
            sys.stdout.write(theB)
            while True:
                theA = get()
                if theA == '[':
                    while True:
                        sys.stdout.write(theA)
                        theA = get()
                        if theA == ']':
                            break
                        if theA == '\\':
                            sys.stdout.write(theA)
                            theA = get()
                        if theA == EOF:
                            raise JSMinError('JSMIN Unterminated set in Regular Expression literal.')
                elif theA == '/':
                    break
                elif theA == '\\':
                    sys.stdout.write(theA)
                    theA = get()
                if theA == EOF:
                    raise JSMinError('JSMIN Unterminated Regular Expression literal.')
                sys.stdout.write(theA)

def jsmin():
    """
    jsmin -- Copy the input to the output, deleting the characters which are
    insignificant to JavaScript. Comments will be removed. Tabs will be
    replaced with spaces. Carriage returns will be replaced with linefeeds.
    Most spaces and linefeeds will be removed.
    """
    #global theA
    #global theB
    action(3)
    while (theA != EOF):
        if theA == ' ':
            if isAlphanum(theB):
                action(1)
            else:
                action(2)
        elif theA == '\n':
            if theB in ('{', '[', '(', '+', '-'):
                action(1)
            elif theB == ' ':
                action(3)
            else:
                if isAlphanum(theB):
                    action(1)
                else:
                    action(2)
        else:
            if theB == ' ':
                if isAlphanum(theA):
                    action(1)
                else:
                    action(3)
            elif theB == '\n':
                if theA in ('}', ']', ')', '+', '-', '"', "'"):
                    action(1)
                else:
                    if isAlphanum(theA):
                        action(1)
                    else:
                        action(3)
            else:
                action(1)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    else:
        for s in argv:
            print('# %s' % s)
    try:
        jsmin()
    except JSMinError, err:
        print >>sys.stderr, 'Error: %s' % err
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
