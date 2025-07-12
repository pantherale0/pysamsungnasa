"""NASA PNP."""

import os

from pysamsungnasa.helpers import bin2hex, hex2bin, getnonce, resetnonce


def nasa_pnp_phase0_request_network_address():
    source = "500000"
    dest = "B0FFFF"  # EHS
    # notifying of the value
    msgnum = hex(0x10000 + 0x210)[-4:]
    val = hex(0x10000)[-4:]
    # write
    return hex2bin(source + dest + "C011" + hex(0x100 + getnonce())[3:] + "01" + msgnum + val)


def nasa_is_pnp_phase0_network_address(source, dest, dataSets):
    global nasa_pnp_unique_network_address
    for ds in dataSets:
        if ds[0] == 0x0210:
            nasa_pnp_unique_network_address = ds[2]
            return True
    return False


# captured MWR-WG00N 50ffffb0ffff c01400 05 200401 04180050c1d4 0217a2f4 041700510000 041900500000
nasa_pnp_unique_address = "50c1d4"
nasa_pnp_unique_network_address = "a2f4"


def nasa_pnp_phase1_request_address(requested_address):
    global nasa_pnp_unique_address
    global nasa_pnp_unique_network_address

    nasa_pnp_unique_address = "50" + bin2hex(os.urandom(2))

    source = "50FFFF"
    dest = "B0FFFF"  # broadcast
    resetnonce()
    return hex2bin(
        source
        + dest
        + "C01400"
        + "05"
        # PNP phase 1
        + "200401"
        # temporary reply to address
        + "041800"
        + nasa_pnp_unique_address
        # network address
        + "0217"
        + nasa_pnp_unique_network_address
        # requested address
        + "041700"
        + requested_address
        # base address??
        + "041900500000"
    )


# captured AE050CXYBEK 20000050c1d4c012490620040304180050c1d40217a2f4041700510000041900500000201201
nonce_pnp_phase3 = None


def nasa_is_pnp_phase3_addressing(source, dest, nonce, dataSets):
    global nasa_pnp_unique_address
    global nasa_pnp_unique_network_address
    pnpphase3present = False
    expectedtempreplyaddr = False
    expectednetaddr = False
    attribaddr = None
    expectedstep = False
    for ds in dataSets:
        if ds[0] == 0x2004 and ds[4][0] == 3:
            pnpphase3present = True
        if ds[0] == 0x418 and ds[2] == "00" + nasa_pnp_unique_address:
            expectedtempreplyaddr = True
        if ds[0] == 0x217 and ds[2] == nasa_pnp_unique_network_address:
            expectednetaddr = True
        if ds[0] == 0x417:
            attribaddr = ds[2]
        # ignored if ds[0] == 0x419:
        # ??
        if ds[0] == 0x2012 and ds[2] == "01":
            expectedstep = True

    if bin2hex(source) == "200000" and pnpphase3present and expectedtempreplyaddr and expectednetaddr and expectedstep:
        global attributed_address
        attributed_address = attribaddr
        global nonce_pnp_phase3
        nonce_pnp_phase3 = hex(0x100 + nonce)[-2:]
        return True
    return False


# captured MWR-WG00N 510000200000c015490620040404180050c1d40217a2f4041700510000041900500000201204
def nasa_pnp_phase4_ack(source=None):
    if not source:
        global attributed_address
        source = attributed_address
    global nasa_pnp_unique_address
    global nasa_pnp_unique_network_address
    dest = "200000"  # EHS
    global nonce_pnp_phase3
    return hex2bin(
        source
        + dest
        + "C015"
        + nonce_pnp_phase3
        + "06"
        # PNP phase 4
        + "200404"
        # temporary reply to address
        + "041800"
        + nasa_pnp_unique_address
        # network address
        + "0217"
        + nasa_pnp_unique_network_address
        # requested address
        + "041700"
        + source
        # base address??
        + "041900500000"
        # ??
        + "201204"
    )


# captured AE050CXYBEK 200000b0ffffc0144b01200400
def nasa_is_pnp_end(source, dest, dataSets):
    for ds in dataSets:
        if bin2hex(source) == "200000" and ds[0] == 0x2004 and ds[4][0] == 0:
            return True
    return False


# captured MWR-WG00N 510000b0ff50c01100014242ffff
def nasa_poke(source=None):
    if not source:
        global attributed_address
        source = attributed_address
    dest = "200000"  # EHS
    return hex2bin(
        source
        + dest
        + "C011"
        + hex(0x100 + getnonce())[3:]
        + "01"
        # PNP poke to detect other nodes
        + "4242FFFF"
    )
