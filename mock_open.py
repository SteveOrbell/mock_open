# The MIT License (MIT)
# Copyright (c) 2013 <ionut@artarisi.eu>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from contextlib import contextmanager
from io import BytesIO as StringIO
import mock

class ExpectedStringIO(StringIO):
    def __init__(self, filename, contents):
        super(ExpectedStringIO, self).__init__(contents)
        self.filename = filename
        super(ExpectedStringIO, self).seek(0)

    def write(self, written):
        expected = super(ExpectedStringIO, self).read(len(written))
        if (expected != written):
            raise AssertionError("Unexpected contents for file %s."
                    "\nExpected:\n%s\nWritten:\n%s\n" %
                    (self.filename, expected, written))

    def close(self):
        remains = super(ExpectedStringIO, self).read()
        if (len(remains) > 0):
            raise AssertionError("Expected data not written to file %s."
                    "\nExpected:\n%s\n" %
                    (self.filename, remains))
        super(ExpectedStringIO, self).close()

class NotMocked(Exception):
    def __init__(self, filename):
        super(NotMocked, self).__init__(
                "The file %s was opened, but not mocked." % filename)
        self.filename = filename

@contextmanager
def mock_open(filename, contents=None, complain=True, mode='r'):
    """Mock the open() builtin function on a specific filename

    Let execution pass through to open() on files different than
    :filename:.

    A StringIO is returned to represent the file contents.  If mode is 'r'
    (default) then we expect the file to be opened for reading, and the
    supplied :contents: are used to prepopulate the returned StringIO.
    If the :contents: parameter is not given or if it is None, a StringIO
    instance simulating an empty file is returned.

    If mode is 'w' then we expect the file to be opened for writing, and in
    this case if :contents: is supplied we raise an AssertionError if the
    eventual file contents don't match that specified.

    If :complain: is True (default), will raise an AssertionError if
    :filename: was not opened in the enclosed block. A NotMocked
    exception will be raised if open() was called with a file that was
    not mocked by mock_open.

    """
    open_files = set()
    def mock_file(*args, **keywords):
        if args[0] == filename:
            if mode == 'r':
                f = StringIO(contents)
            else:
                f = ExpectedStringIO(filename, contents)
            f.name = filename
        else:
            mocked_file.stop()
            f = open(*args, **keywords)
            mocked_file.start()
        open_files.add(f.name)
        return f
    mocked_file = mock.patch('__builtin__.open', mock_file)
    mocked_file.start()
    try:
        yield
    except NotMocked as e:
        if e.filename != filename:
            raise
    mocked_file.stop()
    try:
        open_files.remove(filename)
    except KeyError:
        if complain:
            raise AssertionError("The file %s was not opened." % filename)
    for f_name in open_files:
        if complain:
            raise NotMocked(f_name)
