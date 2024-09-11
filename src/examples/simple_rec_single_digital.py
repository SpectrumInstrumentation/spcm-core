#
# **************************************************************************
#
# simple_rec_single_digital.py                             (c) Spectrum GmbH
#
# **************************************************************************
#
# Example for all SpcmDrv digital acquisition cards.
# Shows a simple standard mode example using only the few necessary commands
#
# Information about the different products and their drivers can be found
# online in the Knowledge Base:
# https://www.spectrum-instrumentation.com/en/platform-driver-and-series-differences
#
# Feel free to use this source for own projects and modify it in any way
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


import sys

# import spectrum driver functions
from spcm_core import *

#
# **************************************************************************
# main 
# **************************************************************************
#

szErrorTextBuffer = create_string_buffer(ERRORTEXTLEN)
dwError = uint32()


# open card
# uncomment the second line and replace the IP address to use remote
# cards like in a digitizerNETBOX
hCard = spcm_hOpen(create_string_buffer(b'/dev/spcm0'))
# hCard = spcm_hOpen(create_string_buffer(b'TCPIP::192.168.1.10::inst0::INSTR'))
if not hCard:
    sys.stdout.write("no card found...\n")
    exit(1)

# get card type name from driver
qwValueBufferLen = 20
pValueBuffer = pvAllocMemPageAligned(qwValueBufferLen)
spcm_dwGetParam_ptr(hCard, SPC_PCITYP, pValueBuffer, qwValueBufferLen)
sCardName = pValueBuffer.value.decode('UTF-8')

# read type, function and sn and check for A/D card
lCardType = int32(0)
spcm_dwGetParam_i32(hCard, SPC_PCITYP, byref(lCardType))
lSerialNumber = int32(0)
spcm_dwGetParam_i32(hCard, SPC_PCISERIALNO, byref(lSerialNumber))
lFncType = int32(0)
spcm_dwGetParam_i32(hCard, SPC_FNCTYPE, byref(lFncType))

if lFncType.value in [SPCM_TYPE_DIO, SPCM_TYPE_DI]:
    sys.stdout.write("Found: {0} sn {1:05d}\n".format(sCardName, lSerialNumber.value))
else:
    sys.stdout.write("This is an example for Digital I/O cards.\nCard: {0} sn {1:05d} not supported by example\n".format(sCardName, lSerialNumber.value))
    spcm_vClose(hCard)
    exit(1) 

#set memsize to 16 kS
lMemsize = int32(16384)

# do a simple standard setup
spcm_dwSetParam_i32(hCard, SPC_CHENABLE,       0xFFFF)                 # 16 bits enabled
spcm_dwSetParam_i32(hCard, SPC_MEMSIZE,        lMemsize)               # acquire a total of 16k samples 
spcm_dwSetParam_i32(hCard, SPC_POSTTRIGGER,    8192)                   # 8k samples after trigger event
spcm_dwSetParam_i32(hCard, SPC_CARDMODE,       SPC_REC_STD_SINGLE)     # standard single acquisition mode
spcm_dwSetParam_i32(hCard, SPC_TIMEOUT,        5000)                   # timeout 5 s
spcm_dwSetParam_i32(hCard, SPC_TRIG_ORMASK,    SPC_TMASK_SOFTWARE)     # trigger set to software
spcm_dwSetParam_i32(hCard, SPC_TRIG_ANDMASK,   0)                      # ...
spcm_dwSetParam_i32(hCard, SPC_CLOCKMODE,      SPC_CM_INTPLL)          # clock mode internal PLL

lSetChannels = int32(0)
spcm_dwGetParam_i32(hCard, SPC_CHCOUNT,     byref(lSetChannels))         # get the number of activated channels

# we try to set the samplerate to 100 kHz (M2i) or 20 MHz on internal PLL, no clock output
if ((lCardType.value & TYP_SERIESMASK) == TYP_M2ISERIES) or ((lCardType.value & TYP_SERIESMASK) == TYP_M2IEXPSERIES):
    spcm_dwSetParam_i64(hCard, SPC_SAMPLERATE, KILO(100))
else:
    spcm_dwSetParam_i64(hCard, SPC_SAMPLERATE, MEGA(20))

spcm_dwSetParam_i32(hCard, SPC_CLOCKOUT, 0)                            # no clock output

# Buffersize in bytes. Enough memory for 16384 samples with 1/8 byte each, 16 channels active
qwBufferSize = uint64(lMemsize.value * lSetChannels.value // 8)
lNotifySize = int32(0)  # driver should notify program after all data has been transferred

# define the data buffer
pvBuffer = pvAllocMemPageAligned(qwBufferSize.value)

spcm_dwDefTransfer_i64(hCard, SPCM_BUF_DATA, SPCM_DIR_CARDTOPC, lNotifySize, pvBuffer, uint64(0), qwBufferSize)

# start everything
dwError = spcm_dwSetParam_i32(hCard, SPC_M2CMD, M2CMD_CARD_START | M2CMD_CARD_ENABLETRIGGER | M2CMD_DATA_STARTDMA | M2CMD_DATA_WAITDMA)


# check for error
if dwError != 0:  # != ERR_OK
    spcm_dwGetErrorInfo_i32(hCard, None, None, szErrorTextBuffer)
    sys.stdout.write("{0}\n".format(szErrorTextBuffer.value))
    spcm_vClose(hCard)
    exit(1)

# use the recorded and transferred data
else:
    if dwError != ERR_OK:
        if dwError == ERR_TIMEOUT:
            sys.stdout.write("... Timeout\n")
        else:
            sys.stdout.write("... Error: {0:d}\n".format(dwError))

    else:
        # this is the point to do anything with the data
        # e.g. print first 10 samples to screen

        # cast to pointer to 16bit unsigned int
        # keep in mind that one 16bit word may contain more than one sample or just a part of it, depending on SPC_CHENABLE.
        # See hardware manual for details.
        pData = cast(pvBuffer, uptr16)
        for sampleIdx in range(0, 10, 1):
            # print each bit
            for bitIdx in range(0, 16, 1):
                if (pData[sampleIdx] & (0x1 << bitIdx)) != 0:
                    sys.stdout.write('1')
                else:
                    sys.stdout.write('0')

                # for better readability a space between each 16 bits
                if bitIdx > 0 and bitIdx % 16 == 0:
                    sys.stdout.write(' ')
            sys.stdout.write('\n')


sys.stdout.write("Finished...\n")


# clean up
spcm_vClose(hCard)

