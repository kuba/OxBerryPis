import unittest

from oxberrypis.errors import OxBerryPisException


class TestFieldsGenerator(unittest.TestCase):

    def create_generator(self, fields, size_mapping):
        from oxberrypis.parsing.fields import FieldsGenerator
        return FieldsGenerator(fields, size_mapping)

    def test_normal(self):
        fields = { 'A': 1, 'B': 2 }
        size_mapping = { 1: 'x', 2: 'Y' }
        fields_generator = self.create_generator(fields, size_mapping)

        self.assertEqual(fields_generator.A, ('A', 'x'))
        self.assertEqual(fields_generator.B, ('B', 'Y'))

    def test_field_not_found(self):
        fields_generator = self.create_generator({}, {})
        with self.assertRaises(AttributeError):
            fields_generator.A

    def test_missing_size_mapping(self):
        fields = { 'A': 1 }
        size_mapping = { 2: 'X' }
        fields_generator = self.create_generator(fields, size_mapping)
        with self.assertRaises(OxBerryPisException):
            fields_generator.A
