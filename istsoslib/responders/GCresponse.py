# -*- coding: utf-8 -*-
# istsos Istituto Scienze della Terra Sensor Observation Service
# Copyright (C) 2010 Massimiliano Cannata
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


import psycopg2 # @TODO the right library
import psycopg2.extras

#import sosConfig
from istsoslib import sosDatabase
from istsoslib import sosException

class ServiceIdentification:
    def __init__(self,sosConfig):
        self.title=sosConfig.serviceIdentification["title"]
        self.abstract=sosConfig.serviceIdentification["abstract"]
        self.keywords=sosConfig.serviceIdentification["keywords"]
        self.serviceTypeCode=sosConfig.serviceType["codespace"]
        self.serviceTypeValue=sosConfig.serviceType["value"]
        self.serviceTypeVersion=sosConfig.serviceType["version"]
        self.fees=sosConfig.serviceIdentification["fees"]
        self.accessconstrains=sosConfig.serviceIdentification["accessConstrains"]
    
class ServiceProvider:
    def __init__(self,sosConfig):
        self.providerName=sosConfig.serviceProvider["providerName"]
        self.providerSite=sosConfig.serviceProvider["providerSite"]
        self.individualName=sosConfig.serviceProvider["serviceContact"]["individualName"]
        self.positionName=sosConfig.serviceProvider["serviceContact"]["positionName"]
        self.contactVoice=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["voice"]
        self.contactFax=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["fax"]
        self.contactDelivery=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["deliveryPoint"]
        self.contactCity=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["city"]
        self.contactArea=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["administrativeArea"]
        self.contactPostCode=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["postalCode"]
        self.contactCountry=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["country"]
        self.contactMail=sosConfig.serviceProvider["serviceContact"]["contactInfo"]["email"]

class Parameter:
    def __init__(self,name,use="optional",allowedValues=[],range=[]):
        self.name=name
        self.use=use
        self.allowedValues=allowedValues
        self.range=range

class Operation:
    def __init__(self,name,get="",post=""):
        self.name=name
        self.get=get
        self.post=post
        self.parameters=[]
    def addParameter(self,name,use="optional",allowedValues=[],range=[]):
        self.parameters.append(Parameter(name,use,allowedValues,range))
    
def BuildSensorIdList(pgdb,sosConfig):
    list=[]
    sql = "SELECT name_prc FROM %s.procedures ORDER BY name_prc" %(sosConfig.schema)
    try:
        rows=pgdb.select(sql)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql)))
    for row in rows:
        list.append(sosConfig.urn["procedure"] + row["name_prc"])    
    return list
    
def BuildOfferingList(pgdb,sosConfig):
    list=[]
    sql = "SELECT distinct(name_off) FROM %s.procedures, %s.off_proc, %s.offerings" %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_prc=id_prc_fk AND id_off_fk=id_off ORDER BY name_off"
    try:
        rows=pgdb.select(sql)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql)))
    #rows=pgdb.select(sql)
    for row in rows:
        list.append(sosConfig.urn["offering"] +row["name_off"])
    return list

def BuildEventTimeRange(pgdb,sosConfig):
    sql = "SELECT min(stime_prc) as b, max(etime_prc) as e FROM %s.procedures" %(sosConfig.schema)
    #sql = "SELECT min(time_eti) as b, max(time_eti) as e FROM %s.event_time" %(sosConfig.schema)
    try:
        rows=pgdb.select(sql)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql)))
    #check if not observation?!?!?!?
    return [rows[0]["b"],rows[0]["e"]]

def BuildobservedPropertyList(pgdb,sosConfig):
    list=[]
    sql = "SELECT distinct(def_opr) as nopr FROM %s.procedures,%s.proc_obs,%s.observed_properties" %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_prc_fk=id_prc AND id_opr_fk=id_opr ORDER BY nopr"
    rows=pgdb.select(sql)
    for row in rows:
        #list.append(sosConfig.urn["phenomena"] + row["nopr"])
        list.append(row["nopr"])
    return list

def BuildfeatureOfInterestList(pgdb,sosConfig):
    list=[]
    sql = "SELECT distinct(name_fty||':'||name_foi) as nfoi FROM %s.foi, %s.feature_type" %(sosConfig.schema,sosConfig.schema) 
    sql += " WHERE id_fty=id_fty_fk ORDER BY nfoi"
    try:
        rows=pgdb.select(sql)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql)))
    for row in rows:
        list.append(sosConfig.urn["feature"] + row["nfoi"])
    return list

