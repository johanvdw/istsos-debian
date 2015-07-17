# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------
# istSOS - Istituto Scienze della Terra
# Copyright (C) 2014 Milan Antonovic, Massimiliano Cannata
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
    Migrate from sos1 to sos2
"""

from datetime import timedelta
import csv
import sys
from os import path
import tempfile
import shutil
import traceback
import glob
import time

sys.path.insert(0, path.abspath("."))

try:
    from lib import requests
    from lib import isodate
    from scripts import istsosutils
    from scripts import istsos2csv
    from scripts import csv2istsos
except ImportError as e:
    print "\nError loading internal libs:\n >> did you run the script from the istSOS root folder?\n\n"
    raise e
    
url1 = "http://geoservice.ist.supsi.ch"
srv1 = "sosraw"
url2 = "https://geoservice.ist.supsi.ch/isos"
srv2 = "sosraw"
    
sos1 = istsosutils.Service(url1, srv1)
sos2 = istsosutils.Service(url2, srv2)

# Get all procedures that the two service have in common
#procedures = sos1.getSharedProcedureListWith(sos2)

#procedures = ["WK_MUZ_MUZ"]

def yearsago(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    try:
        return from_date.replace(year=from_date.year - years)
    except:
        # Must be 2/29!
        assert from_date.month == 2 and from_date.day == 29 # can be removed
        return from_date.replace(month=2, day=28,
                                 year=from_date.year-years)

files = glob.glob(path.join('check', "*_errors.csv"))
files.sort()

for f in files:
    
    procedure = f.replace('check/','').replace('_errors.csv','')
    
    fileObj = open(f, 'rU')
    
    lines = fileObj.readlines()
    
    print "Gathering info for %s from source" % procedure
    go1 = sos1.getSOSProcedure(procedure)
    
    if ' component' in go1['observedProperty']:
        op = go1['observedProperty'][' component'][1]
    else:
        op = go1['observedProperty']['component'][1]
    
    '''print "Gathering info for %s from destination" % procedure
    go2 = sos2.getSOSProcedure(procedure)'''
    
    for line in lines:
    
        if procedure in ['Q_BOL_PTC', 'Q_CFER_ARO', 'Q_LAV_MEN', 'Q_MAG_VIS', 'Q_MOR_GIU', 'Q_RMUL_COM', 'Q_ROV_CVM2', 'Q_SBIB_PON', 'Q_TICTO_CHIR', 'Q_TRA_ARB_FFS1', 'Q_VED_ISO', 'Q_VVED_AGN', 'P_PON', 'Q_BON_QUA', 'Q_CUC_POR', 'Q_LAV_RSV', 'Q_MAR_MAR', 'Q_MUZ_MUZ', 'Q_RMUL_MAR', 'Q_ROV_CVM3', 'Q_SCA_LUG', 'Q_TRA_ARB', 'Q_TRA_ARB_FFS2', 'Q_VED_MUZ', 'V_TEST', 'Q_AETCAN_AIR', 'Q_CAL_AIR', 'Q_GNO_GNO', 'Q_MAG_LOD', 'Q_MAR_MAR2', 'Q_RMUL_ARB', 'Q_ROV_CVM1', 'Q_SAL_MAG', 'Q_TIC_BED', 'Q_TRA_ARB_FFS', 'Q_TRA_ARB_FFS3', 'Q_VER_BGU']:
            continue
        
        begin = isodate.parse_datetime(line.replace("\"","").split(",")[0])
        end   = isodate.parse_datetime(line.replace("\"","").split(",")[0])
        
        # Creating temporary directory where CSV files will be stored
        dirpath = tempfile.mkdtemp()
        
        try:
            
            istsos2csv.execute({
                'begin': begin.isoformat(),
                'end': end.isoformat(),
                'procedure': procedure,
                'op': op,
                'url': '%s/%s' % (url1, srv1),
                'd': dirpath
            })
            
            csv2istsos.execute({
                'u':  url2,
                's': srv2,
                'wd': dirpath,
                'p': [procedure],
                'v': True
            })
        
        except Exception as e:
            print "*****************************************************************"
            print str(e)
            traceback.print_exc()
            print "*****************************************************************"
            pass
    
        shutil.rmtree(dirpath)
        print "Sleeping.. yaaaawn"
        #time.sleep(1)



