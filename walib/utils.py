# -*- coding: utf-8 -*-
# istSOS WebAdmin - Istituto Scienze della Terra
# Copyright (C) 2012 Massimiliano Cannata, Milan Antonovic
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

import sys, traceback

def valid_NCName(name):
    not_allowed_NCName = [' ', '!','"', '#', '$', '%', '&', '\'', 
                          '(', ')', '*', '+', ',', '/', ':', ';', 
                          '<', '=', '>', '?', '@', '[', '\\', ']', 
                          '^', '`', '{', '|', '}', '~']
    for c in not_allowed_NCName:
        if name.find(c)>0:
            return False
    return True                

def validatedb(user,password,dbname,host,port=5432,service=None):
    """
    Validate a service db connection parameters
    
    @param user: user name used to authenticate
    @param password: password used to authenticate
    @param dbname: the database name (only in dsn string)
    @param host: database host address
    @param port: onnection port number (optional - defaults to 5432)
    @param service: service name that correspond with associated database schema (optional)
    @return: L{True} if connection could be estabished and the schema found (only if schema is provided)
    """
    from walib import databaseManager
    test_conn = databaseManager.PgDB(user,password,dbname,host,port)
    if not service == None or service=="default":
        sql = "SELECT count(*) from pg_namespace WHERE nspname = %s"
        par = (service,)
        res = test_conn.select(sql,par)
        if len(res)==1:
            pass
        else:
            raise Exception("CONNECTION ERROR: wrong schema %s" % service)

def preventInjection(sql):
    """
    Parse given sql with regex for possible malicious sql ignection
    
    @param sql: text to parse
    @param type: L{string}
    @return: L{True} if no malicious sql ingnection was detected
    """
    regex = "(\W)|(\d)|(script)|(&lt;)|(&gt;)|(%3c)|(%3e)|(SELECT) |(UPDATE) |(INSERT) |(DELETE)|(GRANT) |(REVOKE)|(UNION)|(&amp;lt;)|(&amp;gt;)/gi"
    import re
    p = re.compile(regex,re.IGNORECASE)
    if p.search( sql ):
        raise Exception("detected possible malicius SQL injection, please change service name avoiding spaces and SQL reserved words")
    return True

def getServiceList(servicepath,listonly=False):
    """
    Return the list of istsos services
    
    @param servicepath: path to service folder
    @param listonly: define if only service list is requested (optional - default L{False})
    @param type: L{boolean}
    @return: return a list of services
    
        >>> Return example with listonly==True :
            [name1,name2,...]
            
        >>> Return example with listonly==False:
            [
                {"service":name1,"path":path1},
                {"service":name1,"path":path1},
                ...
            ]
    """
    import os, fnmatch
    services=[]
    for root, dirnames, filenames in os.walk( servicepath ):
        for filename in fnmatch.filter(filenames, '*.cfg'):
            service = filename.split(".")[0].split("/")[-1]
            path = os.path.join(root, filename)
            if service == "default" or service == "wa":
                continue
            else:
                if listonly==True:
                    services.append(service)
                else:
                    services.append({"service":service,"path":path})
    return services

def getOfferingNamesList(pgdb,service):
    """
    Return the list of offerings for a give istsos service connection
    
    @param pgdb: service connection
    @type pgdb: L{wa.databaseManager.PgDB} object
    @param service: service name
    @type service: L{string}
    @return: C{list} of C{dict} with offering C{id} and C{name} keys
    
    >>> Return example:
        [
            { "id":1,"name":"temporary"},
            { "id":2,"name":"water"},
            { "id":3,"name":"air"}
        ]
    
    """
    sql  = "SELECT id_off, name_off FROM %s.offerings ORDER BY name_off" %((service,))
    rows = pgdb.select(sql,None)
    if rows:
        return [ { "id":row["id_off"] , "name":row["name_off"]} for row in rows ]
    else:
        return []
        
