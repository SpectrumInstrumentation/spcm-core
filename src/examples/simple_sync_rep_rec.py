#
# **************************************************************************
#
# simple_sync_rep_rec.py                                  (c) Spectrum GmbH
#
# **************************************************************************
#
# Information about the different products and their drivers can be found
# online in the Knowledge Base:
# https://www.spectrum-instrumentation.com/en/platform-driver-and-series-differences
#
# Shows a simple example using synchronized replay and record
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

from spcm_core import *
import sys
import math
import msvcrt

# import matplotlib.pyplot as plt


def lKbhit():
    return ord(msvcrt.getch()) if msvcrt.kbhit() else 0


#
# **************************************************************************
# Setup AD card
# **************************************************************************
#

def vSetupCardAD(hCard):
    # set up the mode
    spcm_dwSetParam_i32(hCard, SPC_CARDMODE, SPC_REC_FIFO_SINGLE)
    spcm_dwSetParam_i32(hCard, SPC_PRETRIGGER, 8)
    spcm_dwSetParam_i32(hCard, SPC_CHENABLE, CHANNEL0)

    # setup trigger
    spcm_dwSetParam_i32(hCard, SPC_TRIG_ORMASK, SPC_TMASK_SOFTWARE)
    spcm_dwSetParam_i32(hCard, SPC_TRIG_ANDMASK, 0)
    spcm_dwSetParam_i32(hCard, SPC_TRIG_CH_ORMASK0, 0)
    spcm_dwSetParam_i32(hCard, SPC_TRIG_CH_ORMASK1, 0)
    spcm_dwSetParam_i32(hCard, SPC_TRIG_CH_ANDMASK0, 0)
    spcm_dwSetParam_i32(hCard, SPC_TRIG_CH_ANDMASK1, 0)
    spcm_dwSetParam_i32(hCard, SPC_TRIGGEROUT, 0)

    # set up clock
    spcm_dwSetParam_i32(hCard, SPC_CLOCKMODE, SPC_CM_INTPLL)
    spcm_dwSetParam_i64(hCard, SPC_SAMPLERATE, MEGA(5))

    spcm_dwSetParam_i32(hCard, SPC_TIMEOUT, 5000)

    # set up the channels
    lNumChannels = int32(0)
    spcm_dwGetParam_i32(hCard, SPC_CHCOUNT, byref(lNumChannels))
    for lChannel in range(0, lNumChannels.value, 1):
        spcm_dwSetParam_i32(hCard, SPC_AMP0 + lChannel * (SPC_AMP1 - SPC_AMP0), 1000)
        spcm_dwSetParam_i32(hCard, SPC_DIFF0 + lChannel * (SPC_DIFF1 - SPC_DIFF0), 0)
        spcm_dwSetParam_i32(hCard, SPC_50OHM0 + lChannel * (SPC_50OHM1 - SPC_50OHM0), 0)


#
# **************************************************************************
# Setup DA card
# **************************************************************************
#

