# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------
# istSOS - Istituto Scienze della Terra
# Copyright (C) 2013 Massimiliano Cannata, Milan Antonovic
#---------------------------------------------------------------------------
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#---------------------------------------------------------------------------
"""
description:
    
    Base class to be extended by specialized implementation to 
    handle different raw source files.
    
"""

import sys
import os
from os import path
import glob
from datetime import datetime
from datetime import timedelta
import decimal
from inspect import stack
import pprint
import tempfile
pp = pprint.PrettyPrinter(indent=4)

try:
    sys.path.insert(0, path.abspath("."))
    from scripts import raw2csv
    from lib.pytz import timezone
    import lib.requests as requests
    import lib.isodate as iso
except ImportError as e:
    print "\nError loading internal libs:\n >> please run the script from the istSOS root folder.\n\n"
    raise e
    
    
class NetConverter(raw2csv.Converter):

    def __init__(self, name, url, service, url, folderOut=None, 
                 exceptionBehaviour={}, 
                 user=None, password=None, debug=False, 
                 csvlength=5000, archivefolder = None):
        
        raw2csv.Converter.__init__(self, name, url, service, url, None, folderOut, 
                 False, exceptionBehaviour={}, 
                 user, password, debug, 
                 csvlength,  None, archivefolder = None)
        
    
    def execute(self):
        
        self.observations = []
        self.observationsCheck = {}
        self.endPosition = None
        















