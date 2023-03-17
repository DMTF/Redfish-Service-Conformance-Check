# Copyright Notice:
# Copyright 2016-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/main/LICENSE.md

#####################################################################################################
# File: rfs_check.py
# Description: Redfish service conformance check tool. This module contains implemented assertions for
#   SUT.These assertions are based on operational checks on Redfish Service to verify that it conforms
#   to the normative statements from the Redfish specification.
#   See assertions in redfish-assertions.xlxs for assertions summary
#
# Verified/operational Python revisions (Windows OS) :
#       2.7.10
#       3.4.3
#
# Initial code released : 01/2016
#   Steve Krig      ~ Intel
#   Fatima Saleem   ~ Intel
#   Priyanka Kumari ~ Texas Tech University
#####################################################################################################

import sys
import re
import rf_utility
import xml.etree.ElementTree as ET
from xml.dom import minidom

# map python 2 vs 3 imports
if (sys.version_info < (3, 0)):
    # Python 2
    Python3 = False
    from urlparse import urlparse
    from StringIO import StringIO
    from httplib import HTTPSConnection, HTTPConnection, HTTPResponse
    import urllib
    import urllib2
    from urllib import urlopen
else:
    # Python 3
    Python3 = True
    from urllib.parse import urlparse
    from io import StringIO
    from http.client import HTTPSConnection, HTTPConnection, HTTPResponse
    from urllib.request import urlopen
    import urllib

import ssl
import re
import json
import argparse
import base64
import datetime
import types
import socket
import select
import os
from collections import OrderedDict
import time

# current spec followed for these assertions
REDFISH_SPEC_VERSION = "Version 1.0.2"

#####################################################################################################
# Name: CacheURI 
# Description: Cache a few random URI's in order to speed up the tool 
#####################################################################################################
cached_uri = None
cached_uri_no_member = None
def cacheURI(self):
    global cached_uri
    global cached_uri_no_member
    cached_uri = self.uris
    cached_uri_no_member = self.uris_no_members

#todo: check 7.x via json schemas aswell where applicable..
###################################################################################################
# Name: Assertion_7_0_1(self, log) :Data Model                                             
# Assertion text: 
#   1. Each resource shall be strongly typed according to a resource type definition (basically in
#   EntityType elements with Name and Basetype if any, thats what we are looking for)
#      (should we verify the format?: namespace.v(ersion if any).typename
#   2. The type shall be defined in a Redfish schema document (verify against the namespace identified)  
#   should we check for all relative uris?           
###################################################################################################
def Assertion_7_0_1(self, log):
    log.AssertionID = '7.0.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris # contains all the urls found in every navigation property of all schemas

    for rf_schema in csdl_schema_model.RedfishSchemas:
        #start from resource
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            for entity_type in r_namespace.EntityTypes:
                if entity_type.BaseType:
                    # call function to verify if basetype is strongly typed that is the type is defined in the schemas 
                    namespace_found, typename_found = csdl_schema_model.verify_resource_basetype(entity_type.BaseType)
                    if not typename_found:
                        assertion_status = log.FAIL
                        log.assertion_log('line', "Resource %s, Basetype %s is not strongly typed as expected" % (entity_type.Name, entity_type.BaseType))  # instead of this just add it in the dictionary of errors to be printed later              

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion_7_0_1

###################################################################################################
# Name: Assertion_7_2_1(self, log)  Type Identifiers in JSON                                
# Assertion text: 
#  Types used within a JSON payload shall be defined in, or referenced, by the metadata document. 
#  metadata document is the document retreived from $metadata 
#  Method: 1. DEFINED IN: Parse @odata.type according to format Namespace.Typename.. Verify 
#             Namespace against Include element in #metadata, then within the Schema File referenced 
#             for the Namespace matched in $metadata, we verify the Typename. 
#     TODO 2. REFERENCED BY: If a Namespace is not found in $metadata, we go through each Url 
#             referenced in the $metadata and try to find it within the References element of each
#             schema file.
###################################################################################################
def Assertion_7_2_1(self, log):
    log.AssertionID = '7.2.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris # contains all the urls found in every navigation property of all schemas
    
    for relative_uri in cached_uri:
        json_payload, headers, status = self.http_cached_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = rf_utility.parse_odata_type(json_payload['@odata.type'])
                if namespace and typename:
                    if self.metadata_document_structure:
                        # we already have a metadata document mapped out in metadata_document_structure for this service in rf_utility
                        type_found = csdl_schema_model.verify_resource_metadata_reference(namespace, typename, self.metadata_document_structure)
                        if not type_found:
                            assertion_status = log.FAIL
                            log.assertion_log('line', "Type used within json payload for resource: %s, '@odata.type': %s is not defined in or referenced by the service's $metadata document: %s as expected" % (relative_uris[relative_uri], json_payload['@odata.type'], self.Redfish_URIs['Service_Metadata_Doc']))  
                    else:
                        assertion_status = log.WARN   
                        log.assertion_log('line', 'Service $metadata document %s not found for namespace %s' % ((self.Redfish_URIs['Service_Metadata_Doc']),namespace))

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 7.2.1

def camel(s):
    return (s != s.lower() and s != s.upper())

###################################################################################################
# Name: Assertion_7_3_0(self, log)                                                
# Assertion text: 
#   Resource Name, Property Names and constants such as Enumerations shall be Pascal-cased
#   The first letter of each work shall be upper case with spaces between words shall be removed                
###################################################################################################
def Assertion_7_3_0(self, log):
 
    log.AssertionID = '7.3.0'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    rq_headers = self.request_headers()
    authorization = 'on'
    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris # contains all the urls found in every navigation property of all schemas
    
    for relative_uri in cached_uri:
        json_payload, headers, status = self.http_cached_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = rf_utility.parse_odata_type(json_payload['@odata.type'])
                if namespace and typename:
                    if self.metadata_document_structure:
                        status = camel(namespace)
                        status_1 = camel(typename)
                        if ( status == True and status_1 == True):
                            assertion_status = log.PASS
                        else :
                            assertion_status = log.FAIL
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 7_3_0

###################################################################################################
# Name: Assertion_7_5_2(self, log)  Schema Documents                                                
# Assertion text: 
#   The outer element of the OData Schema representation document shall be the Edmx element, and shall 
#   have a 'Version' attribute with a value of "4.0".    
###################################################################################################
def Assertion_7_5_2(self, log):
    log.AssertionID = '7.5.2'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    csdl_schema_model = self.csdl_schema_model

    for schema in csdl_schema_model.FullRedfishSchemas:
        if csdl_schema_model.map_element_to_csdlnamespace('Edmx') != schema.edmx:
            assertion_status = log.FAIL
            log.assertion_log('line', "~ The outer element of the OData Schema representation document %s is not the Edmx element, instead found %s" % (schema.SchemaUri, schema.edmx))
        if schema.Version is None:
            assertion_status = log.FAIL
            log.assertion_log('line', "~ The outer Edmx element of the OData Schema representation document %s does not have a 'Version' attribute" % schema.SchemaUri)
        elif schema.Version != '4.0':
            assertion_status = log.FAIL
            log.assertion_log('line', "~ The outer Edmx element of the OData Schema representation document %s does not have a value of '4.0' in the 'Version' attribute, instead found %s" % (schema.SchemaUri, schema.Version))

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_5_2

