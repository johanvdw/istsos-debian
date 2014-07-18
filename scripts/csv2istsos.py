# -*- coding: utf-8 -*-
# istSOS WebAdmin - Istituto Scienze della Terra
# Copyright (C) 2013 Massimiliano Cannata, Milan Antonovic
#
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

'''
This script 
'''

import sys
import os
from os import path
import traceback
import json
import pprint
import glob
from datetime import datetime

#print path.abspath(".")
#print path.normpath("%s/../" % path.abspath("."))
    
sys.path.insert(0, path.abspath("."))
try:
    import lib.argparse as argparse
    import lib.requests as requests
    import lib.isodate as iso
    from lib.pytz import timezone
except ImportError as e:
    print "\nError loading internal libs:\n >> did you run the script from the istSOS root folder?\n\n"
    raise e

datacache = {}

def execute (args, logger=None):
    
    def log(message):
        if logger:
            logger.log(message)
        else:
            print message
    
    pp = pprint.PrettyPrinter(indent=2)
    
    try:
    
        # Initializing URLs
        url = args['u']
        
        # Service instance name
        service = args['s']
        
        # Quality index
        quality = '100'
        if 'q' in args:
            quality = args['q']
        
        # Procedures
        procs = args['p']
        
        # Working directory, where the CSV files are located
        wd = args['wd']
        
        # File extension
        ext = '.dat'
        if 'e' in args:
            ext = args['e']
        
        debug = False
        if 'v' in args:
            debug = args['v']
        
        test = False
        if 't' in args:
            test = args['t']
        
        user = None
        if 'usr' in args:
            user = args['usr']
        passw = None
        if 'pwd' in args:
            passw = args['pwd']
            
        #req = requests.session()
        req = requests
        
        for proc in procs:
            
            log("\nProcedure: %s" % proc)
            
            # Load procedure description                
            res = req.get("%s/wa/istsos/services/%s/procedures/%s" % (
                url,
                service,
                proc
                ), prefetch=True, auth=(user, passw), verify=False)
                
            data = res.json
            #log(pp.pprint(data))
                
            if data['success']==False:
                raise Exception ("Description of procedure %s can not be loaded: %s" % (proc, data['message']))
            else:
                if debug:
                    pp.pprint(data)
                else:
                    print " > %s" % data['message']
            
            data = data['data']
            
            aid = data['assignedSensorId']
            
            # Getting observed properties from describeSensor response
            op = []
            for out in data['outputs']:
                op.append(out['definition'])
            
            # Load of a getobservation request
            res = req.get("%s/wa/istsos/services/%s/operations/getobservation/offerings/%s/procedures/%s/observedproperties/%s/eventtime/last" % (
                url,
                service,
                'temporary',
                proc,
                ','.join(op)
                ), prefetch=True, auth=(user, passw), verify=False)
            
            data = res.json
            
            if data['success']==False:
                raise Exception ("Last observation of procedure %s can not be loaded: %s" % (proc, data['message']))
            else:
                if debug:
                    pp.pprint(data)
                else:
                    print " > %s" % data['message']
                    
            data = data['data'][0]
            data['AssignedSensorId'] = aid
            
            # Set values array empty (can contain 1 value if procedure not empty)
            data['result']['DataArray']['values'] = []
            
            # discover json observed property disposition
            jsonindex = {}
            for pos in range(0, len(data['result']['DataArray']['field'])):
                field = data['result']['DataArray']['field'][pos]
                jsonindex[field['definition']] = pos
            
            log ("Searching: %s" % os.path.join(wd, "%s_[0-9]*%s" % (proc,ext)))
                
            files = glob.glob(os.path.join(wd, "%s_*%s" % (proc,ext)))
            files.sort()
            
            if debug:
                print " > %s %s found" % (len(files), "Files" if len(files)>1 else "File")
                
            for f in files:
            
                # open file
                file = open(f, 'rU')
                
                # loop lines
                lines = file.readlines()
                
                obsindex = lines[0].strip(' \t\n\r').split(",")
                
                # Check if all the observedProperties of the procedure are included in the CSV file (quality index is optional)
                for k, v in jsonindex.iteritems():
                    if k in obsindex:
                        continue
                    elif ':qualityIndex' in k:
                        continue
                    else:
                        raise Exception ("Mandatory observed property %s is not present in the CSV." % k)
                
                # loop lines skipping the header
                for i in range(1, len(lines)):
                    try:
                        line = lines[i]
                        lineArray = line.strip(' \t\n\r').split(",")
                        
                        # Creating an empty array where the values will be inserted
                        observation =  ['']*len(jsonindex)
                        
                        for k, v in jsonindex.iteritems():
                            val = None
                            if k in obsindex:
                                val = lineArray[obsindex.index(k)]
                            elif ':qualityIndex' in k: # Quality index is not present in the CSV so the default value will be set
                                val = quality
                                
                            observation[v] = val
                            
                        # attach to object
                        data['result']['DataArray']['values'].append(observation)
                        
                    except Exception as e:
                        print "Errore alla riga: %s" % i
                        raise e
                        
            log ("Before insert ST:")
            log (" > Begin: %s" % data["samplingTime"]["beginPosition"])
            log ("   + End: %s" % data["samplingTime"]["endPosition"])
            
            ep = datetime.strptime(
                os.path.split(f)[1].replace("%s_" % proc, "").replace(ext, ""),"%Y%m%d%H%M%S%f"
            ).replace(tzinfo=timezone('UTC')) # .isoformat()
            
            # @todo: date shall be converted in datetime objects
            if len(data['result']['DataArray']['values'])>0:
                bp = iso.parse_datetime(
                    data['result']['DataArray']['values'][0][jsonindex['urn:ogc:def:parameter:x-istsos:1.0:time:iso8601']]
                )
                if bp > iso.parse_datetime(data["samplingTime"]["endPosition"]):
                    bp = iso.parse_datetime(data["samplingTime"]["endPosition"])
            else:
                if ep > iso.parse_datetime(data["samplingTime"]["endPosition"]):
                    bp = iso.parse_datetime(data["samplingTime"]["endPosition"])
                else:
                    raise Exception("Something is wrong with begin position..")
                    
            data["samplingTime"] = {
                "beginPosition": bp.isoformat(),
			   "endPosition":  ep.isoformat()
            }
            
            #data["result"]["DataArray"]["elementCount"] = str(len(data['result']['DataArray']['values']))
            
            log ("Insert ST:")
            log (" > Begin: %s" % bp.isoformat())
            log ("   + End: %s" % ep.isoformat())
            log (" > Values: %s" % len( data['result']['DataArray']['values']))
                
            if not test and len(files)>0: # send to wa
                res = req.post("%s/wa/istsos/services/%s/operations/insertobservation" % (
                    url,
                    service), 
                    prefetch=True,
                    auth=(user, passw),
                    verify=False,
                    data=json.dumps({
                    "ForceInsert": "true",
                    "AssignedSensorId": aid,
                    "Observation": data
                    })
                )
                # read response
                log (" > Insert observation success: %s" % res.json['success'])
                if not res.json['success']:
                    log (res.json['message'])
                    
                
                print "~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~"
        pass
        
    except Exception as e:    
        print "ERROR: %s\n\n" % e
        traceback.print_exc()
        pass
        
    pass
    

    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Import data from a csv file.')
    
    parser.add_argument('-v','--verbose',
        action = 'store_true',
        dest   = 'v',
        help   = 'Activate verbose debug')
        
    parser.add_argument('-t','--test',
        action = 'store_true',
        dest   = 't',
        help   = 'Use to test the command, deactivating the insert observation operations.')
        
    parser.add_argument('-p', 
        action='store',
        required=True,
        nargs='+',
        dest='p',
        metavar='procedures',
        help='List of procedures to be aggregated.')
    
    parser.add_argument('-q',
        action = 'store',
        dest   = 'q',
        metavar= 'quality index',
        default= '100',
        help   = 'The quality index to set for all the measures of the CSV file, if not set into the CSV. (default: %(default)s).')
        
    parser.add_argument('-u',
        action = 'store',
        dest   = 'u',
        metavar= 'url',
        default= 'http://localhost:80/istsos',
        help   = 'IstSOS Server address IP (or domain name) used for all request. (default: %(default)s).')
    
    parser.add_argument('-s',
        action = 'store',
        required=True,
        dest   = 's',
        metavar= 'service',
        
        help   = 'The name of the service instance.')
    
    parser.add_argument('-w',
        action = 'store',
        required=True,
        dest   = 'wd',
        metavar= 'working directory',
        help   = 'Working directory where the csv files are located.')
        
    parser.add_argument('-e',
        action = 'store',
        dest   = 'e',
        metavar= 'file extension',
        default= '.dat',
        help   = 'Extension of the CSV file. (default: %(default)s)')
        
    parser.add_argument('-usr',
        action = 'store',
        dest   = 'usr',
        metavar= 'user name')
        
    parser.add_argument('-pwd',
        action = 'store',
        dest   = 'pwd',
        metavar= 'password')

    args = parser.parse_args()
    #print args.__dict__
    execute(args.__dict__)


