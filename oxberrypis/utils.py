"""Various utilities."""


def chunks(l, n):
    """Yield successive n evenly-sized chunks from l."""
    k = len(l) / n
    for i in xrange(0, len(l), k):
        yield l[i:i+k]
