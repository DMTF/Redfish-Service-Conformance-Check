# Copyright Notice:
# Copyright 2016-2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/LICENSE.md

###################################################################################################
# File: rf_utility.py
#   This module contains Service class with each instance containing information specific to the
#   System Under Test (SUT) and functions related to redfish service and resources available on SUT.
#
# Verified/operational Python revisions (Windows OS) :
#       2.7.10
#       3.4.3
#
# Initial code released : 01/2016
#   Steve Krig      ~ Intel
#   Fatima Saleem   ~ Intel
#   Priyanka Kumari ~ Texas Tech University
###################################################################################################
import sys
from schema import SchemaModel
import rf_utility
from collections import OrderedDict

# map python 2 vs 3 imports
if (sys.version_info < (3, 0)):
    # Python 2
    Python3 = False
    from urlparse import urlparse
    from StringIO import StringIO
    from httplib import HTTPSConnection, HTTPConnection, responses
    import urllib2
    from urllib import URLopener

else:
    # Python 3
    Python3 = True
    from urllib.parse import urlparse
    from io import StringIO, BytesIO
    from http.client import HTTPSConnection, HTTPConnection, responses
    import urllib.request
    from urllib.request import URLopener

import ssl
import json
import argparse
import base64
import warnings
import shutil
from datetime import datetime
import gzip
from xml.etree import ElementTree as ET
import os
import zipfile


