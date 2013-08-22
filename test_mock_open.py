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

import unittest

from mock_open import mock_open

class MockTest(unittest.TestCase):
    def test_open_same_mocked_file_twice(self):
        with mock_open("test_file", "foo"):
            with open("test_file") as a:
                with open("test_file") as b:
                    self.assertEqual(a.read(), b.read())
                    a.seek(0)
                    self.assertEqual("foo", a.read())

    def test_file_open_not_mocked(self):
        with self.assertRaises(AssertionError):
            with mock_open("file"):
                pass

    def test_file_write(self):
        with mock_open("test_file", "bob", mode='w'):
            with open("test_file", mode='w') as f:
                f.write("bob")

    def test_file_bad_write(self):
        with mock_open("test_file", "bob", mode='w'):
            with open("test_file", mode='w') as f:
                with self.assertRaises(AssertionError):
                    f.write("cheese")

    def test_file_partial_write(self):
        with mock_open("test_file", "itchyandscratchy", mode = 'w'):
            with self.assertRaises(AssertionError):
                with open("test_file", mode='w') as f:
                    f.write("itchy")
                    f.write("and")