###################################################################################################
# Name: Assertion_7_5_3(self, log)  Resource Type Definitions                                                
# Assertion text: 
# All resources shall include Description and LongDescription annotations i.e EntityTypes under Schema
###################################################################################################
def Assertion_7_5_3(self, log):
    log.AssertionID = '7.5.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            entity_types = r_namespace.EntityTypes
            for entity_type in entity_types:
                if not csdl_schema_model.verify_annotation_recur(entity_type,'OData.Description'): #should alias be prepended or should this be independent of Alias?
                   assertion_status = log.FAIL
                   log.assertion_log('line', "~ Resource: %s, BaseType: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.Description' in its OData schema representation document: %s" % (entity_type.Name, entity_type.BaseType, rf_schema.SchemaUri))
                if not csdl_schema_model.verify_annotation_recur(entity_type,'OData.LongDescription'): #should alias be prepended or should this be independent of Alias?
                   assertion_status = log.FAIL
                   log.assertion_log('line', "~ Resource: %s, BaseType: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.LongDescription' in its OData schema representation document: %s" % (entity_type.Name, entity_type.BaseType, rf_schema.SchemaUri))   

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_5_3


###################################################################################################
# Name: Assertion_7_5_4(self, log)  Resource Properties                                                
# Assertion text: 
# Property names in the Request and Response JSON Payload shall match the casing of the value of the Name attribute
###################################################################################################
def Assertion_7_5_4(self, log):
    log.AssertionID = '7.5.4'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    resource = 'Chassis'
    rq_headers = self.request_headers()
    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?
    for relative_uri in cached_uri:
        if resource in relative_uri:
                json_payload, headers, status = self.http_cached_GET(relative_uris[relative_uri], rq_headers, authorization)
                if status == 200:
                    if 'ChassisType' in json_payload :
                            json_payload['Chassistype'] = json_payload['ChassisType']
                            del json_payload['ChassisType']
                            print ('The json value is now %s' %json_payload)
                            assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
                             # manage assertion status
                            assertion_status = log.status_fixup(assertion_status,assertion_status_)
                            if assertion_status_ != log.PASS: 
                                    continue
                            elif not json_payload:
                                    assertion_status_ = log.WARN
                            else:
                                if '@odata.type' in json_payload:
                                            namespace, typename = rf_utility.parse_odata_type(json_payload['@odata.type'])
                                            namespace = resource + '_v1'
                                            if namespace and typename:
                                                # TODO: rf_utility.get_resource_xml_metadata() is missing
                                                xml_metadata, schema_file = rf_utility.get_resource_xml_metadata(namespace, self.xml_directory)
                                                if xml_metadata and schema_file:
                                                    print ('The xml_metadata is %s' %xml_metadata)                                      
                                                    properties = xml_metadata.getElementsByTagName('Property')[0]
                                                    print ('Properties is %s' %properties)
                                                    if(properties.getAttribute('Name') == 'Chassistype'):
                                                        assertion_status = log.FAIL
                                                        print('Property names in the Request and Response JSON Payload is matching even when the casing of the value does not match')                                                                                                     
                                                    else :
                                                            assertion_status = log.PASS
                                                            continue
                    else :
                        continue
                else :
                    print('Not a valid URI, go to another URI')
                    continue
    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_5_4

###################################################################################################
# Name: Assertion_7_5_5(self, log)  Resource Properties                                                
# Assertion text: 
# All properties shall include Description and LongDescription annotations.  Checking all
# Property types : Property (within EntityType and ComplexType)
###################################################################################################
def Assertion_7_5_5(self, log):
    log.AssertionID = '7.5.5'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    ns_tag = 'Property'
    find_ns_tag = ['Annotation']

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            for entity_type in r_namespace.EntityTypes:
                for prop in entity_type.Properties:
                    if not csdl_schema_model.verify_annotation_recur(prop,'OData.Description'): #should alias be prepended or should this be independent of Alias?
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ Property: %s, Type: %s and any of its parent Type resources (based on inheritance) does not have annotation 'OData.Description' in its OData schema representation document: %s" % (prop.Name, prop.Type, rf_schema.SchemaUri))
                    if not csdl_schema_model.verify_annotation_recur(prop,'OData.LongDescription'): #should alias be prepended or should this be independent of Alias?
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ Property: %s, Type: %s and any of its parent Type resources (based on inheritance) does not have annotation 'OData.LongDescription' in its OData schema representation document: %s" % (prop.Name, prop.Type, rf_schema.SchemaUri))   

            for complextype in r_namespace.ComplexTypes:
                for prop in complextype.Properties:
                    if not csdl_schema_model.verify_annotation_recur(prop,'OData.Description'): #should alias be prepended or should this be independent of Alias?
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ Property: %s, Type: %s and any of its parent Type resources (based on inheritance) does not have annotation 'OData.Description' in its OData schema representation document: %s" % (prop.Name, prop.Type, rf_schema.SchemaUri))
                    if not csdl_schema_model.verify_annotation_recur(prop,'OData.LongDescription'): #should alias be prepended or should this be independent of Alias?
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ Property: %s, Type: %s and any of its parent Type resources (based on inheritance) does not have annotation 'OData.LongDescription' in its OData schema representation document: %s" % (prop.Name, prop.Type, rf_schema.SchemaUri))   

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_5_5

####################################################################################################################
# Name: Assertion_7_5_6(self, log)  Resource Properties                                                
# Assertion text: 
# Properties that are read-only are annotated with the Permissions annotation with a value of ODataPermissions/Read
#####################################################################################################################

def Assertion_7_5_6(self, log):
    log.AssertionID = '7.5.6'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    ns_tag = 'Property'
    find_ns_tag = ['Annotation']

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            for entity_type in r_namespace.EntityTypes:
                for prop in entity_type.Properties:
                    if csdl_schema_model.verify_annotation_recur(prop,'OData.Permission/Read'): #should alias be prepended or should this be independent of Alias?
                        log.assertion_log('line', "~ Property: %s, Type: %s and any of its parent Type resources (based on inheritance) does  have annotation 'OData.Permission/Read' in its OData schema representation document which is read-only: %s" % (prop.Name, prop.Type, rf_schema.SchemaUri))

            for complextype in r_namespace.ComplexTypes:
                for prop in complextype.Properties:
                    if csdl_schema_model.verify_annotation_recur(prop,'OData.Permission/Read'): #should alias be prepended or should this be independent of Alias?
                        log.assertion_log('line', "~ Property: %s, Type: %s and any of its parent Type resources (based on inheritance) does have annotation 'OData.Permission/Read' in its OData schema representation document which is read-only: %s" % (prop.Name, prop.Type, rf_schema.SchemaUri))

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_5_6

##############################################################################################################
# Name: Assertion_7_5_7(self, log)  Resource Properties                                                
# Assertion text: 
# Properties that are required to be implemented by all services are annotated with the required annotation.
###############################################################################################################

