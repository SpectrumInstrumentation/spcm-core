#
# **************************************************************************
#
# netbox_discovery.py                                      (c) Spectrum GmbH
#
# **************************************************************************
#
# This example will send a LXI discovery request to the network and check the
# answers for Spectrum products.
#
# Feel free to use this source for own projects and modify it in any kind
#
# Documentation for the API as well as a detailed description of the hardware
# can be found in the manual for each device which can be found on our website:
# https://www.spectrum-instrumentation.com/en/downloads
#
# Further information can be found online in the Knowledge Base:
# https://www.spectrum-instrumentation.com/en/knowledge-base-overview
#
# **************************************************************************
#

# import spectrum driver functions
from spcm_core import *
#from spcm_tools import *
from ctypes import *
import sys
import functools
from collections import namedtuple

# custom compare function for "Card" named tuples
def card_compare(lhs, rhs):
    if lhs.sIP < rhs.sIP:
        return -1
    elif lhs.sIP == rhs.sIP:
        # use "greater than" here to get the card with the Netbox-SN to the top
        if lhs.lNetboxSN > rhs.lNetboxSN:
            return -1
        elif lhs.lNetboxSN == rhs.lNetboxSN:
            if lhs.lCardSN < rhs.lCardSN:
                return -1
    return 1

# use a named tuple to simplify access to members
Card = namedtuple ("Card", "sIP lCardSN lNetboxSN sName sVISA sNetbox")

#
# **************************************************************************
# main
# **************************************************************************
#

sys.stdout.write ("Netbox discovery running...\n\n")

# ----- first make discovery - check if there are any LXI compatible remote devices -----
dwMaxNumRemoteCards = 50
dwMaxVisaStringLen = 256
dwTimeout_ms = 5000
pszVisa = (c_char_p * dwMaxNumRemoteCards)()
for i in range(0, dwMaxNumRemoteCards, 1):
    pszVisa[i] = cast(create_string_buffer(dwMaxVisaStringLen), c_char_p)
spcm_dwDiscovery (pszVisa, uint32(dwMaxNumRemoteCards), uint32(dwMaxVisaStringLen), uint32(dwTimeout_ms))

# ----- check from which manufacturer the devices are -----
dwMaxIdnStringLen = 256
pszIdn = (c_char_p * dwMaxNumRemoteCards)()
for i in range(0, dwMaxNumRemoteCards, 1):
    pszIdn[i] = cast(create_string_buffer(dwMaxIdnStringLen), c_char_p)
spcm_dwSendIDNRequest (pszIdn, uint32(dwMaxNumRemoteCards), uint32(dwMaxIdnStringLen))

# ----- store VISA strings for all discovered cards and open them afterwards -----
listsSpectrumDevices = []
for (id, visa) in zip(pszIdn, pszVisa):
    if not id:
        break

    if id.decode('utf-8').startswith("Spectrum GmbH,"):
        listsSpectrumDevices.append (visa)

# ----- try to open each VISA string and read the Netbox SN if open was successful -----
listCards = []
for sVISA in listsSpectrumDevices:
    # open card
    hCard = spcm_hOpen (sVISA)
    if hCard is None:
        sys.stdout.write ("no card found...\n")
        exit(1)

    # VISA string has format "TCPIP[x]::<IP>::instX::INSTR"
    # extract the IP from the VISA string
    sIP = sVISA.decode("utf-8")
    sIP = sIP[sIP.find('::') + 2:]
    sIP = sIP[:sIP.find ('::')]

    lCardType = int32(0)
    spcm_dwGetParam_i32 (hCard, SPC_PCITYP, byref(lCardType))
    lCardSN = int32(0)
    spcm_dwGetParam_i32 (hCard, SPC_PCISERIALNO, byref(lCardSN))
    lNetboxType = int32(0)
    spcm_dwGetParam_i32 (hCard, SPC_NETBOX_TYPE, byref(lNetboxType))
    lNetboxSN = int32(0)
    spcm_dwGetParam_i32 (hCard, SPC_NETBOX_SERIALNO, byref(lNetboxSN))

    sNetbox = ""
    if lNetboxType.value != 0:
        sNetbox = "DN{:x}.".format((lNetboxType.value & NETBOX_SERIES_MASK) >> 24)
        sNetbox += "{:x}".format  ((lNetboxType.value & NETBOX_FAMILY_MASK) >> 16)
        sNetbox += "{:x}".format  ((lNetboxType.value & NETBOX_SPEED_MASK) >> 8)
        sNetbox += "-{:d}".format  (lNetboxType.value & NETBOX_CHANNEL_MASK)

    # get card type name from driver
    qwValueBufferLen = 20
    pValueBuffer = pvAllocMemPageAligned(qwValueBufferLen)
    spcm_dwGetParam_ptr(hCard, SPC_PCITYP, pValueBuffer, qwValueBufferLen)
    sCardName = pValueBuffer.value.decode('UTF-8')

    listCards.append(Card(sIP, lCardSN.value, lNetboxSN.value, sCardName, sVISA.decode("utf-8"), sNetbox))

    # close card
    spcm_vClose (hCard)

# sort the list with the discovered cards because the order of answers to discovery is not defined
listCards.sort (key=functools.cmp_to_key(card_compare))

# ----- print the discovered Netboxes -----
if listCards:
    sys.stdout.write ("Netboxes found:\n")

    sLastIP = ""
    for card in listCards:
        if card.sIP != sLastIP:
            if card.lNetboxSN != 0:
                sys.stdout.write(f'{card.sNetbox} at {card.sIP} with SN {card.lNetboxSN}\n')
            else:
                sys.stdout.write(f'Remote Server at {card.sIP}\n')

            sLastIP = card.sIP;

        sys.stdout.write (f'\t{card.sName} SN: {card.lCardSN} at {card.sVISA}\n')
else:
    sys.stdout.write ("No Netboxes found!\n")