###################################################################################################
# Class: SUT                                            
#  This class is a container for all SUT information. Initializes with a dictionary containing
#  basic info the SUT provided in properties.json             
###################################################################################################
class SUT():
    def __init__(self, sut_prop):
        # basic properties of the SUT, it MUST have "DnsName", "LoginName" and "Password" and 
        # "DisplayName". See help.txt for correct format
        self.SUT_prop = sut_prop
        # Redfish defined URIs, this is updated according to the service protocol version retrieved
        # in rf_util.GetProtocol_ODataVersion()
        self.Redfish_URIs = dict()
        self.Redfish_URIs['Protocol_Version'] = '/redfish' 
        self.Redfish_URIs['Service_Root'] = '/redfish/v1/' # default, might be updated according to protocol version
        self.Redfish_URIs['Service_Odata_Doc'] = None
        self.Redfish_URIs['Service_Metadata_Doc'] = None

        # gets service top level entry points from OData Service Doc
        self.sut_toplevel_uris = dict()
        # place holder for relative uris 
        self.relative_uris = OrderedDict()
        # placeholder for relative uris minus resource 'Members'
        self.relative_uris_no_members = OrderedDict()

        #service root uri
        self.service_root = None
        #deafult odata-version 
        self.default_odata_version = '4.0'
        #service protocol version
        self.protocol_version = None
        #odata context in /odata json_payload
        self.metadata_in_odatacontext = None
        # top level links found in service root
        self.serviceroot_toplevel_uris = ''
        # 'value' found in odata doc
        self.odata_values = ''
        # instance of SchemaModel for schema documents is placed here
        self.csdl_schema_model = None
        # instance of SchemaModel for 
        self.metadata_document_structure = None
        # vars to store http response cookies for all assertions
        self.cookie_detail = list()
        self.cookie_info = [False, self.cookie_detail, 0]
        #self.cookie_info = None

        # this gets set on a successful event subscription - Assertion 8.1.3
        # these get used by subsequent event subscription checks/assertions
        self.Assertion8_1_3EventSubscriptionURI = None
        self.Assertion8_1_3EventSubscriptionJSON = None
        self.Assertion8_1_3EventSubscriptionPayload = None
        self.Conformant_evt_rq_body = None
        self.Submit_Test_Event = None

        # Oem key and name will be parsed from the root service json_payload by an early assertion (6.3.1)
        self.SUT_OEM = dict()
        self.SUT_OEM['key'] = None
        self.SUT_OEM['name'] = None

        # directory paths for schema folder, csdl files and json metadata files set for SUT from 
        # rf_client and properties.json
        self.schema_directory = None
        self.csdl_directory = None
        self.json_directory = None
        self.xml_directory = None

    ###############################################################################################
    # Name: self.request_headers()                                                
    #   returns a request header dictionary used globally throughout rfs_check.py thru base
    #   create_request_headers() in rf_utility 
    ###############################################################################################
    def request_headers(self): 
        return rf_utility.create_request_headers()

    ###############################################################################################
    # Name: http_GET(resource_uri, rq_headers, auth_on_off)                                              
    #   Issue a GET request for resource uri thru base HTTP__GET() in rf_utility by passing SUT
    #   HTTP connection properties to it.
    #   Takes resource uri, request header dict, and authorization 'on' or 'off' option
    # Returns:
    #   - Response json_payload dict or string depending on 'content-type' in request header. If
    #       'application/json' then json_payload will be a dict. 
    #   - Response Headers dict: header keys in lower case
    #   - Response Status code: http status code returned from the request                                                 
    ###############################################################################################
    def http_GET(self, resource_uri, rq_headers, auth_on_off) :      
        if (rq_headers == None):
            rq_headers = self.request_headers()
        # issue the GET on the resource...
        return rf_utility.http__GET(self.SUT_prop, resource_uri, rq_headers, auth_on_off, self.cookie_info)
                                                            
    #
    ## end http_GET

    ###############################################################################################
    # Name: http__POST(resource_uri, rq_headers, rq_body, auth_on_off)                                              
    #   Issue a POST request for resource uri thru base HTTP__POST() in rf_utility by passing SUT
    #   HTTP connection properties to it.
    #   Takes resource uri, request header dict, request body and authorization 'on' or 'off' 
    # Returns:
    #   - Response json_payload dict or string depending on 'content-type' in request header. If
    #       'application/json' then json_payload will be a dict. 
    #   - Response Headers dict: header keys in lower case
    #   - Response Status code: http status code returned from the request
    ###############################################################################################
    def http_POST(self, resource_uri, rq_headers, rq_body, auth_on_off) :
        if (rq_headers == None):
            rq_headers = self.request_headers()

        return(rf_utility.http__POST(self.SUT_prop, resource_uri, rq_headers, rq_body, auth_on_off))
    #
    ## end http_POST

    ###############################################################################################
    # Name: http__TRACE(resource_uri, rq_headers, rq_body, auth_on_off)                                              
    #   Issue a TRACE request for resource uri thru base HTTP__TRACE() in rf_utility by passing SUT
    #   HTTP connection properties to it.
    #   Takes resource uri, request header dict, request body and authorization 'on' or 'off' 
    # Returns:
    #   - Response json_payload dict or string depending on 'content-type' in request header. If
    #       'application/json' then json_payload will be a dict. 
    #   - Response Headers dict: header keys in lower case
    #   - Response Status code: http status code returned from the request
    ###############################################################################################
    def http_TRACE(self, resource_uri, rq_headers, rq_body, auth_on_off) :
        if (rq_headers == None):
            rq_headers = self.request_headers()
        return(rf_utility.http__TRACE(self.SUT_prop, resource_uri, rq_headers, rq_body, auth_on_off, self.cookie_info ))
    #
    ## end http_TRACE

    ###############################################################################################
    # Name: http__OPTIONS()                                              
    #   Issue a OPTIONS request for resource uri thru base HTTP__OPTIONS() in rf_utility by passing 
    #   SUT HTTP connection properties to it.
    #   Takes resource uri, request header dict, request body and authorization 'on' or 'off' 
    # Returns:
    #   - Response json_payload dict or string depending on 'content-type' in request header. If
    #       'application/json' then json_payload will be a dict. 
    #   - Response Headers dict: header keys in lower case
    #   - Response Status code: http status code returned from the request
    ###############################################################################################
    def http_OPTIONS(self, resource_uri, rq_headers, rq_body, auth_on_off) :
        if (rq_headers == None):
            rq_headers = self.request_headers()
        return(rf_utility.http__OPTIONS(self.SUT_prop, resource_uri, rq_headers, rq_body, auth_on_off, self.cookie_info ))
    #
    ## end http_OPTIONS

    ###############################################################################################
    # Name: http__PATCH()                                              
    #   Issue a PATCH request for resource uri thru base HTTP__PATCH() in rf_utility by passing SUT
    #   HTTP connection properties to it.
    #   Takes resource uri, request header dict, request body and authorization 'on' or 'off' 
    # Returns:
    #   - Response json_payload dict or string depending on 'content-type' in request header. If
    #       'application/json' then json_payload will be a dict. 
    #   - Response Headers dict: header keys in lower case
    #   - Response Status code: http status code returned from the request      
    ###############################################################################################
    def http_PATCH(self, resource_uri, rq_headers, rq_body, auth_on_off) :
        if (rq_headers == None):
            rq_headers = self.request_headers()
        return(rf_utility.http__PATCH(self.SUT_prop, resource_uri, rq_headers, rq_body, auth_on_off))
    #
    ## end http_PATCH

    ###############################################################################################
    # Name: http__PUT()
    #   Issue a PUT request for resource uri thru base HTTP__PUT() in rf_utility by passing SUT
    #   HTTP connection properties to it.
    #   Takes resource uri, request header dict, request body and authorization 'on' or 'off' 
    # Returns:
    #   - Response json_payload dict or string depending on 'content-type' in request header. If
    #       'application/json' then json_payload will be a dict. 
    #   - Response Headers dict: header keys in lower case
    #   - Response Status code: http status code returned from the request    
    ###############################################################################################
    def http_PUT(self, resource_uri, rq_headers, rq_body, auth_on_off) :
        if (rq_headers == None):
            rq_headers = self.request_headers()
        return(rf_utility.http__PUT(self.SUT_prop, resource_uri, rq_headers, rq_body, auth_on_off))
    #
    ## end http_PUT

    ###############################################################################################
    # Name: http__HEAD()  
    #   Issue a HEAD request for resource uri thru base HTTP__HEAD() in rf_utility by passing SUT
    #   HTTP connection properties to it.
    #   Takes resource uri, request header dict, request body and authorization 'on' or 'off' 
    # Returns:
    #   - Response json_payload dict or string depending on 'content-type' in request header. If
    #       'application/json' then json_payload will be a dict. 
    #   - Response Headers dict: header keys in lower case
    #   - Response Status code: http status code returned from the request                
    ###############################################################################################
    def http_HEAD(self, resource_uri, rq_headers, auth_on_off) :
        if (rq_headers == None):
            rq_headers = self.request_headers()
        return(rf_utility.http__HEAD(self.SUT_prop, resource_uri, rq_headers, auth_on_off, self.cookie_info))
    #
    ## end http_HEAD

    ###############################################################################################
    # Name: http__DELETE()                                              
    #   Issue a DELETE request for resource uri thru base HTTP__DELETE() in rf_utility by passing
    #   SUT HTTP connection properties to it.
    #   Takes resource uri, request header dict and authorization 'on' or 'off' option
    # Returns:
    #   - Response json_payload dict or string depending on 'content-type' in request header. If
    #       'application/json' then json_payload will be a dict. 
    #   - Response Headers dict: header keys in lower case
    #   - Response Status code: http status code returned from the request
    ###############################################################################################
    def http_DELETE(self, resource_uri, rq_headers, auth_on_off) :
        if (rq_headers == None):
            rq_headers = self.request_headers()
        return(rf_utility.http__DELETE(self.SUT_prop, resource_uri, rq_headers, auth_on_off))
    #
    ## end http_DELETE 

    ###############################################################################################
    # Name: set_redfish_defined_uris(service_root)                                          
    #   Takes sut's service root uri and sets the Redfish defined uris in SUT by concatenating them
    #   with the service root
    ###############################################################################################
    def set_redfish_defined_uris(self, service_root):
        self.Redfish_URIs['Service_Root'] = service_root
        self.Redfish_URIs['Service_Odata_Doc'] = service_root + 'odata'
        self.Redfish_URIs['Service_Metadata_Doc'] = service_root + '$metadata'

    ###############################################################################################
    # Name: set_protocol_version(protocol_version)                                          
    #   Takes sut's service protocol version and sets the protocol version in SUT
    ###############################################################################################
    def set_protocol_version(self, protocol_version):
        self.protocol_version = protocol_version

    ###############################################################################################
    # Name: set_odata_context(odata_context)                                          
    #   Takes sut's odata document's @odata.context property and sets the context property in SUT
    ###############################################################################################
    def set_odata_context(self, odata_context):
        self.metadata_in_odatacontext = odata_context

    ###############################################################################################
    # Name: set_odata_values(odata_values)                                             
    #   Takes sut's odata document's 'value' property and sets the value property in SUT 
    ###############################################################################################
    def set_odata_values(self, odata_values):
        self.odata_values = odata_values

    ###############################################################################################
    # Name: set_serviceroot_toplevel_uris(serviceroot_toplevel_uris)                                          
    #   Takes sut's Service Root (/redfish/v1) top-level uris that are exposed by the sut and sets
    #   the top-level uris in SUT
    ###############################################################################################
    def set_serviceroot_toplevel_uris(self, serviceroot_toplevel_uris):
        self.serviceroot_toplevel_uris = serviceroot_toplevel_uris

    ###############################################################################################
    # Name: set_sut_toplevel_uris(odata_values, serviceroot_toplevel_uris)                                          
    #   Takes sut's odata document 'value' property and service root's toplevel uris and sets the
    #   top level uris in SUT.  
    ###############################################################################################
    def set_sut_toplevel_uris(self, top_level_uris):
        self.sut_toplevel_uris = top_level_uris

    ###############################################################################################
    # Name: set_metadata_document_structure(self, metadata_document_structure)                                          
    #   Takes sut's metadata document's in schema_model object and sets it in SUT.  
    ###############################################################################################
    def set_metadata_document_structure(self, metadata_document_structure):
        self.metadata_document_structure = metadata_document_structure

    ###############################################################################################
    # Name: set_event_params(self, Conformant_evt_rq_body, Submit_Test_Event)                                          
    #   Takes event parameters from properties.json and set it to use with this SUT  
    ###############################################################################################
    def set_event_params(self, Conformant_evt_rq_body, Submit_Test_Event):
        self.Conformant_evt_rq_body = Conformant_evt_rq_body
        self.Submit_Test_Event = Submit_Test_Event

    ###############################################################################################
    # Name: parse_protocol_version(protocol_version_url)                                          
    #   Get of /redfish returns the protocol version Any resource discovered through this link shall
    #   conform to the same version of the protocol supported by root service.
    # Return:
    #   body with version as key and root service uri as value {'v1' : '/redfish/v1/'}         
    ###############################################################################################
    def parse_protocol_version(self, protocol_version_url):
        protocol_version = ''
        service_root = ''

        rq_headers = self.request_headers()
        authorization = 'off'
        try:
            json_payload, headers, status = self.http_GET(protocol_version_url, rq_headers, authorization)
            if not (json_payload and headers and status):
                return None, None
            elif (status != rf_utility.HTTP_OK):
                print("~ GET for resource %s failed: FAIL (HTTP status %s)" % (protocol_version_url, status)) 
      
            elif isinstance(json_payload, dict)and isinstance(headers, dict):
                for version, service_root in json_payload.items():
                    protocol_version = version
                    service_root = service_root

            return protocol_version, service_root
        except:
            print('%s could not be retreived due to operational errors.' % (protocol_version_url))
            
        return protocol_version, service_root
    ###############################################################################################
    # Name: parse_serviceroot_toplevel_uris(service_root):                                               
    #   Takes Service root uri, performs GET on it and walk the response body to get all root links     
    # Returns:
    #   dictionary of top level links - Updated by Priyanka
    ###############################################################################################
    def parse_serviceroot_toplevel_uris(self, service_root):
        rq_headers = self.request_headers()
        authorization = 'off'
        #get service's rest/v1/ json_payload 
        json_payload, headers, status = self.http_GET(service_root, rq_headers, authorization)
        if not (json_payload and headers and status):
            return None
        elif (status != rf_utility.HTTP_OK):
            print('line', "~ GET for resource %s failed: FAIL (HTTP status %s)" % (service_root, status)) 
        else:
            base_rootservice_links = {\
            'Systems' : '',\
            'Chassis' : '',\
            'Managers' : '',\
            'TaskService' : '',\
            'AccountService' : '',\
            'SessionService' : '',\
            'EventService' : '',\
            'Registries' : '',\
            'JsonSchemas' : '',\
            'Links' : ''
            }

            toplevel_uris =  dict()
            for key in base_rootservice_links.keys() :
                try :
                    if key == 'Links':
                        for subkey in json_payload[key]:
                            toplevel_uris[subkey] = (json_payload[key])[subkey]['@odata.id']
                    else:
                        toplevel_uris[key] = (json_payload[key])['@odata.id']
                except :
                    #assertion_status = log.WARN
                    #log.assertion_log('line', "~ rf.WARN: \'%s\' not found in json_payload returned from GET %s" % (key, self.Redfish_URIs['Service_Root']))
                    continue

        return toplevel_uris

    ###############################################################################################
    # Name: parse_odatadoc_payload(service_odata_uri):                                             
    #   Takes odata document uri and parses the response body from service odata document to get 
    #   odata context and value 
    # Returns:
    #   string for 'odata.context' and dictionary of 'values' which contains top level uris     
    ###############################################################################################
    def parse_odatadoc_payload(self, service_odata_uri):       
        rq_headers = self.request_headers()
        authorization = 'off'
        values = dict()
        odata_context = ''

        json_payload, headers, status = self.http_GET(service_odata_uri, rq_headers, authorization)
        if not (json_payload and headers and status):
            return None, None
        elif (status != rf_utility.HTTP_OK):
            print("~ GET for resource %s failed: FAIL (HTTP status %s)" % (service_odata_uri, status))

        elif isinstance(json_payload, dict):
            if '@odata.context' in json_payload:
                odata_context = json_payload['@odata.context']
            else:
                print('Warning: OData Service Spec object does not comply with the Specification. @odata.context expected but not found in %s json_payload' % (service_odata_uri))

            try:
                #following dictionary keys are traced out by Redfish specification
                if 'value' in json_payload:
                    for resource in json_payload['value']:
                        values[resource['name']] = {'kind' : resource['kind'], 'url' : resource['url']} 
            except:
                print('Warning: OData Service Spec object does not comply with the Specification')
                return None, None
                
        return odata_context, values

    ################################################################################################
    # Name: parse_metadata_document(metadata_uri, log = None)                                         
    #   Take $metadata uri and performs GET on it and serializes it in schemamodel object, optional
    #   log file
    # Returns:
    #   Serialized metadata document object of type SchemaModel
    ###############################################################################################
    def parse_metadata_document(self, metadata_uri, log = None):
        # init SchemaModel obj
        csdl_schema_model = SchemaModel()
        rq_headers = self.request_headers()
        authorization = 'off'
        #get service's $metadata json_payload 
        json_payload, headers, status = self.http_GET(metadata_uri, rq_headers, authorization)
        if not (headers and status):
            return None
        elif (status != rf_utility.HTTP_OK):
            print('line', "~ GET for resource %s failed: FAIL (HTTP status %s)" % (metadata_uri, status)) 
        elif json_payload:  
            csdl_schema_model.serialize_schema(schema_payload = json_payload, schema_uri= metadata_uri)
            # there will be only one element in this case ans we only need that
            if csdl_schema_model.FullRedfishSchemas[0]:
                return csdl_schema_model.FullRedfishSchemas[0]
            return None

    ###############################################################################################
    # Name: collect_relative_resources(service_root)
    #   Takes service root uri and  triggers the recursive function process_uri starting with 
    #   the service root to retrieve all the @odata.ids from the json_payload of each resource
    ###############################################################################################
    def collect_relative_uris(self, service_root):
        #start with rest/v1/
        self.relative_uris['Root Service'] = service_root
        self.relative_uris_no_members['Root Service'] = service_root
        self.process_uri(service_root, 'Root Service')

    ###############################################################################################
    # Name: process_uri(url, nested_key = None)
    #   Takes a resource uri and an optional nested key for resource record in relative_uris based 
    #   on resource name/level. It performs a GET on it, each key of the json_payload is either mapped
    #   to a dict or list if it contains '@odata.id', it retrieves the '@odata.id' by processing 
    #   the dictionary or list recursively
    ###############################################################################################
    def process_uri(self, url, nested_key = None):
        rq_headers = self.request_headers()      
        json_payload, headers, status = self.http_GET(url, rq_headers, 'on')
        if not (headers and status):
            return
        elif (status != rf_utility.HTTP_OK) :
            ('line', "~ GET %s : FAIL (HTTP status %s)" % (url, status))
        elif json_payload:
            for key in json_payload:
                if 'Oem' in key or 'JsonSchemas' in key: #pass all oems for now or add them to another list
                    continue
                if isinstance(json_payload[key], dict):
                    if nested_key:
                        nested_key_ = nested_key + '_' + key
                    else:
                        nested_key_ = key
                    result = self.process_dict(json_payload[key], nested_key_)
                    for url_, nested_key_ in result:
                        skip = False
                        # make sure urls not already been traversed, if so skip it
                        for relative_uri in self.relative_uris.values():
                            if url_ == relative_uri:
                                skip = True
                                break
                        if not skip:
                            self.relative_uris[nested_key_] = url_
                            self.relative_uris_no_members[nested_key_] = url_
                            print('%s :%s' % (nested_key_, url_))
                            self.process_uri(url_, nested_key_)


                elif isinstance(json_payload[key], list):
                    if nested_key:
                        nested_key_ = nested_key + '_' + key
                    else:
                        nested_key_ = key
                    url = self.process_list(json_payload[key], nested_key_)
                    count = 0
                    for url_, nested_key_ in url:
                        skip = False
                        # make sure urls not already been traversed, if so skip it
                        for relative_uri in self.relative_uris.values():
                            if url_ == relative_uri:
                                skip = True
                                break
                        if not skip:
                            count+=1
                            nested_key__ = nested_key_ + '_' + str(count)                       
                            self.relative_uris[nested_key__] = url_
                            print('%s :%s' % (nested_key__, url_))
                            self.process_uri(url_, nested_key__)      
                               

    ###############################################################################################
    # Name: process_dict(json_payload, nested_key)
    #   Takes json json_payload of a resource, searches base condition: a '@odata.id' within json_payload that
    #   has a dictionary value. If the json_payload key is mapped to another dictionary, it recursively 
    #   calls itself till it finds the base condition. If condtion is met, it yields the value of 
    #   '@odata.id' and nested key for resource record in relative_uris based on resource name/level.
    ###############################################################################################
    def process_dict(self, json_payload, nested_key):  
        for dict_key in json_payload:
            if '@odata.id' in json_payload and not isinstance(json_payload[dict_key], dict):
                url = json_payload['@odata.id']
                yield url, nested_key
                
            elif isinstance(json_payload[dict_key], dict):
                nested_key_ = nested_key + '_' + dict_key               
                result = self.process_dict(json_payload[dict_key], nested_key_)
                for url, nested_key_ in result:
                    yield url, nested_key_

            '''
            elif isinstance(json_payload[dict_key], list):
                result = self.process_list(json_payload[dict_key], nested_key)
                for url, nested_key_ in result:
                    # no need to process these links
                    self.relative_uris2[nested_key_] = url
                    print('key: %s :%s' % (nested_key_, url))
                '''

    ###############################################################################################
    # Name: process_list(json_payload, nested_key)
    #   Takes json json_payload of a resource, searches base condition: yield if '@odata.id' found within
    #   the list. If the json_payload item is mapped to a dictionary it calls process_dict. If condtion is 
    #   met, it yields the value of '@odata.id' and nested key for resource record in relative_uris 
    #   based on resource name/level.
    ###############################################################################################            
    def process_list(self, json_payload, nested_key):
        for list_key in json_payload:
            if '@odata.id' in list_key:                                    
                yield list_key['@odata.id'], nested_key
                
            elif isinstance(list_key, dict):               
                result = self.process_dict(list_key, nested_key)
                for url, nested_key_ in result:
                    yield url, nested_key_     
      
    ###############################################################################################
    # Name: allowable_method(method, headers)  
    #   Takes a method name, resource response headers. It searches for 'allow' header key checks 
    #   if method is available in the header key
    # Retrun:
    #   True if method found, else False               
    ###############################################################################################
    def allowable_method(self, method, headers):
        if headers:
            if 'allow' in headers:
                if method in headers['allow']:
                    return True
        return False    
       
    ###############################################################################################
    # Name: get_resource_members(uri = None, rq_headers = None, json_payload = None)                                                 
    #   Takes a resource uri or json_payload, optionally request header to find 'Members' in 
    #   json_payload and perform a GET on each memebr resource using id.
    #   Yield:
    #     json_payload, headers on member resource                
    ###############################################################################################
    def get_resource_members(self, uri = None, rq_headers = None, json_payload = None):
        authorization = 'on'
        if uri != None:
            if rq_headers == None:
                rq_headers = self.request_headers()
            #get a response json_payload from GET on the link for a response header, then iterate through the json_payload for member uris 
            json_payload, headers, status = self.http_GET(uri, rq_headers, authorization)
            if not (json_payload and headers and status):
                yield None, None
            elif (status != rf_utility.HTTP_OK):
                print("- GET member resource %s : FAIL (HTTP status: %s)" % (uri, status) )
            elif json_payload:
                #property name = 'Members' as mapped out by Redfish 1.01  
                if 'Members' in json_payload:
                    # iterate 
                    for member in json_payload['Members']:
                        mem_payload, headers, status = self.http_GET(member['@odata.id'], rq_headers, authorization)
                        if not (mem_payload and headers and status):
                            continue
                        elif (status != rf_utility.HTTP_OK):
                            continue
                            #print( "- GET %s : FAIL (HTTP status: %s)" % (member['@odata.id'], status) )                        
                        else:
                            yield mem_payload, headers


    #####################################################################################################
    # Name: response_status_check(resource_uri, response_status, log, expected_status = None, request_type = 'GET')
    #   Takes resource uri, response status, log instance and optionally an expected status and a 
    #   request stype string (GET, POST etc) and verifies response status against that. 
    #   By default it checks against HTTP OK status and default request type is 'GET'  
    #####################################################################################################
    def response_status_check(self, resource_uri, response_status, log, expected_status = None, request_type = 'GET'):
        assertion_status = log.PASS

        if not response_status:
            asseertion_status = log.WARN
        else:
            if expected_status:
           # http_ok and not found are acceptable status in most cases, anything else is generally a warning unless handled in individiual assertion as a failure
                if (response_status != expected_status and response_status != rf_utility.HTTP_NOT_FOUND) :
                    assertion_status = log.FAIL
                    try:
                        log.assertion_log('line', "~ %s:%s failed : HTTP status %s:%s, Expected status %s:%s" % (request_type, resource_uri, response_status, rf_utility.HTTP_status_string(response_status), expected_status, rf_utility.HTTP_status_string(expected_status)))
                    except:
                        log.assertion_log('line', "~ %s:%s failed : HTTP status %s, Expected status %s" % (request_type, resource_uri, response_status, expected_status))
            elif (response_status != rf_utility.HTTP_OK and response_status != rf_utility.HTTP_NOT_FOUND) :
                    assertion_status = log.FAIL
                    try:
                        log.assertion_log('line', "~ %s:%s failed : HTTP status %s:%s, Expected status %s:%s" % (request_type, resource_uri, response_status, rf_utility.HTTP_status_string(response_status), rf_utility.HTTP_OK, rf_utility.HTTP_status_string(rf_utility.HTTP_OK)))
                    except:
                        log.assertion_log('line', "~ %s:%s failed : HTTP status %s, Expected status %s" % (request_type, resource_uri, response_status, rf_utility.HTTP_OK))
                    # if the url is not found, then log it as a subtle warning (if an assertion passes as the result of all urls not found, there should be atleast some info) 
                    #TODO add a diff log status for such case or do a sanity check for all urls at the start of the tool before running assertions)
            if response_status == rf_utility.HTTP_NOT_FOUND:
                assertion_status = log.INCOMPLETE
                log.assertion_log('TX_COMMENT',"WARN: %s:%s failed : HTTP status %s:%s" % (request_type , resource_uri, response_status, rf_utility.HTTP_status_string(response_status)) )
        
        return assertion_status
    


    
    ###############################################################################################
    # Name: GetSchemaVersion():  WIP                                           
    # Description:  
    #   Takes $metadata document uri to parse and does a check on resource url to retreive the 
    #   appropriate schema version the current service uses. (use $metadata in SchemaModel object)
    ###############################################################################################
    def GetSchemaVersion(self, metadata_uri):
        rq_headers = self.request_headers()
        authorization = 'on'

        json_payload, headers, status = self.http_GET(metadata_uri, rq_headers, authorization)
        if not (json_payload and headers and status):
            return None
        elif (status != rf_utility.HTTP_OK):
            print("~ GET for resource %s failed: FAIL (HTTP status %s)" % (metadata_uri, status))




     