def Assertion_7_5_7(self, log):
    log.AssertionID = '7.5.7'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    ns_tag = 'Property'
    find_ns_tag = ['Annotation']

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            for entity_type in r_namespace.EntityTypes:
                for prop in entity_type.Properties:
                    if csdl_schema_model.verify_annotation_recur(prop,'Redfish.Required'): #should alias be prepended or should this be independent of Alias?
                        log.assertion_log('line', "~ Property: %s, Type: %s and any of its parent Type resources (based on inheritance) does  have annotation 'Redfish.Required' in its OData schema representation document which is a required property: %s" % (prop.Name, prop.Type, rf_schema.SchemaUri))

            for complextype in r_namespace.ComplexTypes:
                for prop in complextype.Properties:
                    if csdl_schema_model.verify_annotation_recur(prop,'Redfish.Required'): #should alias be prepended or should this be independent of Alias?
                        log.assertion_log('line', "~ Property: %s, Type: %s and any of its parent Type resources (based on inheritance) does have annotation 'Redfish.Required' in its OData schema representation document which is a required property: %s" % (prop.Name, prop.Type, rf_schema.SchemaUri))

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_5_7

###################################################################################################
# Name: Assertion_7_5_8(self, log)  Resource Properties                                                
# Assertion text: 
# Structured types shall include Description and LongDescription annotations. i.e ComplexTypes 
###################################################################################################
def Assertion_7_5_8(self, log):
    log.AssertionID = '7.5.8'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    resource = []
    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            print('Namespace is %s' %r_namespace.Namespace)
            complextypes = r_namespace.ComplexTypes
            for complextype in complextypes:
                print('Complextype is %s' %complextype.Annotations)
                if not csdl_schema_model.verify_annotation_recur(complextype,'OData.Description'): #should alias be prepended or should this be independent of Alias?
                   assertion_status = log.FAIL
                   print('The namespace %s has Complex type but does not include OData.Description' %r_namespace.Namespace)
                   resource.append(r_namespace.Namespace)
                   log.assertion_log('line', "~ ComplexType: %s, BaseType: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.Description' in its OData schema representation document: %s" % (complextype.Name, complextype.BaseType, rf_schema.SchemaUri))
                if not csdl_schema_model.verify_annotation_recur(complextype,'OData.LongDescription'): #should alias be prepended or should this be independent of Alias?
                   assertion_status = log.FAIL
                   print('The namespace %s has Complex type but does not include OData.LongDescription' %r_namespace.Namespace)
                   if r_namespace.Namespace not in resource:
                       resource.append(r_namespace.Namespace)
                   log.assertion_log('line', "~ ComplexType: %s, BaseType: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.LongDescription' in its OData schema representation document: %s" % (complextype.Name, complextype.BaseType, rf_schema.SchemaUri))   
    while resource:
        print('The list of namespaces that do not have the required annotations are %s' % resource.pop())
    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_5_8

###################################################################################################
# Name: Assertion_7_5_9(self, log)  Enums                                              
# Assertion text: 
# Enumeration Types shall include Description and LongDescription annotations.
###################################################################################################
def Assertion_7_5_9(self, log):
    log.AssertionID = '7.5.9'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            enum_types = r_namespace.EnumTypes
            for enum_type in enum_types:
                if not csdl_schema_model.verify_annotation(enum_type,'OData.Description'): #should alias be prepended or should this be independent of Alias?
                   assertion_status = log.FAIL
                   log.assertion_log('line', "~ EnumType: %s within Schema Namespace: %s does not have annotation 'OData.Description' in its OData schema representation document: %s" % (enum_type.Name, r_namespace.Namespace, rf_schema.SchemaUri))
                if not csdl_schema_model.verify_annotation(enum_type, 'OData.LongDescription'): #should alias be prepended or should this be independent of Alias?
                   assertion_status = log.FAIL
                   log.assertion_log('line', "~ EnumType: %s within Schema Namespace: %s does not have annotation 'OData.LongDescription' in its OData schema representation document: %s" % (enum_type.Name, r_namespace.Namespace, rf_schema.SchemaUri))   

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_5_9
###################################################################################################
# Name: Assertion_7_5_10(self, log)  Enums                                              
# Assertion text: 
# Enumeration Members shall include Description annotations.
###################################################################################################
def Assertion_7_5_10(self, log):
    log.AssertionID = '7.5.10'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    
    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            enum_types = r_namespace.EnumTypes
            for enum_type in enum_types:
                for member in enum_type.Members:
                    if not csdl_schema_model.verify_annotation(member, 'OData.Description'): #should alias be prepended or should this be independent of Alias?
                       assertion_status = log.FAIL
                       log.assertion_log('line', "~ Member: %s of EnumType: %s does not have annotation 'OData.Description' in its OData schema representation document: %s" % (member.Name, enum_type.Name, rf_schema.SchemaUri))             

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_5_10

###################################################################################################
# Name: check_addprop_annotation()
#   This function checks for additional properties annotation within a resource type
#   and based on 
###################################################################################################
def find_addprop_annotation(self, xtype):
    additional_property = self.csdl_schema_model.get_annotation(xtype, 'OData.AdditionalProperties')
    if additional_property:
        if additional_property.AttrValue:
            if additional_property.AttrValue == 'False':
                return False
    return True

###################################################################################################
# Name: get_resource_additionalprop():
# returns any addtional properties found in payload
###################################################################################################
def get_resource_additionalprop(self, json_payload, xtype, namespace = None):
    # AdditionalProperties is False, we dont need to do the following...
    for key in json_payload:
        # first check if its in the common properties list
        if key in self.csdl_schema_model.CommonRedfishResourceProperties:
            continue
        # need to ignore @odata properties
        elif '@odata' in key:
            continue
        # not an odata property, nor a common property, it should be in this resource's defined properties (if inheritence use recur)
        elif self.csdl_schema_model.verify_property_in_resource_recur(xtype, key, namespace):
            continue                                         
        #this could potentially be the additional property
        return key 

    return None