def getOfferingDetailsList(pgdb,service):
    """
    Return the list of offerings details for a given istsos service connection
    
    @param pgdb: service connection
    @type pgdb: L{wa.databaseManager.PgDB} object
    @param service: service name
    @type service: L{string}
    @return: C{list} of C{dict} with offering C{id} and C{name} keys
    
    >>> Return example:
        [
            {"name": "temperature","description": "descrizione 3","procedures": 12,"expiration": "22.12.2012","active": true},
            {"name": "water","description": "descrizione 3","procedures": 22,"expiration": "22.12.2012","active": true},
            {"name": "air","description": "descrizione 3","procedures": 3,"expiration": "22.12.2012","active": true}
        ]
    """
    sql  = """
        SELECT DISTINCT id_off as id, name_off as name, desc_off as description, 
            expiration_off as expiration, active_off as active, count(id_off_prc) as procedures
        FROM %s.offerings
        LEFT JOIN %s.off_proc 
            ON id_off = id_off_fk
        GROUP BY id_off, name_off, desc_off, expiration_off, active_off
        ORDER BY name_off; """ %((service,)*2)
    rows = pgdb.select(sql,None)
    if rows:
        from lib import isodate
        return [
            {
                "id":row["id"],
                "name":row["name"],
                "description":row["description"],
                "procedures":row["procedures"],
                "expiration": isodate.datetime_isoformat(row["expiration"]) if row["expiration"] else "",
                "active":row["active"]
            } for row in rows
        ]
    else:
        return []

def getProcedureNamesList(pgdb,service,offering=None, observationType=None):
    """
    Return the list of procedures:
        
        The list can be filtered by offering and/or observationType
    
    @param pgdb: service connection
    @type pgdb: L{wa.databaseManager.PgDB} object
    @param service: service name
    @type service: L{string}
    @param offering: filter procedures by this offering name
    @type offering: C{string} or C{None}
    @type observationType: C{string} or C{None}
    @return: C{list} of C{dict} with procedure C{id} and C{name} keys
    
    >>> Return example:
        [
            { "id":1,"name":"Chiasso", "description": "", "assignedid": "1234"},
            { "id":2,"name":"Bellinzona", "description": "", "assignedid": "1235"},
            { "id":3,"name":"Lugano", "description": "", "assignedid": "1236"}
        ]
    """
    if offering==None:
        if observationType==None:            
            sql = """
                SELECT id_prc, name_prc, desc_prc, assignedid_prc, name_oty, stime_prc, etime_prc
                FROM %s.procedures, %s.obs_type 
                WHERE id_oty_fk = id_oty 
                ORDER BY name_prc""" %((service,)*2)
            rows = pgdb.select(sql)
            
        else:
            sql = """
                SELECT id_prc, name_prc, desc_prc, assignedid_prc, name_oty, stime_prc, etime_prc
                FROM %s.procedures, %s.obs_type 
                WHERE id_oty_fk = id_oty""" % ((service,)*2)
            sql += """
                AND name_oty = %s
                ORDER BY name_prc""" 
            rows = pgdb.select(sql,(observationType,))
    else:
        if observationType==None:   
            sql  = """
                SELECT id_prc, name_prc, desc_prc, assignedid_prc, name_oty, stime_prc, etime_prc
                FROM %s.off_proc op, %s.procedures p, %s.offerings o, %s.obs_type """ %((service,)*4)
            sql += """ 
                WHERE o.id_off = op.id_off_fk 
                AND op.id_prc_fk = p.id_prc  
                AND id_oty_fk = id_oty
                AND o.name_off = %s
                ORDER BY p.name_prc; """
            rows = pgdb.select(sql,(offering,))
        else:
            sql = """
                SELECT id_prc, name_prc, desc_prc, assignedid_prc, name_oty, stime_prc, etime_prc
                FROM %s.off_proc op, %s.procedures, %s.offerings, %s.obs_type """ % ((service,)*4)
            sql += """
                WHERE o.id_off=op.id_off_fk 
                AND op.id_prc_fk=p.id_prc 
                AND id_oty_fk = id_oty
                AND o.name_off = %s
                AND name_oty = %s
                ORDER BY name_prc""" 
            rows = pgdb.select(sql,(offering, observationType))
            
    if rows:
    
        ret = []
        for row in rows:
            begin = ""
            end = ""
            
            if row["stime_prc"]:
                begin = row["stime_prc"].strftime("%Y-%m-%dT%H:%M:%S%z")
            if row["etime_prc"]:
                end = row["etime_prc"].strftime("%Y-%m-%dT%H:%M:%S%z")
            
            ret.append({ 
                "id": row["id_prc"], 
                "name": row["name_prc"], 
                "description": row["desc_prc"], 
                "assignedid": row["assignedid_prc"], 
                "sensortype": row["name_oty"], 
                "samplingTime": {
                    "beginposition": begin, 
                    "endposition": end
                }
            })
            
        return ret
    else:
        return []
               