def BuildOffEnvelope(pgdb,id,sosConfig):
    sql = "SELECT ST_asgml(Box2D(u.geom)) as ext FROM"
    sql += " ("
    #----case obs_type = fix
    sql += " SELECT ST_Transform(geom_foi,%s) as geom FROM %s.off_proc," %(sosConfig.istsosepsg,sosConfig.schema)
    sql += " %s.procedures, %s.foi" %(sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_prc_fk=id_prc AND id_foi_fk=id_foi AND id_off_fk=%s"
    #---------------
    sql += " UNION"
    #----case obs_type = mobile
    sql += " SELECT ST_Transform(geom_pos,%s) as geom FROM %s.positions, %s.event_time e," %(sosConfig.istsosepsg,sosConfig.schema,sosConfig.schema)
    sql += " %s.procedures, %s.off_proc o" %(sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_eti=id_eti_fk AND id_prc=e.id_prc_fk AND id_prc=o.id_prc_fk AND id_off_fk=%s"
    #----------------
    sql += " ) u"
    params=(id,id)
    try:
        rows=pgdb.select(sql,params)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql,params)))
        
    # Retrieve any of the gml:* elements below to go inside the gml:Envelope tag.
    # Unfortunately, xml.etree.ElementTree.fromstring cannot parse xml elements with
    # an unknown prefix, so I have to revert to string manipulation.
    result = "<gml:Null>Not Applicable</gml:Null>"
    if rows:
        gml = rows[0]["ext"]
        # TODO: a better solution would be to parse these from the schema definition.
        for element in ['gml:coordinates','gml:lowerCorner', 'gml:coord', 'gml:pos']:
            open_tag = '<%s>' % element
            close_tag = '</%s>' % element
            pos = gml.find(open_tag)
            if pos:
                gml = gml[pos:]
                pos = gml.find(close_tag)
                result = gml[:pos+len(close_tag)]
                break
    return result


def BuildOffTimePeriod(pgdb,id,sosConfig):
    sql = "SELECT max(etime_prc) as e, min(stime_prc) as b"
    sql += " from %s.procedures, %s.off_proc o" %(sosConfig.schema,sosConfig.schema)
    sql += " WHERE o.id_prc_fk=id_prc and id_off_fk=%s" 
    params = (id,)
    try:
        rows=pgdb.select(sql,params)
    except Exception as err:
        raise Exception("SQL2: %s - %s" %(pgdb.mogrify(sql,params), err))
    
    return [rows[0]["b"],rows[0]["e"]]

def BuildOffProcList(pgdb,id,sosConfig):
    list=[]
    sql = "SELECT distinct(name_prc)"
    sql += " FROM %s.off_proc, %s.procedures,%s.offerings" %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_off=id_off_fk AND id_prc_fk=id_prc AND id_off=%s"
    sql += " ORDER BY name_prc"
    params = (id,)
    try:
        rows=pgdb.select(sql,params)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql,params)))
    for row in rows:
        #list.append(sosConfig.urn["procedure"] + row["name_prc"])
        list.append(row["name_prc"])
    return list

def BuildOffObsPrList(pgdb,id,sosConfig):
    list=[]
    sql = "SELECT distinct(def_opr)"
    sql += " FROM %s.offerings, %s.off_proc o, %s.procedures," %(sosConfig.schema,sosConfig.schema,sosConfig.schema)
    sql += " %s.proc_obs p, %s.observed_properties" %(sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_off=id_off_fk AND o.id_prc_fk=id_prc AND p.id_prc_fk=id_prc"
    sql += " AND id_opr_fk=id_opr AND id_off=%s" %(id)
    sql += " ORDER BY def_opr"
    params = (id,)
    try:
        rows=pgdb.select(sql,params)
    except:
        raise Exception("sql: %s"%(pgdb.mogrify(sql,params)))
    for row in rows:
        list.append(row["def_opr"])
    return list

def BuildOffFoiList(pgdb,id,sosConfig):
    list=[]

    sql = "SELECT distinct(name_fty || ':' || name_foi) as fois" 

    sql += " FROM %s.off_proc, %s.procedures,%s.foi,%s.feature_type"  %(sosConfig.schema,sosConfig.schema,sosConfig.schema,sosConfig.schema)
    sql += " WHERE id_prc_fk=id_prc AND id_off_fk=%s"
    sql += " AND id_foi_fk=id_foi AND id_fty_fk=id_fty"
    sql += " ORDER BY fois"
    params = (id,)
    try:
        rows=pgdb.select(sql,params)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql,params)))
    for row in rows:
        list.append(sosConfig.urn["feature"] + row["fois"])
    return list