###################################################################################################
# Name: Assertion_7_4_11(self, log)  Additional Properties  - checked via xml metadata                                     
# Assertion text: 
# The AdditionalProperties annotation term is used to specify whether a type can contain additional 
# properties outside of those defined. Types annotated with the AdditionalProperties annotation with 
# a Boolean attribute with a value of "False", must not contain additional properties.
# applies to EntityTypes and ComplexType Annotations
# Reference: https://tools.oasis-open.org/version-control/browse/wsvn/odata/trunk/spec/vocabularies/Org.OData.Core.V1.xml
# specification unclear. Description for AdditionalProperties states : 
# String="Instances of this type may contain properties in addition to those declared in $metadata", 
# does it mean the context url of the resource?
###################################################################################################
def _Assertion_7_4_11(self, log):
    log.AssertionID = '7.4.11'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in cached_uri:
        json_payload, headers, status = self.http_cached_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = csdl_schema_model.get_resource_namespace_typename(json_payload['@odata.type'])
                if namespace and typename:
                    if not find_addprop_annotation(self, typename):
                        # AdditionalProperties is False, if it were True, we dont need to do the following...
                        property_key = get_resource_additionalprop(self, json_payload, typename, namespace)
                        if property_key: 
                            assertion_status = log.FAIL
                            log.assertion_log('line', "~ Resource: %s has EntityType: %s with Annotation 'AdditionalProperty' set to False in its schema document %s, but additional property: %s found in resource payload" % (json_payload['@odata.id'], typename.Name, namespace.SchemaUri, property_key))  
                                     
                    '''     
                    for complextype in namespace.ComplexTypes:
                        if not find_addprop_annotation(self, complextype):
                            # complextype name and some simple property name could be the same, (example Actions, Links found in serviceroot.xml and computersystem.xml).. make sure its a complextype key in payload.
                            if complextype.Name in json_payload.keys() and isinstance(json_payload[complextype.Name], dict):
                                sub_payload = json_payload[complextype.Name]
                                #find complextype.name and properties within that
                                property_key = get_resource_additionalprop(self, sub_payload, complextype)
                                if property_key:                                         
                                    assertion_status = log.FAIL
                                    log.assertion_log('line', "~ Resource: %s has ComplexType: %s with Annotation 'AdditionalProperty' set to False in its schema document %s, but an additional property: %s found in resource payload" % (json_payload['@odata.id'], complextype.Name, namespace.SchemaUri, property_key))                                      
                                   
                    '''
    log.assertion_log(assertion_status, None)
    return (assertion_status)

###################################################################################################
# verify_typename_in_json_metadata(typename, json_metadata):
# verifies if typename exists in resources json schema document. Search for it under 'definitions'
###################################################################################################
def verify_typename_in_json_metadata(typename, json_metadata):
    if 'definitions' in json_metadata:
        if json_metadata['definitions']:
            if typename in json_metadata['definitions']:
                return True
    return False
           
###################################################################################################
# Name: Assertion_7_5_11(self, log)  Additional Properties   - checked via json metadata                                        
# Assertion text: 
# The AdditionalProperties annotation term is used to specify whether a type can contain additional 
# properties outside of those defined. Types annotated with the AdditionalProperties annotation with 
# a Boolean attribute with a value of "False", must not contain additional properties.
# applies to EntityTypes and ComplexType Annotations
# Reference: https://tools.oasis-open.org/version-control/browse/wsvn/odata/trunk/spec/vocabularies/Org.OData.Core.V1.xml
# specification unclear. Description for AdditionalProperties states : 
# String="Instances of this type may contain properties in addition to those declared in $metadata", 
# does it mean the context url of the resource?
###################################################################################################
def Assertion_7_5_11(self, log):
    log.AssertionID = '7.5.11'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    #camelcased? need to verify this...
    annotation_term = 'additionalProperties'

    for relative_uri in cached_uri:
        json_payload, headers, status = self.http_cached_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = rf_utility.parse_odata_type(json_payload['@odata.type'])
                if namespace and typename:
                    json_metadata, schema_file = rf_utility.get_resource_json_metadata(namespace, self.json_directory)     
                    if json_metadata and schema_file:           
                        if verify_typename_in_json_metadata(typename, json_metadata):
                            if annotation_term in json_metadata['definitions'][typename]:
                                if not json_metadata['definitions'][typename][annotation_term]:
                                    # if value is False then check if there are any additional properties, which it shouldnt
                                    if 'properties' in json_metadata['definitions'][typename]:
                                        regex = None
                                        # get and compile the 'patternProperties' regex if present
                                        if 'patternProperties' in json_metadata['definitions'][typename]:
                                            prop = json_metadata['definitions'][typename]['patternProperties']
                                            if isinstance(prop, dict) and len(list(prop)) == 1:
                                                pattern = list(prop)[0]
                                                try:
                                                    regex = re.compile(pattern)
                                                except Exception as e:
                                                    print('Exception while compiling regex pattern "{}" from schema file {}; Exception is: "{}"'
                                                          .format(pattern, schema_file, e))
                                        # check the properties in the payload against the schema
                                        for property_key in json_payload:
                                            if "@odata.etag" in property_key or\
                                               "@odata.nextLink" in property_key:
                                                # Skip etag properties as these may be appended to the resource
                                                # by the service, according to section 6.5.4.4 of v1.2.0 of the spec
                                                #
                                                # Also skipping @odata.nextLink properties as these are allowed on 
                                                # resource colelctions that are paged, but are not currently in the schema
                                                continue

                                            if regex is not None:
                                                # If property matches patternProperties regex, it is good
                                                if regex.match(property_key):
                                                    continue

                                            if property_key not in json_metadata['definitions'][typename]['properties']:
                                                assertion_status = log.FAIL
                                                log.assertion_log('line', "~ Resource: %s of type: %s has Annotation: '%s' set to 'False' in its schema document %s, but additional property: %s found in resource payload" % (json_payload['@odata.id'], namespace, annotation_term, schema_file, property_key))  
    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_5_11

###################################################################################################
# check_required_property_in_payload()
#   This function checks the payload for a required 'Property' key 
###################################################################################################
def check_required_property_in_payload(required_property, property_name, json_payload):
    if not required_property.AttrValue or required_property.AttrValue != 'false':
        #check payload, must have it
        for key in json_payload:
            if key == property_name:
                return True
        return False

###################################################################################################
# Name: Assertion_7_4_13(self, log)  Required Properties    - checked via xml schema                                
# Assertion text: 
# If an implementation supports a property, it shall always provide a value for that property.
# If a value is unknown, then null is an acceptable values in most cases. 
# required is True by default, so unless it is a False, it should be in the payload with a value or null
###################################################################################################
def _Assertion_7_4_13(self, log):
    log.AssertionID = '7.4.13'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in cached_uri:
        json_payload, headers, status = self.http_cached_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = csdl_schema_model.get_resource_namespace_typename(json_payload['@odata.type'])
                if namespace and typename:
                    #structural property
                    for property in typename.Properties:
                        required_property = csdl_schema_model.get_annotation(property, 'Redfish.Required')
                        if required_property:
                            if not check_required_property_in_payload(required_property, property.Name, json_payload):
                                assertion_status = log.FAIL
                                log.assertion_log('line', "Resource %s contains a Property %s which has Annotation 'Redfish.Required' set to 'True' but property not found in its resource payload %s" % (typename.Name, property.Name, json_payload['@odata.id']))
                  
                    #reference property
                    for navproperty in typename.NavigationProperties:
                        required_property = csdl_schema_model.get_annotation(navproperty, 'Redfish.Required')
                        if required_property:
                            if not check_required_property_in_payload(required_property, navproperty.Name, json_payload):
                                assertion_status = log.FAIL
                                log.assertion_log('line', "Resource %s contains a Navigation Property %s which has Annotation 'Redfish.Required' set to 'True' but property not found in its resource payload %s" % (typename.Name, property.Name, json_payload['@odata.id']))
                  
    log.assertion_log(assertion_status, None)
    return (assertion_status)