def getObsPropNamesList(pgdb,service,offering=None):
    """
    Return the list of observed properties
    
    @param pgdb: service connection
    @type pgdb: L{wa.databaseManager.PgDB} object
    @param service: service name
    @type service: L{string}
    @param offering: filter procedures by this offering name
    @type offering: C{string} or C{None}
    @return: C{list} of C{dict} with observed property C{id} and C{name} keys
    
    >>> Return example:
        [
            { "id":1,"name":"urn:ogc:def:parameter:x-istsos:1.0:lake:water:height"},
            { "id":2,"name":"urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall"}
        ]
    
    """
    if offering==None:
        sql  = "SELECT DISTINCT id_opr, name_opr FROM %s.observed_properties ORDER BY name_opr" %((service,))
        rows = pgdb.select(sql)
    else:
        sql  = "SELECT DISTINCT id_opr, name_opr"
        sql += " FROM %s.procedures p, %s.proc_obs po ,%s.observed_properties obs" %((service,)*3)
        sql += ", %s.off_proc op, %s.offerings o" %((service,)*2)
        sql += " WHERE po.id_prc_fk=p.id_prc AND po.id_opr_fk=obs.id_opr"
        sql += " AND p.id_prc=op.id_prc_fk AND op.id_off_fk=o.id_off AND o.name_off=%s ORDER BY obs.name_opr"
        rows = pgdb.select(sql,(offering,))
    if rows:
        return [ { "id":row["id_opr"] , "name":row["name_opr"]} for row in rows ]
    else:
        return None

def getFoiNamesList(pgdb,service,offering=None):
    """
    Return the list of observed properties
    
    @param pgdb: service connection
    @type pgdb: L{wa.databaseManager.PgDB} object
    @param service: service name
    @type service: L{string}
    @param offering: filter procedures by this offering name
    @type offering: C{string} or C{None}
    @return: C{list} of C{dict} with observed property C{id} and C{name} keys
    
    >>> Return example:
        [
            { "id":1,"name":"urn:ogc:def:parameter:x-istsos:1.0:lake:water:height"},
            { "id":2,"name":"urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall"}
        ]
    
    """
    if offering==None:
        sql = "SELECT DISTINCT id_foi,(name_fty || ':' || name_foi) as name_foi" 
        sql += " FROM %s.off_proc op, %s.procedures p, %s.foi f, %s.feature_type ft" %((service,)*4)
        sql += " WHERE op.id_prc_fk=p.id_prc AND p.id_foi_fk=f.id_foi AND f.id_fty_fk=ft.id_fty"
        sql += " ORDER BY name_foi"
        rows = pgdb.select(sql)
    else:
        sql = "SELECT DISTINCT id_foi,(name_fty || ':' || name_foi) as name_foi" 
        sql += " FROM %s.off_proc op, %s.procedures p, %s.foi f" %((service,)*3)
        sql += ", %s.feature_type ft, %s.offerings o" %((service,)*2)
        sql += " WHERE op.id_prc_fk=p.id_prc AND op.id_off_fk=o.id_off AND o.name_off=%s"
        sql += " AND p.id_foi_fk=f.id_foi AND f.id_fty_fk=ft.id_fty"
        sql += " ORDER BY name_foi"
        rows = pgdb.select(sql,(offering,))
    if rows:
        return [ { "id":row["id_foi"] , "name":row["name_foi"]} for row in rows ]
    else:
        return None


def getGeoJSONFromProcedure(pgdb, service, procedure, epsg):
    """
    >>> Return example:
        {"type":"Point","coordinates":[8.961270000000001,46.027230000000003,344.100000000000023]}    
    """
    import json
    sql = """ 
        SELECT st_asgeojson(ST_Transform(geom_foi,%s)) as gjson
        FROM %s.foi, %s.procedures    
        WHERE id_foi = id_foi_fk
    """ % (epsg,service,service)
    sql += "AND name_prc=%s"
    rows = pgdb.select(sql,(procedure,))
    if rows:
        return  json.loads(rows[0]["gjson"])
    else:
        return None
    
