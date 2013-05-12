import unittest

from io import StringIO


class TestParseSymbolMappingFile(unittest.TestCase):

    sample_file1 = ("IBM|IBM|6940|P|N|A|100|4|9|||\n"
                    "GOOG|GOOG|1753|P|Q|C|100|4|13|||\n"
                    "VGZ|VGZ|9843|P|A|B|100|6|20|||\n"
                    "VNO PRG|VNO-G|9886|P|N|A|100|4|20|||\n")

    def run_it(self, symbol_mapping_file):
        from oxberrypis.parsing.symbols import parse_symbol_mapping_file
        return parse_symbol_mapping_file(symbol_mapping_file)

    def test_it(self):
        stream = StringIO(self.sample_file1.decode('utf-8'))
        generator = self.run_it(stream)
        symbol_mapping = list(generator)

        self.assertEqual(len(symbol_mapping), 4)

        self.assertEqual(
            symbol_mapping[0],
            ("IBM", 6940, 4),
        )

        self.assertEqual(
            symbol_mapping[1],
            ("GOOG", 1753, 4),
        )

        self.assertEqual(
            symbol_mapping[2],
            ("VGZ", 9843, 6),
        )

        self.assertEqual(
            symbol_mapping[3],
            ("VNO-G", 9886, 4),
        )