###################################################################################################
# Name: _Assertion_7_5_14(self, log)  Required Properties   - checked via json schema                                 
# Assertion text: 
# If an implementation supports a property, it shall always provide a value for that property.
# If a value is unknown, then null is an acceptable values in most cases. 
# required is True by default, so unless it is a False, it should be in the payload with a value or null
###################################################################################################
def Assertion_7_5_14(self, log):
    log.AssertionID = '7.5.14'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    annotation_term = 'required'

    for relative_uri in cached_uri:
        json_payload, headers, status = self.http_cached_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = rf_utility.parse_odata_type(json_payload['@odata.type'])
                if namespace and typename:
                    json_metadata, schema_file = rf_utility.get_resource_json_metadata(namespace, self.json_directory)     
                    if json_metadata and schema_file:           
                        if verify_typename_in_json_metadata(typename, json_metadata):
                            if annotation_term in json_metadata['definitions'][typename]:
                                for req_prop in json_metadata['definitions'][typename][annotation_term]:                                       
                                    if req_prop not in json_payload.keys():
                                        assertion_status = log.FAIL
                                        log.assertion_log('line', "~ Resource: %s of type: %s has Annotation: '\%s'\ for property: %s in its schema document %s, but property not found in resource payload" % (json_payload['@odata.id'], namespace, annotation_term, req_prop, schema_file))                     
    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_5_14


###################################################################################################
# Name: _Assertion_7_5_14_1(self, log)  Required Properties                                 
# Assertion text: 
# Properties not returned from a GET operation shall indicate that the property is not currently supported by the 
# implementation
###################################################################################################
def Assertion_7_5_14_1(self, log):
    log.AssertionID = '7.5.14.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    annotation_term = 'required'
    supported_term = 'the property is not currently supported'
    for relative_uri in cached_uri:
        json_payload, headers, status = self.http_cached_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = rf_utility.parse_odata_type(json_payload['@odata.type'])
                if namespace and typename:
                    json_metadata, schema_file = rf_utility.get_resource_json_metadata(namespace, self.json_directory)     
                    if json_metadata and schema_file:           
                        if verify_typename_in_json_metadata(typename, json_metadata):
                            if annotation_term in json_metadata['definitions'][typename]:
                                for req_prop in json_metadata['definitions'][typename][annotation_term]:                                       
                                    if req_prop not in json_payload.keys():
                                        if supported_term not in headers:
                                            assertion_status = log.FAIL
                                            log.assertion_log('line', "~ Resource: %s of type: %s has Annotation: '\%s'\ for property: %s in its schema document %s, but property not found in resource payload and is not indicated that the property is not supported by the implementation" % (json_payload['@odata.id'], namespace, annotation_term, req_prop, schema_file))                     
    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_5_14_1


###################################################################################################
# check_property_in_payload()
#   This function check the payload for a non-nullable property
###################################################################################################
def check_property_in_payload(property, json_payload):
    for key in json_payload:
        if key == property.Name:
            #value cant be null
            if json_payload[key] is None:
                return False
    return True

###################################################################################################
# Name: Assertion_7_5_13_xml(self, log)  Required Properties  - checked via xml schema                                     
# Description: 
# Assertion text: required property shall be annotated with Nullable = False
# cannot contain null values, (not necc to have the property in the payload?)
###################################################################################################
def Assertion_7_5_13_xml(self, log):
    log.AssertionID = '7.5.13'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in cached_uri:
        json_payload, headers, status = self.http_cached_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = csdl_schema_model.get_resource_namespace_typename(json_payload['@odata.type'])
                if namespace and typename:
                    #structural property
                    for property in typename.Properties:
                        if property.Nullable == 'false':
                            #check if the payload contains the key and its value
                            if not check_property_in_payload(property, json_payload):
                                assertion_status = log.FAIL
                                log.assertion_log('line', "Resource %s contains a Property: %s which has Annotation 'Nullable' set to 'false' but property's value is null in its resource urls payload %s" % (typename.Name, property.Name, relative_uris[relative_uri]))
                                
                    for navproperty in typename.NavigationProperties:
                        if navproperty.Nullable == 'false':
                            #check if the payload contains the key and its value
                            if not check_property_in_payload(navproperty, json_payload):
                                assertion_status = log.FAIL
                                log.assertion_log('line', "Resource %s contains a Navigation Property: %s which has Annotation 'Nullable' set to 'false' but property's value is null in its resource urls payload %s" % (typename.Name, navproperty.Name, relative_uris[relative_uri]))

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_5_13_xml


###################################################################################################
# Name: Assertion_7_5_13(self, log)  Required Properties       - check via json schema                                
# Description: 
# Assertion text: required property shall be annotated with Nullable = False
# cannot contain null values, (not necc to have the property in the payload?)
###################################################################################################
def _Assertion_7_5_13(self, log):
    log.AssertionID = '7.5.13'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    annotation_term = 'required'
    nullable_term = 'nullable'

    for relative_uri in cached_uri:
        json_payload, headers, status = self.http_cached_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            if '@odata.type' in json_payload:
                namespace, typename = rf_utility.parse_odata_type(json_payload['@odata.type'])
                if namespace and typename:
                    json_metadata, schema_file = rf_utility.get_resource_json_metadata(namespace, self.json_directory)     
                    if json_metadata and schema_file:           
                        if verify_typename_in_json_metadata(typename, json_metadata):
                            if annotation_term in json_metadata['definitions'][typename] and 'properties' in json_metadata['definitions'][typename]:
                                for req_prop in json_metadata['definitions'][typename][annotation_term]:                                       
                                    if req_prop in json_payload.keys():
                                        if nullable_term in json_metadata['definitions'][typename]['properties'][req_prop]:
                                            if not json_metadata['definitions'][typename]['properties'][req_prop][nullable_term]:
                                                if not json_payload[req_prop]:
                                                    assertion_status = log.FAIL
                                                    log.assertion_log('line', "~ Resource: %s of type: %s has Annotation: '\%s'\: %s for property: %s in its schema document %s, but value for property not found in resource payload" % (json_payload['@odata.id'], namespace, nullable_term, json_metadata['definitions'][typename]['properties'][req_prop][nullable_term], req_prop, schema_file))                     
    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_5_13
###################################################################################################
# check_unit_instance(xtype, schema, namespace, log) WIP
# This helper function checks Redfish schema Annotation 'Measures.Unit' type. It should follow the 
# naming convention provided in ucum-essence.xml TODO parse ucum-essence to match the value 
###################################################################################################
def check_unit_instance(xtype, schema, namespace, log):
    if xtype.AttrKey:
        if xtype.AttrKey != 'String':
            assertion_status = log.FAIL
            log.assertion_log('line', "~ Property 'Measures.Unit': %s within Schema Namespace: %s in resource file %s is not of type string as required by the Redfish specification document %s" % (xtype.AttrKey, namespace.Namespace, schema.SchemaUri, REDFISH_SPEC_VERSION))   
        if xtype.AttrValue:
            if not isinstance(xtype.AttrValue, str):
                assertion_status = log.FAIL
                log.assertion_log('line', "~ The value of Property 'Measures.Unit': %s: %s within Schema Namespace: %s in resource file %s is not of type string as required by the Redfish specification document %s" % (xtype.AttrKey, xtype.AttrValue, namespace.Namespace, schema.SchemaUri, REDFISH_SPEC_VERSION))   
                     
