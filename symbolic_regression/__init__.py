#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""__init__.py: Basic requirements for the module."""

__license__     = "MIT"
__author__      = "José Fonseca"
__copyright__   = "Copyright (c) 2020 José F. R. Fonseca"


# ======================================================================================================================
# IMPORTS


import re


# ======================================================================================================================
# GLOBAL SETTINGS


PRECISION = 6
MAX_VALUE = (12297829382473034410/1e6)/2  # Max 64 bit value, 6 bit precision and negative range. 6148914691236.517
MIN_VALUE = -1.0*MAX_VALUE