def vSetupCardDA(hCard):
    llMemSamples = int64(KILO_B(64))

    spcm_dwSetParam_i32(hCard, SPC_CARDMODE, SPC_REP_STD_CONTINUOUS)
    spcm_dwSetParam_i64(hCard, SPC_CHENABLE, CHANNEL0)
    spcm_dwSetParam_i64(hCard, SPC_MEMSIZE, llMemSamples)
    spcm_dwSetParam_i64(hCard, SPC_LOOPS, 0)

    spcm_dwSetParam_i32(hCard, SPC_CLOCKMODE, SPC_CM_INTPLL)
    spcm_dwSetParam_i64(hCard, SPC_SAMPLERATE, MEGA(50))
    spcm_dwSetParam_i32(hCard, SPC_CLOCKOUT, 0)

    spcm_dwSetParam_i32(hCard, SPC_TRIG_ORMASK, SPC_TMASK_SOFTWARE)
    spcm_dwSetParam_i32(hCard, SPC_TRIG_ANDMASK, 0)
    spcm_dwSetParam_i32(hCard, SPC_TRIG_CH_ORMASK0, 0)
    spcm_dwSetParam_i32(hCard, SPC_TRIG_CH_ORMASK1, 0)
    spcm_dwSetParam_i32(hCard, SPC_TRIG_CH_ANDMASK0, 0)
    spcm_dwSetParam_i32(hCard, SPC_TRIG_CH_ANDMASK1, 0)
    spcm_dwSetParam_i32(hCard, SPC_TRIGGEROUT, 0)

    lSetChannels = int32(0)
    spcm_dwGetParam_i32(hCard, SPC_CHCOUNT, byref(lSetChannels))
    lBytesPerSample = int32(0)
    spcm_dwGetParam_i32(hCard, SPC_MIINST_BYTESPERSAMPLE, byref(lBytesPerSample))

    for lChannel in range(0, lSetChannels.value, 1):
        spcm_dwSetParam_i32(hCard, SPC_ENABLEOUT0 + lChannel * (SPC_ENABLEOUT1 - SPC_ENABLEOUT0), 1)
        spcm_dwSetParam_i32(hCard, SPC_AMP0 + lChannel * (SPC_AMP1 - SPC_AMP0), 1000)
        spcm_dwSetParam_i32(hCard, SPC_CH0_STOPLEVEL + lChannel * (SPC_CH1_STOPLEVEL - SPC_CH0_STOPLEVEL), SPCM_STOPLVL_HOLDLAST)

    # allocate buffer for data transfer
    qwBufferSize = uint64(llMemSamples.value * lBytesPerSample.value * lSetChannels.value)
    pvBuffer = c_void_p()
    pvBuffer = pvAllocMemPageAligned(qwBufferSize.value)

    # calculate sine waveform
    pnBuffer = cast(pvBuffer, ptr16)
    for i in range(0, llMemSamples.value, 1):
        pnBuffer[i] = int16(int(5000 * math.sin(2.0 * math.pi * i / llMemSamples.value)))

    # we define the buffer for transfer and start the DMA transfer
    sys.stdout.write("Starting the DMA transfer and waiting until data is in board memory\n")
    spcm_dwDefTransfer_i64(hCard, SPCM_BUF_DATA, SPCM_DIR_PCTOCARD, int32(0), pvBuffer, uint64(0), qwBufferSize)
    spcm_dwSetParam_i32(hCard, SPC_M2CMD, M2CMD_DATA_STARTDMA | M2CMD_DATA_WAITDMA)
    sys.stdout.write("... data has been transferred to board memory\n")


#
# **************************************************************************
# main
# **************************************************************************
#

lMBytesToAcquire = int32(100)

# settings for the FIFO mode buffer handling
llBufferSizeInBytes = uint64(MEGA_B(8))
lNotifySize = int32(KILO_B(16))

szErrorTextBuffer = create_string_buffer(ERRORTEXTLEN)

# open cards
hCardAD = None
hCardDA = None

lSHCarrierIdx = 0
for i in range(2):
    if i == 0:
        hCard = spcm_hOpen(create_string_buffer(b'/dev/spcm0'))
    else:
        hCard = spcm_hOpen(create_string_buffer(b'/dev/spcm1'))
    if not hCard:
        sys.stdout.write("card not found...\n")
        exit(1)

    # get card type name from driver
    qwValueBufferLen = 20
    pValueBuffer = pvAllocMemPageAligned(qwValueBufferLen)
    spcm_dwGetParam_ptr(hCard, SPC_PCITYP, pValueBuffer, qwValueBufferLen)
    sCardName = pValueBuffer.value.decode('UTF-8')

    # read type, function and sn and check for D/A card
    lCardType = int32(0)
    spcm_dwGetParam_i32(hCard, SPC_PCITYP, byref(lCardType))
    lSerialNumber = int32(0)
    spcm_dwGetParam_i32(hCard, SPC_PCISERIALNO, byref(lSerialNumber))
    lFncType = int32(0)
    spcm_dwGetParam_i32(hCard, SPC_FNCTYPE, byref(lFncType))

    if lFncType.value == SPCM_TYPE_AO:
        hCardDA = hCard
        sys.stdout.write("DA card found: {0} sn {1:05d}".format(sCardName, lSerialNumber.value))
    else:
        hCardAD = hCard
        sys.stdout.write("AD card found: {0} sn {1:05d}".format(sCardName, lSerialNumber.value))

    # check if this card carries a starhub
    lFeatures = int32(0)
    spcm_dwGetParam_i32(hCard, SPC_PCIFEATURES, byref(lFeatures))
    if lFeatures.value & (SPCM_FEAT_STARHUB5 | SPCM_FEAT_STARHUB16):
        lSHCarrierIdx = i
        sys.stdout.write(" with Starhub module")
    sys.stdout.write("\n")