def BuildSensorList(pgdb,sosConfig):
    sql = "SELECT assignedid_prc as id from %s.procedures" %(sosConfig.schema)
    try:
        rows=pgdb.select(sql)
    except:
        raise Exception("sql: %s" %(pgdb.mogrify(sql)))
    return [ sosConfig.urn["sensor"]+str(sid["id"]) for sid in rows ]

class OperationsMetadata:
    def __init__(self,pgdb,sosConfig):
        self.OP=[]
        srslist=[sosConfig.urn["refsystem"]+i for i in sosConfig.parameters["GO_srs"]]

        """ GetCapabilities """
        GetCapabilities=Operation(name="GetCapabilities",get=sosConfig.serviceUrl["get"],post=sosConfig.serviceUrl["post"])
        GetCapabilities.addParameter(name="service",use="required",allowedValues=sosConfig.parameters["service"])
        GetCapabilities.addParameter(name="version",use="required",allowedValues=sosConfig.parameters["version"])
        GetCapabilities.addParameter(name="section",use="optional",allowedValues=sosConfig.parameters["GC_Section"])
        self.OP.append(GetCapabilities)
        
        #DescribeSensor 
        DescribeSensor=Operation(name="DescribeSensor",get=sosConfig.serviceUrl["get"],post=sosConfig.serviceUrl["post"])
        DescribeSensor.addParameter(name="service",use="required",allowedValues=sosConfig.parameters["service"])
        DescribeSensor.addParameter(name="version",use="required",allowedValues=sosConfig.parameters["version"])
        DescribeSensor.addParameter(name="procedure",use="required",allowedValues=BuildSensorIdList(pgdb,sosConfig))
        DescribeSensor.addParameter(name="outputFormat",use="required",allowedValues=sosConfig.parameters["DS_outputFormats"])
        self.OP.append(DescribeSensor)
         
        #GetObservation 
        GetObservation=Operation(name="GetObservation",get=sosConfig.serviceUrl["get"],post=sosConfig.serviceUrl["post"])
        GetObservation.addParameter(name="service",use="required",allowedValues=sosConfig.parameters["service"])
        GetObservation.addParameter(name="version",use="required",allowedValues=sosConfig.parameters["version"])
        GetObservation.addParameter(name="srsName",use="optional",allowedValues=srslist) 
        GetObservation.addParameter(name="offering",use="required",allowedValues=BuildOfferingList(pgdb,sosConfig))
        GetObservation.addParameter(name="eventTime",use="optional",allowedValues=[],range=BuildEventTimeRange(pgdb,sosConfig))
        GetObservation.addParameter(name="procedure",use="optional",allowedValues=BuildSensorIdList(pgdb,sosConfig))
        GetObservation.addParameter(name="observedProperty",use="optional",allowedValues=BuildobservedPropertyList(pgdb,sosConfig))
        GetObservation.addParameter(name="featureOfInterest",use="optional",allowedValues=BuildfeatureOfInterestList(pgdb,sosConfig))
        
        #GetObservation.addParameter(name="result",use="optional",allowedValues=[sosConfig.parameters["result"]])
        GetObservation.addParameter(name="responseFormat",use="required",allowedValues=sosConfig.parameters["GO_responseFormat"])
        GetObservation.addParameter(name="resultModel",use="optional",allowedValues=sosConfig.parameters["GO_resultModel"])
        GetObservation.addParameter(name="responseMode",use="optional",allowedValues=sosConfig.parameters["GO_responseMode"])
        self.OP.append(GetObservation)
         
        #GetFeatureOfInterest 
        GetFeatureOfInterest=Operation(name="GetFeatureOfInterest",get=sosConfig.serviceUrl["get"],post=sosConfig.serviceUrl["post"])
        GetFeatureOfInterest.addParameter(name="service",use="required",allowedValues=sosConfig.parameters["service"])
        GetFeatureOfInterest.addParameter(name="version",use="required",allowedValues=sosConfig.parameters["version"])
        GetFeatureOfInterest.addParameter(name="featureOfInterest",use="required",allowedValues=BuildfeatureOfInterestList(pgdb,sosConfig))
        GetFeatureOfInterest.addParameter(name="srsName",use="optional",allowedValues=srslist)
        self.OP.append(GetFeatureOfInterest)
         
        #RegisterSensor 
        RegisterSensor=Operation(name="RegisterSensor",get=None,post=sosConfig.serviceUrl["post"])
        RegisterSensor.addParameter(name="service",use="required",allowedValues=sosConfig.parameters["service"])
        RegisterSensor.addParameter(name="version",use="required",allowedValues=sosConfig.parameters["version"])
        RegisterSensor.addParameter(name="SensorDescription",use="required",allowedValues=["Any SensorML"])
        RegisterSensor.addParameter(name="ObservationTemplate",use="required",allowedValues=["Any om:Observation"])
        self.OP.append(RegisterSensor)
        
        #--InsertObservation 
        InsertObservation=Operation(name="InsertObservation",get=None,post=sosConfig.serviceUrl["post"])
        InsertObservation.addParameter(name="service",use="required",allowedValues=sosConfig.parameters["service"])
        InsertObservation.addParameter(name="version",use="required",allowedValues=sosConfig.parameters["version"])
        InsertObservation.addParameter(name="AssignedSensorId",use="required",allowedValues=["Any registered sensorID"])
        InsertObservation.addParameter(name="Observation",use="optional",allowedValues=["Any om:Observation"])
        self.OP.append(InsertObservation)
        
        """ optional parameters are:
        result ogc:comparisonOps Zero or one (Optional)
        responseFormat (e.g.: text/xml;schema="ioos/0.6.1" TML, O&M, native format, or MPEG stream out-of-band). (MIME content type) One (mandatory)
        resultModel QName Zero or one (Optional)
        responseMode (inline, out-of-band, attached, resultTemplate) Zero or one (Optional)
        """