###################################################################################################
# Name: Assertion_7_5_15(self, log) Units of Measure                               
# Assertion text: 
# In addition to following naming conventions, properties representing units of measure 
# shall be annotated with the Units annotation term in order to specify the units of measurement for 
# the property. check for annotation term 'Measures.Unit'
###################################################################################################
def Assertion_7_5_15(self, log):
    log.AssertionID = '7.5.15'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        #start with namespace
        for r_namespace in resource_namespaces:
            #check EntityType
            for entity_type in r_namespace.EntityTypes:
                unit = csdl_schema_model.get_annotation(entity_type, 'Measures.Unit')
                if unit:
                    check_unit_instance(unit, rf_schema, r_namespace, log)
                #check Property within EntityType
                for property in entity_type.Properties:
                    unit = csdl_schema_model.get_annotation(property, 'Measures.Unit')
                    if unit:
                        check_unit_instance(unit, rf_schema, r_namespace, log)
                #check NavigationProperty within EntityType
                for nav_property in entity_type.NavigationProperties:
                    unit = csdl_schema_model.get_annotation(nav_property, 'Measures.Unit')
                    if unit:
                        check_unit_instance(unit, rf_schema, r_namespace, log)

            #check ComplexType
            for complextype in r_namespace.ComplexTypes:
                unit = csdl_schema_model.get_annotation(complextype, 'Measures.Unit')
                if unit:
                    check_unit_instance(unit, rf_schema, r_namespace, log)
                #check Property within ComplexType
                for property in complextype.Properties:
                    unit = csdl_schema_model.get_annotation(property, 'Measures.Unit')
                    if unit:
                        check_unit_instance(unit, rf_schema, r_namespace, log)
                #check NavigationProperty within ComplexType
                for nav_property in complextype.NavigationProperties:
                    unit = csdl_schema_model.get_annotation(nav_property, 'Measures.Unit')
                    if unit:
                        check_unit_instance(unit, rf_schema, r_namespace, log)
                                                 
            #check Enumtype               
            for enum_type in r_namespace.EnumTypes:
                unit = csdl_schema_model.get_annotation(enum_type, 'Measures.Unit')
                if unit:
                    check_unit_instance(unit, rf_schema, r_namespace, log)
                #check Member within EnumType
                for member in enum_type.Members:
                    unit = csdl_schema_model.get_annotation(member, 'Measures.Unit')
                    if unit:
                        check_unit_instance(unit, rf_schema, r_namespace, log)

            #check Action       
            for action in r_namespace.Actions:
                unit = csdl_schema_model.get_annotation(action, 'Measures.Unit')
                if unit:
                    check_unit_instance(unit, rf_schema, r_namespace, log)


    log.assertion_log(assertion_status, None)
    return (assertion_status)
## end Assertion 7_5_15

###################################################################################################
# Name: Assertion_7_5_16(self, log) Reference Properties                                
# Assertion text: 
# All reference properties shall include Description and LongDescription annotations.
# NavigationProperty within EntityType and ComplexType
###################################################################################################
def Assertion_7_5_16(self, log):
    log.AssertionID = '7.5.16'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        for r_namespace in resource_namespaces:
            entity_types = r_namespace.EntityTypes
            complextypes = r_namespace.ComplexTypes
            for entity_type in entity_types:
                for nav_prop in entity_type.NavigationProperties:
                    if not csdl_schema_model.verify_annotation_recur(nav_prop,'OData.Description'): 
                       assertion_status = log.FAIL
                       log.assertion_log('line', "~ NavigationProperty: %s, Type: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.Description' in its OData schema representation document: %s" % (nav_prop.Name, nav_prop.Type, rf_schema.SchemaUri))
                    if not csdl_schema_model.verify_annotation_recur(nav_prop,'OData.LongDescription'): 
                       assertion_status = log.FAIL
                       log.assertion_log('line', "~ NavigationProperty: %s, Type: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.LongDescription' in its OData schema representation document: %s" % (nav_prop.Name, nav_prop.Type, rf_schema.SchemaUri))   
            for complextype in complextypes:
                for nav_prop in complextype.NavigationProperties:
                    if not csdl_schema_model.verify_annotation_recur(nav_prop,'OData.Description'): 
                       assertion_status = log.FAIL
                       log.assertion_log('line', "~ NavigationProperty: %s, Type: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.Description' in its OData schema representation document: %s" % (nav_prop.Name, nav_prop.Type, rf_schema.SchemaUri))
                    if not csdl_schema_model.verify_annotation_recur(nav_prop,'OData.LongDescription'): 
                       assertion_status = log.FAIL
                       log.assertion_log('line', "~ NavigationProperty: %s, Type: %s and any of its parent BaseType resources (based on inheritance) does not have annotation 'OData.LongDescription' in its OData schema representation document: %s" % (nav_prop.Name, nav_prop.Type, rf_schema.SchemaUri))   

    log.assertion_log(assertion_status, None)
    return (assertion_status)
    ## end Assertion 7_5_16

###################################################################################################
# Name: Assertion_7_5_18(self, log) Oem Property Format and Content   WIP                         
# Assertion text: 
# OEM-specified objects that are contained within the Oem property must be 
# valid JSON objects that follow the format of a Redfishcomplex type. 
###################################################################################################
def Assertion_7_5_18(self, log):
    log.AssertionID = '7.4.18'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in cached_uri:
        json_payload, headers, status = self.http_cached_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            #look for Oem property, we have loaded it from json object so we already know its a json object
            if 'Oem' in json_payload:
                #find a property 
                #should follow complextype, should contain a dictionary and within that expect a key with dictionary as value
                # complextypes have properties and navigationproperties
                if not isinstance(json_payload['Oem'], dict):
                    assertion_status = log.FAIL
                    log.assertion_log('line',"~ Expected a dictionary as to satist complextype format which contains properties and navigational properties within the resource object " % (relative_uri, status) )
                else:
                    #this key is the name of the object, expected to have properties and navigational(reference) properties
                    for key in json_payload['Oem']:
                        if not isinstance(json_payload['Oem'][key], dict):
                            assertion_status = log.FAIL
                            log.assertion_log('line',"~ " % (relative_uri, status) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)

#end Assertion_7_5_18

###################################################################################################
# Name: Assertion_7_5_18_1(self, log) Oem Property Format and Content  WIP                            
# Assertion text: 
# OEM-specified objects... The name of the object (property) shall uniquely identify 
# the OEM or organization that manages the top of the namespace under which the property is defined.
###################################################################################################
def Assertion_7_5_18_1(self, log):
    log.AssertionID = '7.5.18.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in cached_uri:
        json_payload, headers, status = self.http_cached_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            #look for Oem property, we have loaded it from json object so we already know its a json object
            if 'Oem' in json_payload:
                #find a property 
                #should follow complextype, should contain a dictionary and within that expect a key with dictionary as value
                # complextypes have properties and navigationproperties
                if not isinstance(json_payload['Oem'], dict):
                    assertion_status = log.FAIL
                    log.assertion_log('line',"~ " % (relative_uri, status) )
                else:
                    #this key is the name of the object so 1 key?, expected to have properties and navigational properties
                    for key in json_payload['Oem']:
                        if not isinstance(json_payload['Oem'][key], dict):
                            assertion_status = log.FAIL
                            log.assertion_log('line',"~ " % (relative_uri, status) )
                            
                        break

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#end Assertion_7_5_18_1