def getObservedPropertiesFromProcedure(pgdb,service,procedure):
    """
    Return the list of observed properties related to the given procedure
    
    @param pgdb: service connection
    @type pgdb: L{wa.databaseManager.PgDB} object
    @param service: service name
    @type service: L{string}
    @param procedureID: filter procedure id
    @type procedure: C{string} or C{None}
    @return: C{list} of C{dict} with observed property C{id} and C{name} keys
    
    >>> Return example:
        [
            { "id":1,"name":"urn:ogc:def:parameter:x-istsos:1.0:lake:water:height"},
            { "id":2,"name":"urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall"}
        ]
    
    """
    sql  = "SELECT id_opr, name_opr, name_uom"
    sql += " FROM %s.proc_obs po, %s.procedures p, %s.observed_properties o, %s.uoms u" %((service,)*4) 
    sql += " WHERE po.id_prc_fk=p.id_prc AND po.id_opr_fk=o.id_opr AND po.id_uom_fk=u.id_uom"
    sql += " AND name_prc=%s"
    params = (procedure,)
    # @todo check this double tuple ?
    rows = pgdb.select(sql,(params,))
    if rows:
        return [ { "id":row["id_opr"] , "name":row["name_opr"], "uom":row["name_uom"]} for row in rows ]
    else:
        return None

def getOfferingsFromProcedure(pgdb,service,procedure):
    """
    Return the list of offerings related to the given procedure
    
    @param pgdb: service connection
    @type pgdb: L{wa.databaseManager.PgDB} object
    @param service: service name
    @type service: L{string}
    @param procedureID: filter procedure id
    @type procedure: C{string} or C{None}
    @return: C{list} of C{dict} with observed property C{id} and C{name} keys
    
    >>> Return example:
        [
            { "id":1,"name":"urn:ogc:def:parameter:x-istsos:1.0:lake:water:height"},
            { "id":2,"name":"urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall"}
        ]
    
    """
    sql  = "SELECT id_off, name_off"
    sql += " FROM %s.off_proc op, %s.procedures p, %s.offerings o" %((service,)*3) 
    sql += " WHERE op.id_prc_fk=p.id_prc AND op.id_off_fk=o.id_off"
    sql += " AND name_prc=%s"
    params = (procedure,)
    rows = pgdb.select(sql,(params,))
    if rows:
        return [ { "id":row["id_off"] , "name":row["name_off"] } for row in rows ]
    else:
        return None    

def verifyxmlservice(url):
    import lib.requests as requests
    from lib.etree import et
    try:
        response = requests.get(url)
        response.raise_for_status()
        root = et.fromstring(response.text)
        if not root.find("Exception") == None:
            return "up with error"
        else:
            return  "up"
    except Exception as e:
        print >> sys.stderr, traceback.print_exc()
        return "down"

def getObservationPeriod(pgdb,service,procedures):
    """
    Return the list of procedures with observation periods
    
    @param pgdb: service connection
    @type pgdb: L{wa.databaseManager.PgDB} object
    @param service: service name
    @type service: L{string}
    @param procedures: procedures
    @type procedure: C{list} of C{string}
    @return: C{list} of C{dict} with procedure, stime (start time) and etime (end time) keys
    
    >>> Return example:
        [
            { "procedure":"P_TRE","stime":"2000-12-31T23:00:00Z", "etime":"2012-12-31T23:00:00Z"},
            { "procedure":"P_ BOD","stime":"1986-12-31T23:00:00Z", "etime":"2012-12-31T23:00:00Z"}
        ]
    
    """
    sql  = "SELECT name_prc, stime_prc, etime_prc"
    sql += " FROM %s.procedures p" %((service,)*3) 
    sql += " WHERE name_prc IN %s"
    params = touple(procedure)
    rows = pgdb.select(sql,(params,))
    if rows:
        return [ { "procedure":row["name_prc"] , "stime":row["stime_prc"], "etime":row["etime_prc"] } for row in rows ]
    else:

        return None 
