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
import io

import mock

class NotMocked(Exception):
    def __init__(self, filename):
        super(NotMocked, self).__init__(
            "The file %s was opened, but not mocked." % filename)
        self.filename = filename

@contextmanager
def mock_open(filename, contents=None, complain=True):
    """Mock the open() builtin function on a specific filename

    Let execution pass through to open() on files different than
    :filename:. Return a StringIO with :contents: if the file was
    matched. If the :contents: parameter is not given or if it is None,
    a StringIO instance simulating an empty file is returned.

    If :complain: is True (default), will raise an AssertionError if
    :filename: was not opened in the enclosed block. A NotMocked
    exception will be raised if open() was called with a file that was
    not mocked by mock_open.

    """
    open_files = set()
    def mock_file(*args):
        if args[0] == filename:
            f = io.StringIO(contents)
            f.name = filename
        else:
            mocked_file.stop()
            f = open(*args)
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
