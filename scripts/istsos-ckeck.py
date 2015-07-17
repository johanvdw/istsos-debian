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
    
    todo
    
"""

import sys
from os import path

try:
    sys.path.insert(0, path.abspath("."))
    from scripts import istsosutils
except ImportError as e:
    print "\nError loading internal libs:\n >> please run the script from the istSOS root folder.\n\n"
    raise e
    
    
sos = istsosutils.Service("http://geoservice.ist.supsi.ch/", "sosraw")
isos = istsosutils.Service("http://localhost/istsos", "sosraw")

sosprocs = sos.getSOSProceduresList()
isosprocs = isos.getSOSProceduresList()

for idx in range(len(isosprocs)):
    isosprocs[idx] = isosprocs[idx].replace('urn:ogc:def:procedure:x-istsos:1.0:','')
    
sosprocs.sort()
isosprocs.sort()

comparator = {}

for name in sosprocs:
    comparator[name] = [True,False,False,False]
    
for name in isosprocs:
    if sosprocs.index(name)>=0:
    
        sosSam = sos.getSOSProcedureSamplingtime(name)
        isosSam = isos.getSOSProcedureSamplingtime(name)
        
        comparator[name][1] = True
        
        if sosSam[0] == isosSam[0]:
            comparator[name][2] = True
            
        if sosSam[1] == isosSam[1]:
            comparator[name][3] = True
            
        for tmp in [sosSam[0],sosSam[1],isosSam[0],isosSam[1]]:
            if  tmp is None:
                comparator[name].append(None)
            else:
                comparator[name].append(tmp.isoformat())
            
        #comparator[name].extend([
        #    sosSam[0].isoformat(),sosSam[1].isoformat(),
        #    isosSam[0].isoformat(),isosSam[1].isoformat()
        #])
        
    else:
        comparator[name] = [False,True,False,False]
    
keys = comparator.keys()
keys.sort()
for c in keys:
    line = c
    for b in range(len(comparator[c])):
        line += ",%s" % comparator[c][b]
    print line
    
    