###################################################################################################
# Name: Assertion_7_5_18_2(self, log) Oem Property Format and Content WIP                             
# Assertion text: 
# The OEM-specified property shall also include a type property that provides
# the location of the schema and the type definition for the property within that schema. 
###################################################################################################
def Assertion_7_5_18_2(self, log):
    log.AssertionID = '7.5.18.2'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in cached_uri:
        json_payload, headers, status = self.http_cached_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            #look for Oem property, we have loaded it from json object so we already know its a json object
            if 'Oem' in json_payload:
                #find a property 
                if not isinstance(json_payload['Oem'], dict):
                    assertion_status = log.FAIL
                    log.assertion_log('line',"~ " % (relative_uri, status) )
                else:
                    for key in json_payload['Oem']:
                        if not isinstance(json_payload['Oem'][key], dict):
                            assertion_status = log.FAIL
                            log.assertion_log('line',"~ " % (relative_uri, status) )
                        else:                            
                            if '@odata.type' not in json_payload['Oem'][key]:
                                assertion_status = log.FAIL
                                log.assertion_log('line',"~ " % (relative_uri, status) )

                            else: # contains namespace and typename
                                namespace, typename = csdl_schema_model.get_resource_namespace_typename(json_payload['Oem'][key]['@odata.type'])
                                if not namespace and not typename:
                                    assertion_status = log.FAIL
                                    log.assertion_log('line',"~ " % (relative_uri, status) )


    log.assertion_log(assertion_status, None)
    return (assertion_status)

#end Assertion_7_5_18_2

###################################################################################################
# check_name_instance(xtype, schema, log)
# This helper function checks Redfish schema property 'Name''s type. It should be a string 
###################################################################################################
def check_name_instance(xtype, schema, log):
    if xtype.Name:
        if not isinstance(xtype.Name, str):
            assertion_status = log.FAIL
            log.assertion_log('line', "~ Property 'Name': %s in resource file %s is not of type string as required by the Redfish specification document version: %s" % (xtype.Name, schema.SchemaUri, REDFISH_SPEC_VERSION))   

###################################################################################################
# Name: Assertion_7_6_2(self, log)  Description
# Description: 
#
# Assertion text: 
#   The Name property is used to convey a human readable moniter for a resource.  The type of the Name 
#   property shall be string.  The value of Name is NOT required to be unique across resource instances
#   within a collection.
# checking EntityTypes under Schema
###################################################################################################
# TODO: Is this supposed to be Assertion_7_5_1_2()?
"""
def Assertion_7_6_2(self, log):
    log.AssertionID = '7.6.2'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        #start with namespace
        for r_namespace in resource_namespaces:
            #check EntityType
            for entity_type in r_namespace.EntityTypes:
                check_name_instance(entity_type, rf_schema, log)
                #check Property within EntityType
                for property in entity_type.Properties:
                    check_name_instance(property, rf_schema, log)
                #check NavigationProperty within EntityType
                for nav_property in entity_type.NavigationProperties:
                    check_name_instance(nav_property, rf_schema, log)

            #check completype
            for complextype in r_namespace.ComplexTypes:
                check_name_instance(complextype, rf_schema, log)
                #check Property within ComplexType
                for property in complextype.Properties:
                   check_name_instance(property, rf_schema, log)
                #check NavigationProperty within ComplexType
                for nav_property in complextype.NavigationProperties:
                    check_name_instance(nav_property, rf_schema, log)

            #check Enumtype           
            for enum_type in r_namespace.EnumTypes:
                check_name_instance(enum_type, rf_schema, log)
                #check Member within EnumType
                for member in enum_type.Members:
                   check_name_instance(member, rf_schema, log)
                     
            #check Action
            for action in r_namespace.Actions:
               check_name_instance(action, rf_schema, log)
               #check parameter within Action
               for parameter in action.Parameters:
                    check_name_instance(parameter, rf_schema, log)

    log.assertion_log(assertion_status, None)
    return (assertion_status)
"""
## end Assertion 7_6_2

###################################################################################################
# check_description_instance(xtype, schema, namespace, log)
#  This helper function just checked if annotaion term 'Description' has a property named 'String' 
#  and the value of this property should be a String type value aswell
###################################################################################################
def check_description_instance(xtype, schema, namespace, log):
    if xtype.AttrKey:
        if xtype.AttrKey != 'String':
            assertion_status = log.FAIL
            log.assertion_log('line', "~ Property 'Description': %s within Schema Namespace: %s in resource file %s is not of type string as required by the Redfish specification document %s" % (xtype.AttrKey, namespace.Namespace, schema.SchemaUri, REDFISH_SPEC_VERSION))   
        if xtype.AttrValue:
            if not isinstance(xtype.AttrValue, str):
                assertion_status = log.FAIL
                log.assertion_log('line', "~ The value of Property 'Description': %s: %s within Schema Namespace: %s in resource file %s is not of type string as required by the Redfish specification document %s" % (xtype.AttrKey, xtype.AttrValue, namespace.Namespace, schema.SchemaUri, REDFISH_SPEC_VERSION))   
                                              
###################################################################################################
# Name: Assertion_7_5_1_3(self, log)  Description                                                
# Assertion text: 
# The Description property is used to convey a human readable description of the resource. The type
# of the Description property shall be string. checking EntityTypes under Schema
###################################################################################################
def Assertion_7_5_1_3(self, log):
    log.AssertionID = '7.5.1.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    csdl_schema_model = self.csdl_schema_model
    #find alias in Include first?
    for rf_schema in csdl_schema_model.RedfishSchemas:
        resource_namespaces = rf_schema.Schemas
        #start with namespace
        for r_namespace in resource_namespaces:
            #check EntityType
            for entity_type in r_namespace.EntityTypes:
                description = csdl_schema_model.get_annotation_recur(entity_type, 'OData.Description')
                if description:
                    check_description_instance(description, rf_schema, r_namespace, log)
                #check Property within EntityType
                for property in entity_type.Properties:
                    description = csdl_schema_model.get_annotation_recur(property, 'OData.Description')
                    if description:
                        check_description_instance(description, rf_schema, r_namespace, log)
                #check NavigationProperty within EntityType
                for nav_property in entity_type.NavigationProperties:
                    description = csdl_schema_model.get_annotation_recur(nav_property, 'OData.Description')
                    if description:
                        check_description_instance(description, rf_schema, r_namespace, log)

            #check ComplexType
            for complextype in r_namespace.ComplexTypes:
                description = csdl_schema_model.get_annotation_recur(complextype, 'OData.Description')
                if description:
                    check_description_instance(description, rf_schema, r_namespace, log)
                #check Property within ComplexType
                for property in complextype.Properties:
                    description = csdl_schema_model.get_annotation_recur(property, 'OData.Description')
                    if description:
                        check_description_instance(description, rf_schema, r_namespace, log)
                #check NavigationProperty within ComplexType
                for nav_property in complextype.NavigationProperties:
                    description = csdl_schema_model.get_annotation_recur(nav_property, 'OData.Description')
                    if description:
                        check_description_instance(description, rf_schema, r_namespace, log) 
                                                 
            #check Enumtype               
            for enum_type in r_namespace.EnumTypes:
                description = csdl_schema_model.get_annotation_recur(enum_type, 'OData.Description')
                if description:
                    check_description_instance(description, rf_schema, r_namespace, log)  
                #check Member within EnumType
                for member in enum_type.Members:
                    description = csdl_schema_model.get_annotation_recur(member, 'OData.Description')
                    if description:
                        check_description_instance(description, rf_schema, r_namespace, log) 

            #check Action       
            for action in r_namespace.Actions:
                description = csdl_schema_model.get_annotation_recur(action, 'OData.Description')
                if description:
                    check_description_instance(description, rf_schema, r_namespace, log)   


    log.assertion_log(assertion_status, None)
    return (assertion_status)
