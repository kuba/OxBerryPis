import unittest

from oxberrypis.errors import OxBerryPisException


class TestGetPktFormatString(unittest.TestCase):

    def go(self, pkt_spec):
        from oxberrypis.parsing.utils import get_pkt_format_string
        return get_pkt_format_string(pkt_spec)

    def test_empty(self):
        pkt_spec = ()
        self.assertTrue(self.go(pkt_spec), '<')

    def test_normal(self):
        pkt_spec = ((None, 'a'), (None, 'bc'))
        self.assertEqual(self.go(pkt_spec), '<abc')

    def test_non_string(self):
        pkt_spec = ((None, None),)
        with self.assertRaises(OxBerryPisException):
            self.go(pkt_spec)


class TestGetPktNamedtuple(unittest.TestCase):

    def go(self, name, pkt_spec):
        from oxberrypis.parsing.utils import get_pkt_namedtuple
        return get_pkt_namedtuple(name, pkt_spec)

    def test_normal(self):
        name = 'Test'
        pkt_spec = (('abcd', None), ('xyz', None))
        ntuple = self.go(name, pkt_spec)
        self.assertEqual(('abcd', 'xyz'), ntuple._fields)

    def test_empty_fields(self):
        name = 'asd'
        ntuple = self.go(name, ())
        self.assertEqual(len(ntuple._fields), 0)

    def test_empty_name(self):
        name = ''
        with self.assertRaises(OxBerryPisException):
            ntuple = self.go(name, ())
