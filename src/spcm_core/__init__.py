"""
.. include:: ./README.md

.. include:: ./SUPPORTED_DEVICES.md
"""

# Import all registery entries and spectrum card errors into the module's name space
from .constants import *
from .pyspcm import *
from .spcm_tools import *

from . import constants
from . import regs
from . import spcerr as errors

# Versioning support using versioneer
from . import _version
__version__ = _version.get_versions()['version']

# Writing spcm_core package version to log file
try:
    #from .pyspcm import spcm_dwGetParam_i64, spcm_dwSetParam_ptr, create_string_buffer, byref, int64
    driver_version = int64(0)
    spcm_dwGetParam_i64(None, SPC_GETDRVVERSION, byref(driver_version))
    version_hex = driver_version.value
    major = (version_hex & 0xFF000000) >> 24
    minor = (version_hex & 0x00FF0000) >> 16
    build = version_hex & 0x0000FFFF
    # Available starting from build 21797
    if build < 21797:
        version_str = "v{}.{}.{}".format(major, minor, build)
        raise OSError(f"Driver version build {version_str} does not support writing spcm version to log")
    from importlib.metadata import version
    version_tag = version('spcm_core')
    version_str = bytes("Python package spcm_core v{}".format(version_tag), "utf-8")
    version_ptr = create_string_buffer(version_str)
    dwErr = spcm_dwSetParam_ptr(None, SPC_WRITE_TO_LOG, version_ptr, len(version_str))
except OSError as e:
    print(e)
