<div style="margin-bottom: 20px; text-align: center">
<a href="https://spectrum-instrumentation.com">
    <img src="https://spectrum-instrumentation.com/img/logo-complete.png"  width=400 />
</a>
</div>

# spcm_core
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI - Version](https://img.shields.io/pypi/v/spcm_core)](https://pypi.org/project/spcm_core)
[![PyPi Downloads](https://img.shields.io/pypi/dm/spcm_core?label=downloads%20%7C%20pip&logo=PyPI)](https://pypi.org/project/spcm_core)
[![Follow](https://img.shields.io/twitter/follow/SpecInstruments.svg?style=social&style=flat&logo=twitter&label=Follow&color=blue)](https://twitter.com/SpecInstruments/)
![GitHub followers](https://img.shields.io/github/followers/SpectrumInstrumentation)

A low-level, Python API package for interfacing with Spectrum Instrumentation GmbH devices.

`spcm_core` can handle individual cards, StarHubs, groups of cards and Netboxes.

# Supported devices

See the [SUPPORTED_DEVICES.md](https://github.com/SpectrumInstrumentation/spcm_core/blob/master/src/spcm_core/SUPPORTED_DEVICES.md) file for a list of supported devices.

# Requirements
[![Static Badge](https://img.shields.io/badge/Python-3.9+-blue)](https://www.python.org/)
[![Static Badge](https://img.shields.io/badge/NumPy-1.25+-green)](https://numpy.org/)
[![Static Badge](https://img.shields.io/badge/h5py-3.10+-orange)](https://www.h5py.org/)
[![Static Badge](https://img.shields.io/badge/pint-0.23+-teal)](https://pint.readthedocs.io/en/stable/)

`spcm_core` requires the Spectrum Instrumentation [driver](https://spectrum-instrumentation.com/support/downloads.php) which is available for Windows and Linux. 
Please have a look in the manual of your product for more information about installing the driver on the different plattforms.

# Installation and dependencies
[![Pip Package](https://img.shields.io/pypi/v/spcm_core?logo=PyPI)](https://pypi.org/project/spcm_core)
[![Publish to PyPI](https://github.com/SpectrumInstrumentation/spcm_core/actions/workflows/spcm_core-publish-to-pypi.yml/badge.svg)](https://github.com/SpectrumInstrumentation/spcm_core/actions/workflows/spcm_core-publish-to-pypi.yml)

Start by installing Python 2.6 or higher. We recommend using the latest version. You can download Python from [https://www.python.org/](https://www.python.org/).

You would probably also like to install and use a virtual environment, although it's not strictly necessary. See the examples [README.md](https://github.com/SpectrumInstrumentation/spcm_core/blob/master/src/examples/README.md) for a more detailed explanation on how to use `spcm_core` in a virtual environment.

To install the latest release using `pip`:
```bash
$ pip install spcm_core
```
Note that: this will automatically install all the dependencies.

# Documentation
[![Documentation](https://img.shields.io/badge/api-reference-blue.svg)](https://spectruminstrumentation.github.io/spcm_core/spcm_core.html)
[![Build dosc](https://github.com/SpectrumInstrumentation/spcm_core/actions/workflows/spcm_core-docs-pages.yml/badge.svg)](https://github.com/SpectrumInstrumentation/spcm_core/actions/workflows/spcm_core-docs-pages.yml)
[![Publish docs](https://github.com/SpectrumInstrumentation/spcm_core/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/SpectrumInstrumentation/spcm_core/actions/workflows/pages/pages-build-deployment)

The API documentation for the latest [stable release](https://spectruminstrumentation.github.io/spcm_core/spcm_core.html) is available for reading on GitHub pages.

Please also see the hardware user manual for your specific card for more information about the available functionality.

# Using spcm_core

The `spcm_core` package is a high-level object-oriented programming library for controlling Spectrum Instrumentation devices.

## Examples
For detailed examples see the `src\examples` directory. There are several sub-directories each corresponding to a certain kind of functionality. You can find the most recent examples on [GitHub](https://github.com/SpectrumInstrumentation/spcm_core/tree/master/src/examples).