class Offering:
    def __init__(self):
        self.id = None
        self.name = None
        self.desc = None
        self.boundedBy = None
        self.beginPosition = None
        self.endPosition = None
        self.procedures=[]
        self.obsProp=[]
        self.fois=[]
         
class ObservationOfferingList:
    #def __init__(self,filter, pgdb):
    def __init__(self, pgdb,sosConfig):        
        self.offerings=[]
        self.responseFormat = sosConfig.parameters["GO_responseFormat"]
        self.resultModel = sosConfig.parameters["GO_resultModel"]
        self.responseMode = sosConfig.parameters["GO_responseMode"]

        #get offering list
        sql = "SELECT id_off,name_off,desc_off from %s.offerings where active_off != false ORDER BY name_off" %(sosConfig.schema)
        rows=pgdb.select(sql)
        for row in rows:
            off = Offering()
            off.id = row["name_off"]
            off.name = sosConfig.urn["offering"] + row["name_off"]
            off.desc = row["desc_off"]
            off.boundedBy = BuildOffEnvelope(pgdb,row["id_off"],sosConfig)
            timelag = BuildOffTimePeriod(pgdb,row["id_off"],sosConfig)
            off.beginPosition = timelag[0]
            off.endPosition = timelag[1]
            off.procedures = BuildOffProcList(pgdb,row["id_off"],sosConfig)
            off.obsProp = BuildOffObsPrList(pgdb,row["id_off"],sosConfig)
            off.fois = BuildOffFoiList(pgdb,row["id_off"],sosConfig)
            self.offerings.append(off)
        

class GetCapabilitiesResponse():
    def __init__(self,fil,pgdb):
        if "all" in fil.sections:
            self.ServiceIdentifier = ServiceIdentification(fil.sosConfig)
            self.ServiceProvider = ServiceProvider(fil.sosConfig)
            self.OperationsMetadata = OperationsMetadata(pgdb,fil.sosConfig)
            self.ObservationOfferingList = ObservationOfferingList(pgdb,fil.sosConfig)
        else:
            if "serviceidentification" in fil.sections:
                self.ServiceIdentifier = ServiceIdentification(fil.sosConfig)
            else:
                self.ServiceIdentifier = []
            if "serviceprovider" in fil.sections:
                self.ServiceProvider = ServiceProvider(fil.sosConfig)
            else:
                self.ServiceProvider = []
            if "operationsmetadata" in fil.sections:
                self.OperationsMetadata = OperationsMetadata(pgdb,fil.sosConfig)
            else:
                self.OperationsMetadata = []
            if "contents" in fil.sections:
                self.ObservationOfferingList = ObservationOfferingList(pgdb,fil.sosConfig)
            else:
                self.ObservationOfferingList = []

    
    
    
