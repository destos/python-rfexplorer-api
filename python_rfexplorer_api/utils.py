from math import log10

def mw_to_dbm(mW):
    """This function converts a power given in mW to a power given in dBm."""
    return 10.0 * log10(mW)

def dbm_to_mw(dBm):
    """This function converts a power given in dBm to a power given in mW."""
    return 10 ** (dBm / 10.0)