## end Assertion 7_5_1_3

###################################################################################################
# Name: Assertion_7_6_1(self, log)  Id                                              
# Assertion text: 
# The Id property of a resource uniquely identifies the resource within the Resource Collection that contains
# it. The value of Id shall be unique across a Resource Collection.
###################################################################################################
def Assertion_7_6_1(self, log):
    log.AssertionID = '7.6.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    rq_headers = self.request_headers()
    uri = 'http://redfish.dmtf.org/schemas/v1/Resource_v1.xml'
    flag = False

    rq_headers['Content-Type'] = rf_utility.content_type['xml']
    response = urlopen(uri)
    myfile = response.read()
    myfile = myfile.decode('utf-8')
    print('The response is %s' %myfile)
    doc = minidom.parseString(myfile)
    type_definition = doc.getElementsByTagName('TypeDefinition')
    for t in type_definition:
            name = t.getAttribute('Name')
            if 'Id' in name:
                  flag = True
            else :
                  continue

    if flag :
        assertion_status = log.PASS
    else :
        assertion_status = log.FAIL

    log.assertion_log(assertion_status, None)
    return (assertion_status)
## end Assertion 7_6_1


###################################################################################################
# Name: Assertion_7_6_2(self, log)  Name                                              
# Assertion text: 
# The Name property is used to convey a human readable moniker for a resource.  
# The type of the Name property shall be string.  The value of Name is NOT required to be unique across resource instances
# within a collection.
###################################################################################################
def Assertion_7_6_2(self, log):
    log.AssertionID = '7.6.2'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    rq_headers = self.request_headers()
    uri = 'http://redfish.dmtf.org/schemas/v1/Resource_v1.xml'
    flag = False

    rq_headers['Content-Type'] = rf_utility.content_type['xml']
    response = urlopen(uri)
    myfile = response.read()
    myfile = myfile.decode('utf-8')
    print('The response is %s' %myfile)
    doc = minidom.parseString(myfile)
    type_definition = doc.getElementsByTagName('TypeDefinition')
    for t in type_definition:
            name = t.getAttribute('Name')
            if 'Name' in name:
                  flag = True
            else :
                  continue

    if flag :
        assertion_status = log.PASS
    else :
        assertion_status = log.FAIL

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_6_2



###################################################################################################
# Name: Assertion_7_6_3(self, log)  Description                                              
# Assertion text: 
# The Description property is used to convey a human readable description of the resource.  
# The type of the Description property shall be string.
###################################################################################################
def Assertion_7_6_3(self, log):
    log.AssertionID = '7.6.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    rq_headers = self.request_headers()
    uri = 'http://redfish.dmtf.org/schemas/v1/Resource_v1.xml'
    flag = False

    rq_headers['Content-Type'] = rf_utility.content_type['xml']
    response = urlopen(uri)
    myfile = response.read()
    myfile = myfile.decode('utf-8')
    print('The response is %s' %myfile)
    doc = minidom.parseString(myfile)
    type_definition = doc.getElementsByTagName('TypeDefinition')
    for t in type_definition:
            name = t.getAttribute('Name')
            if 'Description' in name:
                  flag = True
            else :
                  continue

    if flag :
        assertion_status = log.PASS
    else :
        assertion_status = log.FAIL

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_6_3


###################################################################################################
# Name: Assertion_7_6_5_1(self, log)  Links                                              
# Assertion text: 
#  All associated reference properties defined for a resource shall be nested under the links property.  
###################################################################################################
def Assertion_7_6_5_1(self, log):
    log.AssertionID = '7.6.5.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    rq_headers = self.request_headers()
    uri = 'http://redfish.dmtf.org/schemas/v1/Resource_v1.xml'
    flag = False

    rq_headers['Content-Type'] = rf_utility.content_type['xml']
    response = urlopen(uri)
    myfile = response.read()
    myfile = myfile.decode('utf-8')
    print('The response is %s' %myfile)
    doc = minidom.parseString(myfile)
    type_definition = doc.getElementsByTagName('ComplexType')
    for t in type_definition:
            name = t.getAttribute('Name')
            if 'Links' in name:
                  flag = True
            else :
                  continue

    if flag :
        assertion_status = log.PASS
    else :
        assertion_status = log.FAIL

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion 7_6_5_1




###################################################################################################
# run(self, log):
# Takes sut obj and logger obj 
###################################################################################################
def run(self, log):
    #Section 7
    assertion_status = Assertion_7_6_1(self, log)
    assertion_status = Assertion_7_0_1(self, log)
    assertion_status = Assertion_7_2_1(self, log)
    assertion_status = Assertion_7_3_0(self, log)
    assertion_status = Assertion_7_5_2(self, log)
    assertion_status = Assertion_7_5_3(self, log)
    # Needs a fix: rf_utility.get_resource_xml_metadata() missing
    # assertion_status = Assertion_7_5_4(self, log)
    assertion_status = Assertion_7_5_5(self, log)
    assertion_status = Assertion_7_5_6(self, log)
    assertion_status = Assertion_7_5_7(self, log)
    assertion_status = Assertion_7_5_8(self, log)
    assertion_status = Assertion_7_5_9(self, log)
    assertion_status = Assertion_7_5_10(self, log)      
    assertion_status = Assertion_7_5_11(self, log)          
    # Missing
    # assertion_status = Assertion_7_5_13(self, log)
    assertion_status = Assertion_7_5_13_xml(self, log)
    assertion_status = Assertion_7_5_14(self, log) 
    assertion_status = Assertion_7_5_14_1(self, log)
    assertion_status = Assertion_7_5_15(self, log)
    assertion_status = Assertion_7_5_16(self, log)
    #WIP
    #assertion_status = Assertion_7_5_18(self, log)
    #WIP
    #assertion_status = Assertion_7_5_18_1(self, log)
    #WIP
    #assertion_status = Assertion_7_5_18_2(self, log)
    # Missing
    # assertion_status = Assertion_7_5_1_2(self, log)
    assertion_status = Assertion_7_5_1_3(self, log)  
    assertion_status = Assertion_7_6_1(self, log) 
    assertion_status = Assertion_7_6_2(self, log)
    assertion_status = Assertion_7_6_3(self, log)
    assertion_status = Assertion_7_6_5_1(self, log)
    #assertion_status = Assertion_7_8_1(self, log)