if hCardAD == None or hCardDA == None:
    sys.stdout.write("Invalid cards ...\n")
    exit(1)

sys.stdout.write("\n")

# open handle for star-hub
hSync = spcm_hOpen(create_string_buffer(b'sync0'))
if not hSync:
    sys.stdout.write("Could not open star-hub...\n")
    spcm_vClose(hCardAD)
    spcm_vClose(hCardDA)
    exit(1)

# setup DA card
vSetupCardDA(hCardDA)

# setup AD card
vSetupCardAD(hCard)

# setup star-hub
spcm_dwSetParam_i32(hSync, SPC_SYNC_ENABLEMASK, 3)
spcm_dwSetParam_i32(hSync, SPC_SYNC_CLKMASK, 1 << lSHCarrierIdx)

# buffer settings for Fifo transfer
pvData = c_void_p()
pvData = pvAllocMemPageAligned(llBufferSizeInBytes.value)

# set fifo buffer for AD card
qwError = spcm_dwDefTransfer_i64(hCard, SPCM_BUF_DATA, SPCM_DIR_CARDTOPC, lNotifySize.value, pvData, 0, llBufferSizeInBytes.value)
if qwError != 0:  # != ERR_OK
    spcm_dwGetErrorInfo_i32(hCard, None, None, szErrorTextBuffer)
    sys.stdout.write("{0}\n".format(szErrorTextBuffer.value))
    sys.stdout.write("... Error: {0:d}\n".format(qwError))
    exit(1)

# start DMA for AD card
dwError = spcm_dwSetParam_i32(hCardAD, SPC_M2CMD, M2CMD_DATA_STARTDMA)
if dwError != 0:  # != ERR_OK
    spcm_dwGetErrorInfo_i32(hSync, None, None, szErrorTextBuffer)
    sys.stdout.write("{0}\n".format(szErrorTextBuffer.value))
    exit(1)

# start all cards using the star-hub handle
dwError = spcm_dwSetParam_i32(hSync, SPC_M2CMD, M2CMD_CARD_START | M2CMD_CARD_ENABLETRIGGER)
if dwError != 0:  # != ERR_OK
    spcm_dwGetErrorInfo_i32(hSync, None, None, szErrorTextBuffer)
    sys.stdout.write("{0}\n".format(szErrorTextBuffer.value))
    exit(1)

sys.stdout.write("\nAcquisition stops after {} MBytes are transferred\n".format(lMBytesToAcquire.value))

sys.stdout.write("\nPress ESC to stop\n\n")

lStatus = int32()
lAvailUser = int32()
lPCPos = int32()
qwTotalMem = uint64(0)
plotData = []

while True:

    if qwTotalMem.value >= MEGA_B(lMBytesToAcquire.value):
        break

    lKey = lKbhit()
    if lKey == 27:  # ESC
        spcm_dwSetParam_i32(hSync, SPC_M2CMD, M2CMD_CARD_STOP)
        break
    else:
        # get status and amount of available data
        spcm_dwGetParam_i32(hCardAD, SPC_M2STATUS, byref(lStatus))
        spcm_dwGetParam_i32(hCardAD, SPC_DATA_AVAIL_USER_LEN, byref(lAvailUser))
        spcm_dwGetParam_i32(hCardAD, SPC_DATA_AVAIL_USER_POS, byref(lPCPos))

        if lAvailUser.value >= lNotifySize.value:
            qwTotalMem.value += lNotifySize.value

            sys.stdout.write("\rTotal:{} MB".format(c_double(qwTotalMem.value).value / MEGA_B(1)))

            # save first block to plot later
            if lPCPos.value == 0 and len(plotData) == 0:
                pnData = cast(pvData, ptr16)
                for i in range(lPCPos.value, lPCPos.value + lNotifySize.value):
                    plotData.append(pnData[i])

            spcm_dwSetParam_i32(hCardAD, SPC_DATA_AVAIL_CARD_LEN, lNotifySize)

        # wait for next block
        dwError = spcm_dwSetParam_i32(hCardAD, SPC_M2CMD, M2CMD_DATA_WAITDMA)

spcm_dwSetParam_i32(hSync, SPC_M2CMD, M2CMD_CARD_STOP)

# close sync handle
spcm_vClose(hSync)

# close cards
spcm_vClose(hCardAD)
spcm_vClose(hCardDA)

# plot first data block
# plt.plot(plotData)
# plt.show()