"""    
def gmlToGeojson(pgdb,gmlstr):
    ""
    Return the list of observed properties
    
    @param pgdb: service connection
    @type pgdb: L{wa.databaseManager.PgDB} object
    @param gmlstr: gml geometry as text
    @type service: L{string}
    @return: C{dict} of geomatry in GeoJson format
    
    >>> Return example:
        [
            {
                "type":"Point",
                "coordinates":[693682,145597,1471],
                "crs": {
                    "type": "name",
                    "properties": {
                        "name": "EPSG:21781"
                    }
                }
            }
        ]
    
    ""
    
    geojsonsql = "SELECT st_asgeojson(st_geomfromgml(%s)) as geojson"
    params = (gmlstr,)
    geojson = pgdb.select(geojsonsql,params)[0]["geojson"]
    
    sridsql = "SELECT st_srid(st_geomfromgml(%s)) as srid""
    srid = pgdb.select(sridsql,params)[0]["srid"]

    exec("geojson=%s" % geojson)
    geojson["crs"] = {}
    geojson["crs"]["type"] = "name"
    geojson["crs"]["properties"] = {}
    geojson["crs"]["properties"]["name"] = "EPSG:%s" % srid
    
    return geojson

"""
"""    
--SELECT st_asewkt(st_geomfromgml('<gml:Point gml:id="SYSTEM_LOCATION" srsName="EPSG:21781">
--<gml:coordinates>693682,145597,1471</gml:coordinates></gml:Point>'))

SELECT st_srid(st_geomfromgml('<gml:Point gml:id="SYSTEM_LOCATION" srsName="EPSG:21781">
<gml:coordinates>693682,145597,1471</gml:coordinates></gml:Point>'))    
"""


'''
Workaround to prevent encoding change during execution exception
'''


import psycopg2 # @TODO the right library
import psycopg2.extras

def to_unicode_or_bust(obj, encoding='utf-8'):
    try:
        if isinstance(obj, basestring):
            if not isinstance(obj, unicode):
                obj = unicode(obj, encoding)
    except Exception as e:
        print >> sys.stderr, "to_unicode_or_bust(%s,%s)\n%s" % (obj,encoding,traceback.print_exc())
    return obj
    
    

def encodeobject(obj, encoding='utf-8'):
    try:
        if type(obj) is list:
            for key, value in enumerate(obj):
                
                if type(value) is dict or type(value) is psycopg2.extras.DictRow:
                    obj[key] = encodeobject(value, encoding)
                elif type(value) is list:
                    obj[key] = encodeobject(value, encoding)
                else:
                    obj[key] = to_unicode_or_bust(value, encoding)
        elif type(obj) is dict or type(obj) is psycopg2.extras.DictRow:
            for key, value in obj.iteritems():
                if type(value) is dict:
                    obj[key] = encodeobject(value, encoding)
                elif type(value) is list:
                    obj[key] = encodeobject(value, encoding)
                else:
                    obj[key] = to_unicode_or_bust(value, encoding)
    except Exception as e:
        print >> sys.stderr, traceback.print_exc()
    return obj
            
    
def validateJsonConstraint(constraint):
    """
    Permitted conigurations:
        {"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0","min":"10"}
        {"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0","max":"10"}
        {"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0","interval":["-10","10"]}
        {"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0","valueList":["1","2","3","4","5","6"]}
    """
    if 'min' in constraint:
        try:
            float(constraint['min'])
        except ValueError:
            raise Exception("Min value in constraint definition must be numeric")
    elif 'max' in constraint:
        try:
            float(constraint['max'])
        except ValueError:
            raise Exception("Max value in constraint definition must be numeric")
    elif 'interval' in constraint:
        if not type(constraint['interval']) == type([]):
            raise Exception("Constraint interval must be an array containint two numeric values")
        if len(constraint['interval']) != 2:
            raise Exception("Constraint interval must be an array containint two numeric values")
        try:
            float(constraint['interval'][0])
            float(constraint['interval'][1])
        except ValueError:
            raise Exception("Constraint interval must be an array containint two numeric values")
    elif 'valueList' in constraint:
        if not type(constraint['valueList']) == type([]):
            raise Exception("Constraint valueList must be an array containint a series of numeric values")
        if len(constraint['valueList']) <= 2:
            raise Exception("Constraint valueList must be an array containint at least 1 numeric value")
        try:
            for val in constraint['valueList']:
                float(val)
        except ValueError:
            raise Exception("Constraint valueList must be an array containint a series of numeric values")
            
    
    
