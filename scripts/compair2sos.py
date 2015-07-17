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

from datetime import timedelta
import csv
import sys
from os import path

sys.path.insert(0, path.abspath("."))

try:
    from lib import requests
    from lib import isodate
    from scripts import istsosutils
except ImportError as e:
    print "\nError loading internal libs:\n >> did you run the script from the istSOS root folder?\n\n"
    raise e
    
auth = ('ist','wms21supsi')
servicename = "sos"

sos1 = istsosutils.Service(
    "http://geoservice.ist.supsi.ch", servicename, basicAuth=auth)
sos2 = istsosutils.Service(
    "https://geoservice.ist.supsi.ch/isos", servicename, basicAuth=auth)

td = timedelta(days=60)

#procedures = ["WT_TRA_ARB_FFS1"] 
procedures = sos1.getSharedProcedureListWith(sos2)

sampling = []

samplingFile = open('sampling.csv', 'w')
out = csv.writer(samplingFile, quoting=csv.QUOTE_ALL)

for procedure in procedures:
    
    if procedure in ["P_PON", "Q_AETCAN_AIR", "Q_BOL_PTC", "Q_BON_QUA", "Q_CAL_AIR", "Q_CERPRE_FAI", "Q_CERSCA_FAI", "Q_CFER_ARO", "Q_CUC_POR", "Q_GNO_GNO", "Q_LAV_MEN", "Q_LAV_RSV", "Q_MAG_LOD", "Q_MAG_VIS", "Q_MAR_MAR", "Q_MAR_MAR2", "Q_MOR_GIU", "Q_MUZ_MUZ", "Q_RMUL_ARB", "Q_RMUL_COM", "Q_RMUL_MAR", "Q_ROV_CVM1", "Q_ROV_CVM2", "Q_ROV_CVM3", "Q_SAL_MAG", "Q_SBIB_PON", "Q_SCA_LUG", "Q_TIC_BED", "Q_TICTO_CHIR", "Q_TRA_ARB", "Q_TRA_ARB_FFS", "Q_TRA_ARB_FFS1", "Q_TRA_ARB_FFS2", "Q_TRA_ARB_FFS3", "Q_TRA_ARB_FFS3_old", "Q_TRA_ARB_FFS_old", "Q_VED_ISO", "Q_VED_MUZ", "Q_VER_BGU", "Q_VVED_AGN"]:
        continue
    
    '''if procedure <= 'T_TRE':
        continue'''
        
    row = []
    
    samp1 = sos1.getSOSProcedureSamplingtime(procedure)
    samp2 = sos2.getSOSProcedureSamplingtime(procedure)
    
    row = [procedure]
    
    row.extend([samp1[0].isoformat(),samp2[0].isoformat(),samp1[1].isoformat(),samp2[1].isoformat()])
    
    out.writerow(row)
    
    sampling.append(row)
    
    samplingFile.flush()

    #minEnd = min(samp1[1],samp2[1])
    minEnd = max(samp1[1],samp2[1])
    #minEnd = isodate.parse_datetime('2015-04-02T00:00:00+00:00')
    
    
    
    print "\n[%s -- %s]\n" % (minEnd-td, minEnd)

    '''
    observations1 = sos1.getSOSProcedureObservations(
        procedure, (minEnd-timedelta(days=120)).isoformat(), (minEnd-timedelta(days=60)).isoformat(), True)
    observations2 = sos2.getSOSProcedureObservations(
        procedure, (minEnd-timedelta(days=120)).isoformat(), (minEnd-timedelta(days=60)).isoformat(), True)'''
        
    observations1 = sos1.getSOSProcedureObservations(
        procedure, (minEnd-td).isoformat(), minEnd.isoformat(), True)
    observations2 = sos2.getSOSProcedureObservations(
        procedure, (minEnd-td).isoformat(), minEnd.isoformat(), True)
        
    '''maxBegin = max(samp1[0],samp2[0])
    observations1 = sos1.getSOSProcedureObservations(
        procedure, maxBegin.isoformat(), (maxBegin+timedelta(days=120)).isoformat())
    observations2 = sos2.getSOSProcedureObservations(
        procedure, maxBegin.isoformat(), (maxBegin+timedelta(days=120)).isoformat())
    
    print " >>> Compairing: %s / %s " % (maxBegin.isoformat(), (maxBegin+timedelta(days=120)).isoformat())'''
    
    if len(observations1)==len(observations2):
        stop = len(observations1)
    elif len(observations1)>len(observations2):
        stop = len(observations1)
    elif len(observations1)<len(observations2):
        stop = len(observations2)
        
    print " > sos1 has %s observations" % len(observations1)
    print " > sos2 has %s observations\n" % len(observations2)
    
    merged = [] # ListTable()
    mergedErrors = []

    stop1 = len(observations1)
    stop2 = len(observations2)
    cnt1 = cnt2 = 0
    stop = max(stop1,stop2)
    
    errors = False
    
    #print "**********************************************"
    #print "Stop: %s, %s" % (stop1,stop2)
    #print "**********************************************"
    
    for i in range(0,stop):

        row = []
        iso1 = None
        iso2 = None
        
        #toprint = i, ": "
        if (cnt1)<stop1:
            iso1 = isodate.parse_datetime(observations1[cnt1][0])
            #toprint = toprint , cnt1, observations1[cnt1], ' '
            
        if (cnt2)<stop2:
            iso2 = isodate.parse_datetime(observations2[cnt2][0])
            #toprint = toprint , cnt2, observations2[cnt2]
        
        #print toprint
        
        if iso1 == None:
            row = [None,None,None,iso2.isoformat(),observations2[cnt2][1],observations2[cnt2][2]]
            #errors = True
            #mergedErrors.append([None,None,None,iso2.isoformat(),observations2[cnt2][1],observations2[cnt2][2]])
            cnt1 += 1     
            if cnt2<stop2 and cnt1>stop1:
                cnt2 += 1
            
        elif iso2 == None:
            row = [iso1.isoformat(),observations1[cnt1][1],observations1[cnt1][2],None,None,None]
            errors = True
            mergedErrors.append([iso1.isoformat(),observations1[cnt1][1],observations1[cnt1][2],None,None,None])
            cnt2 += 1
            if cnt1<stop1 and cnt2>stop2:
                cnt1 += 1
            
        elif iso1 == iso2:
            #row.extend([iso1.isoformat(),observations1[cnt1][1],observations1[cnt1][2],iso2.isoformat(),observations2[cnt2][1],observations2[cnt2][2]])
            row = [iso1.isoformat(),observations1[cnt1][1],observations1[cnt1][2],iso2.isoformat(),observations2[cnt2][1],observations2[cnt2][2]]
            if observations1[cnt1][1] != observations2[cnt2][1]:
                if observations1[cnt1][1]=='-999.900000' and observations2[cnt2][1] == 'None':
                    pass
                elif observations1[cnt1][1]=='-999.900000' and observations2[cnt2][1] != '-999.900000':
                    pass
                elif observations1[cnt1][1]=='-999.900000' and observations2[cnt2][1] != 'None':
                    pass
                else:
                    errors = True
                    mergedErrors.append([iso1.isoformat(),observations1[cnt1][1],observations1[cnt1][2],iso2.isoformat(),observations2[cnt2][1],observations2[cnt2][2]])
                    #print "%s - %s == %s" % (iso1.isoformat(), observations1[cnt1][1], observations2[cnt2][1])
            # QI Check
            '''if observations1[cnt1][2] != observations2[cnt2][2]:
                errors = True'''
            cnt1 += 1
            cnt2 += 1
            
        elif iso1 < iso2:
            row = [iso1.isoformat(),observations1[cnt1][1],observations1[cnt1][2],None,None,None]
            cnt1 += 1
            errors = True
            mergedErrors.append([iso1.isoformat(),observations1[cnt1][1],observations1[cnt1][2],None,None,None])
            
        elif iso1 > iso2:
            row = [None,None,None,iso2.isoformat(),observations2[cnt2][1],observations2[cnt2][2]]
            cnt2 += 1
            #errors = True
            
        #print row
        #print ""
        
        merged.append(row)
    
    if errors:
        print "\n  > Checked with errors"
    else:
        print "  > Checked Ok"
        
    if errors:
        check = open('check/%s.csv' % procedure, 'w')
    else:
        check = open('check/_%s.csv' % procedure, 'w')
    
    if len(mergedErrors)>0:
        errorsFile = open('check/%s_errors.csv' % procedure, 'w')
        outErrors = csv.writer(errorsFile, quoting=csv.QUOTE_ALL)
        for row in mergedErrors:
            outErrors.writerow(row)        
        errorsFile.flush()
        errorsFile.close()
        
    print "\n*****************************************************************\n"
    
    outCheck = csv.writer(check, quoting=csv.QUOTE_ALL)
    for row in merged:
        outCheck.writerow(row)        
    check.flush()
    check.close()
    
    
