"""ARCA Symbol Mapping parsing."""


SYMBOL_MAPPING_FILENAME = 'ARCASymbolMapping.txt'

def parse_symbol_mapping_file(symbol_mapping_file):
    """Parse symbol mapping file.

    File can be obtained at ftp://ftp.nyxdata.com/ARCASymbolMapping/ARCASymbolMapping.txt.

    Returns a tuple containging the CQS symbol, symbol index
    and price scale code which is the exponent of 10 in the
    denominator of the price.

    """
    for line in symbol_mapping_file:
        parts = line.split('|')

        symbol = parts[1] # CQS Symbol
        symbol_index = int(parts[2]) # SymbolIndex
        price_scale_code = int(parts[7]) # PriceScaleCode

        yield (symbol, symbol_index, price_scale_code)