samplingFile.close()   


"""

from lib import requests
from lib import isodate
from scripts import istsosutils
from datetime import timedelta
import csv

td = 200

sos1 = istsosutils.Service("http://geoservice.ist.supsi.ch", "sos")
sos2 = istsosutils.Service("https://geoservice.ist.supsi.ch/isos", "sos")

procedure = 'A_CAL_AIR'

row = []

samp1 = sos1.getSOSProcedureSamplingtime(procedure)
samp2 = sos2.getSOSProcedureSamplingtime(procedure)

row = [procedure]

row.extend([samp1[0].isoformat(),samp2[0].isoformat(),samp1[1].isoformat(),samp2[1].isoformat()])

#sampling.append(row)

minEnd = min(samp1[1],samp2[1])

observations1 = sos1.getSOSProcedureObservations(
    procedure, (minEnd-timedelta(days=td)).isoformat(), minEnd.isoformat())
observations2 = sos2.getSOSProcedureObservations(
    procedure, (minEnd-timedelta(days=td)).isoformat(), minEnd.isoformat())

if len(observations1)==len(observations2):
    stop = len(observations1)
elif len(observations1)>len(observations2):
    stop = len(observations1)
elif len(observations1)<len(observations2):
    stop = len(observations2)
    
merged = [] # ListTable()

stop1 = len(observations1)
stop2 = len(observations2)
cnt1 = cnt2 = 0
stop = max(stop1,stop2)

check = open('check/%s.csv' % procedure, 'w')
outCheck = csv.writer(check, quoting=csv.QUOTE_ALL)

for i in range(0,stop):

    row = []
    iso1 = None
    iso2 = None
    
    if (cnt1)<stop1:
        iso1 = isodate.parse_datetime(observations1[cnt1][0])
        
    if (cnt2)<stop2:
        iso2 = isodate.parse_datetime(observations2[cnt2][0])
    
    if iso1 == None:
        row = [None,None,iso2.isoformat(),observations2[cnt2][1]]
        cnt1 += 1
        
    elif iso2 == None:
        row = [iso1.isoformat(),observations1[cnt1][1],None,None]
        cnt2 += 1
        
    elif iso1 == iso2:
        row.extend([iso1.isoformat(),observations1[cnt1][1],iso2.isoformat(),observations2[cnt2][1]])
        cnt1 += 1
        cnt2 += 1
        
    elif iso1 < iso2:
        row = [iso1.isoformat(),observations1[cnt1][1],None,None]

        cnt1 += 1
        
    elif iso1 > iso2:
        row = [None,None,iso2.isoformat(),observations2[cnt2][1]]
        cnt2 += 1
        
    merged.append(row)

    outCheck.writerow(row)        
    check.flush()
    
    #print row
    
print "  > Checked"

#samplingFile.close()   
check.close()


"""
