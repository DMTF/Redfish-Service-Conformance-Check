# Copyright Notice:
# Copyright 2016-2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/LICENSE.md

#####################################################################################################
# File: rfs_check.py
# Description: Redfish service conformance check tool. This module contains implemented Section 6
#   assertions for SUT.These assertions are based on operational checks on Redfish Service to verify
#   that it conforms to the normative statements from the Redfish specification.
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
# Priyanka- making changes here to access schema files in import sys-adding from schema and from collections 
import sys
from schema import SchemaModel
from collections import OrderedDict
from xml.dom import minidom
import re
import rf_utility
import datetime
import xml.etree.ElementTree as ET
import urllib

# map python 2 vs 3 imports
if (sys.version_info < (3, 0)):
    # Python 2
    Python3 = False
    from urlparse import urlparse
    from StringIO import StringIO
    from httplib import HTTPSConnection, HTTPConnection, HTTPResponse
    import urllib
    import urllib2
else:
    # Python 3
    Python3 = True
    from urllib.parse import urlparse
    from io import StringIO
    from http.client import HTTPSConnection, HTTPConnection, HTTPResponse
    from urllib.request import urlopen


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

REDFISH_SPEC_VERSION = "Version 1.0.5"

#####################################################################################################
# Name: Assertion_1_2_3(self, log)                                               
# Description:  This is General Assertion Template for writing assertion code             
#####################################################################################################
def Assertion_1_2_3(self, log) : # self here is service's instance..
    #set id in log object, this should be same as the excel 
    log.AssertionID = '1.2.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    # authorization ~ this controls whether an HTTP request contains an authorization
    # header or not -~ this can be set to 'on' or 'off' ~ if its 'off' then no
    authorization = 'on'

    ## Assertion verification logic goes here...

    #sample intermediate log string going to the text logfile and the xlxs file
    log.assertion_log('line', "~ GET %s" % self.Redfish_URIs['Protocol_Version'])
    #sample intermediate log string to text logfile
    log.assertion_log('TX_COMMENT', "~ GET %s" % self.Redfish_URIs['Protocol_Version'])
 
    #Note: any assertion which FAILs or WARNs should place an explanation in the the reporting spreadsheet
    #be careful with volume of text here ~ needs to fit in a spreadsheet cell..
    if (assertion_status != log.PASS):
        # this text will go only into the comment section of the xlxs assertion run spreadsheet
        log.assertion_log('XL_COMMENT', ('~ GET %s : %s %s' % (self.Redfish_URIs['Protocol_Version'], assertion_status, "a meaningful failure note")) )          
               
    ## log completion status
    log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion 1.2.3

#####################################################################################################
# Name: Assertion_6_1_8_2(self, log)                                               
# Description:     
#   GET:  Object or Collection retrieval               
#####################################################################################################
def Assertion_6_1_8_2(self, log) :
 
    log.AssertionID = '6.1.8.2'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    # get SUTs relative uris dictionary
    relative_uris = self.relative_uris

    authorization = 'on'
    rq_headers = self.request_headers()
    
    # loop for each uri in relative uris dict
    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)             
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)

    log.assertion_log(assertion_status, None)

    return (assertion_status)
#
## end Assertion 6.1.8.2

##
    # these next 3 assertions should be run in series ~ create/cleanup a new user account...
    # ...POST/create a new user account
    # ...PATCH/update the new user account -~ this assertion expects that a user acct for 'testuser' has been previosly created..
    # ...DELETE the new user account
    #
    ## 
#####################################################################################################
# Name: Assertion_6_1_8_1(self, log)                                               
# Description:     
#   POST: Object create, Object action, Eventing
# Spec: 
# The service shall set the Location header to the URI of the newly created resource.   
# The response to a successful create request should be 201 (Created) and may include
# a response body containing the "representation of the newly created resource".		                                             
# For POST request body see requiredOnCreate annotation in schemas
# TODO try a sample post, patch and delete for every resource that allows the methods, run it in series
#####################################################################################################
def Assertion_6_1_8_1(self, log) :
 
    log.AssertionID = '6.1.8.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    user_name = 'xxuserxx'
    root_link_key = 'SessionService'

    sample = dict()

    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris[root_link_key]['url'], rq_headers, authorization)
        assertion_status_ = self.response_status_check(self.sut_toplevel_uris[root_link_key]['url'], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status, assertion_status_)
        if assertion_status_ != log.PASS:                 
            pass
        elif not json_payload: 
            assertion_status = log.WARN
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (self.sut_toplevel_uris[root_link_key]['url']))
        else:              
            ## get Accounts collection from payload
            try :
                key = 'Sessions'
                acc_collection = (json_payload[key])['@odata.id']
            except :
                assertion_status = log.WARN
                log.assertion_log('line', "~ \'Sessions\' not found in the payload from GET %s" % (self.sut_toplevel_uris[root_link_key]['url']))    
            else:          
                json_payload, headers, status = self.http_GET(acc_collection, rq_headers, authorization)
                assertion_status_ = self.response_status_check(acc_collection, status, log)      
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                if assertion_status_ != log.PASS:                 
                    pass
                elif not headers:
                    assertion_status = log.WARN
                else:
                    # check if intended method is an allowable method for resource
                    if (self.allowable_method('POST', headers) != True):      
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for POST" % acc_collection)
                        log.assertion_log('line', rf_utility.json_string(headers))
                    else:
                        #check if user already exists, if it does perfcorm a delete to clean up
                        '''members = self.get_resource_members(acc_collection)
                        for json_payload, headers in members:
                            if json_payload['UserName'] == user_name:       
                                log.assertion_log('TX_COMMENT', "~ note: the %s account pre-exists... deleting it now in prep for creation" % json_payload['UserName'])   
                                # check if intended method is an allowable method for resource
                                if (self.allowable_method('DELETE', headers)):         
                                    json_payload_, headers_, status_ = self.http_DELETE(json_payload['@odata.id'], rq_headers, authorization)
                                    assertion_status_ = self.response_status_check(json_payload['@odata.id'], status_, log, request_type = 'DELETE')      
                                    # manage assertion status
                                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                    if assertion_status_ != log.PASS:                 
                                        log.assertion_log('XL_COMMENT', "~ note: DELETE for %s : %s PASS" % (user_name, json_payload['@odata.id']))
                                        break
                                else:
                                    assertion_status = log.FAIL
                                    log.assertion_log('line', "~ The response headers for %s do not indicate support for DELETE" % acc_collection)
                                    log.assertion_log('line', "~ Item already exists in %s and attempt to request DELETE failed, Try changing item configuration in the script" % acc_collection)                        
                                    break'''

                    if (assertion_status == log.PASS): # Ok to create the session now                                   
                        rq_body = {'UserName' : user_name, 'Password' : '12345' }
                        log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s' % (acc_collection, rq_body))                            
                        json_payload, headers, status = self.http_POST(acc_collection, rq_headers, rq_body, authorization)
                        assertion_status_ = self.response_status_check(acc_collection, status, log, rf_utility.HTTP_CREATED, 'POST')      
                        # manage assertion status
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        if assertion_status_ != log.PASS:                 
                            pass
                        elif not headers:
                            assertion_status = log.WARN
                        else:
                            account_location = headers['location']
                            #perfcorm assertions 6_1_8_1_1,  6_1_8_1_2 to make sure account was created and returned expected headers/body
                            if Assertion_6_1_8_1_1(headers, acc_collection, log) == log.PASS:         
                                # check resource representation in response body              
                                subassertion_status = Assertion_6_1_8_1_2(account_location, json_payload, self, log)
                                if subassertion_status:
                                    #Check status
                                    assertion_status = subassertion_status if (subassertion_status != log.PASS) else assertion_status     
                        
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    log.AssertionID = '6.1.8.1'    
    log.assertion_log(assertion_status, None)    
    return assertion_status
#
## end Assertion 6.1.8.1

#####################################################################################################
# Name: Assertion_6_1_8_1_1(self, log)  Authentication                                             
# Description:      	       
# The response to the POST request to create a user includes:
#  a "Location header that contains a link to the newly created resource.
#####################################################################################################
def Assertion_6_1_8_1_1(headers, url, log):
    log.AssertionID = '6.1.8.1.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    response_key = 'location'
    if response_key not in headers:
        assertion_status = log.FAIL
        log.assertion_log('line', "~ Expected header %s to be in the response header of %s ~ Not found" % (response_key, url))                    
                 
    log.assertion_log(assertion_status, None)
    return assertion_status
#
## end Assertion 6.1.8.1.1

#####################################################################################################
# Name: Assertion_6_1_8_1_2(self, log)                                           
# Description:     	       
# The JSON response body 'may' contain a full representation of the newly created object     
#####################################################################################################
def Assertion_6_1_8_1_2(location_url, json_payload, self, log):
    log.AssertionID = '6.1.8.1.2'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    
    rq_headers = self.request_headers()

    # get the object using GET on location and compare it against the payload returned during POST
    check_payload, headers, status = self.http_GET(location_url, rq_headers, authorization)
    assertion_status_ = self.response_status_check(location_url, status, log)      
    # manage assertion status
    assertion_status = log.status_fixup(assertion_status,assertion_status_)
    if assertion_status_ != log.PASS:                 
        pass
    elif not check_payload:
        assertion_status = log.WARN
        log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (location_url))
    else:
        assertion_status = verifyCreatedObject(json_payload, check_payload, log)      
        if assertion_status == log.FAIL:
            # 'may' contain a full representation....
            assertion_status = log.WARN 
            try:
                log.assertion_log('line', "~ The response body does not contain a full representation of the newly created session object at %s" % (check_payload['@odata.id'] ))
            except:
                log.assertion_log('line', "~ The response body does not contain a full representation of the newly created session object")
                
    log.assertion_log(assertion_status, None) 
    return assertion_status
#
## end Assertion 6.1.8.1.2

#####################################################################################################
# Name: verifyCreatedObject (object_payload, check_payload)                                               
# Description:     
#	Verify an object represented by a json body on its creation with the object requested via GET for
#   the same resource using its location from header             
#####################################################################################################
def verifyCreatedObject(object_payload, check_payload, log):  
    assertion_status = log.PASS
    # check for mismatch...
    for key in check_payload.keys():
        if (key in object_payload):
            if (check_payload[key] != object_payload[key]):
                assertion_status = log.FAIL
                log.assertion_log('line', "~ Property \'%s\' : \'%s\' does not match what was specifed at Creation %s" % (key, check_payload[key], object_payload[key]) )                
        else: 
            assertion_status = log.FAIL
            log.assertion_log('line', "~ The response body does not contain \'%s\' Property of the newly created object" % (key ))            

    return assertion_status

#####################################################################################################
# Name: Assertion_6_1_8_3(self, log)                                               
# Description:     
# PATCH Object update	                                                          
#####################################################################################################
def Assertion_6_1_8_3(self, log) :
    log.AssertionID = '6.1.8.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()
    user_name = 'xxuserxx'
    root_link_key = 'AccountService'

    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        # GET user accounts
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris[root_link_key]['url'], rq_headers, authorization)
        assertion_status_ = self.response_status_check(self.sut_toplevel_uris[root_link_key]['url'], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS:                 
            pass
        elif not json_payload:
            assertion_status = log.WARN
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (self.sut_toplevel_uris[root_link_key]['url']))
        else:
            ## get Accounts collection from payload
            try :
                key = 'Accounts'
                acc_collection = (json_payload[key])['@odata.id']
            except : # no user accounts?
                assertion_status = log.WARN
                log.assertion_log('line', "~ no accounts collection was returned from GET %s" % self.sut_toplevel_uris[root_link_key]['url'])
            else:
                found = False
                members = self.get_resource_members(acc_collection)
                # check for user we want to PATCH       
                for json_payload, headers in members:
                    # check if intended method is an allowable method for resource
                    if (self.allowable_method('PATCH', headers) != True): 
                        assertion_status = log.WARN
                        log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for PATCH" % json_payload['@odata.id'])
                        log.assertion_log('line', rf_utility.json_string(headers))
                    if json_payload['UserName'] == user_name:  
                        found = True                      
                        if self.allowable_method('PATCH', headers):                        
                            account_url = json_payload['@odata.id']
                            patch_key = 'RoleId'   
                            patch_value = 'Operator'
                            rq_body = {'UserName': user_name, 'Password': '12345' , 'RoleId' : patch_value}
                            rq_headers['Content-Type'] = rf_utility.content_type['json']
                            json_payload_, headers_, status_ = self.http_PATCH(account_url, rq_headers, rq_body, authorization)
                            assertion_status_ = self.response_status_check(account_url, status_, log, request_type = 'PATCH')      
                            # manage assertion status
                            assertion_status = log.status_fixup(assertion_status,assertion_status_)
                            if assertion_status_ != log.PASS:                 
                                break
                            else:
                                log.assertion_log('line', "~ note: PATCH %s PASS" % (account_url))
                                #check if the patch succeeded:
                                json_payload, json_headers, status = self.http_GET(account_url, rq_headers, authorization)
                                assertion_status_ = self.response_status_check(account_url, status, log)      
                                # manage assertion status
                                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                if assertion_status_ != log.PASS:                 
                                    log.assertion_log('line', "~ note: Unable to verify if PATCH succeeded, status %s" % status)
                                    break                                     
                                elif json_payload:                             
                                    #if patch_value not in json_payload, FAIL
                                    if 'RoleId' in json_payload:
                                        if patch_value not in json_payload['RoleId']:
                                            assertion_status = log.FAIL
                                            log.assertion_log('line', "~ note : Expected value of patched %s : %s found %s" % (patch_key, patch_value, json_payload[patch_key]) )
                                            break                                                    

                if found == False:
                    assertion_status = log.WARN
                    log.assertion_log('line', "~ note: PATCH could not be verified")

    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    log.assertion_log(assertion_status, None)
    return assertion_status
## end Assertion 6.1.8.3

#####################################################################################################
# Name: Assertion_6_1_8_4(self, log)                                               
# Description:     
# Method: DELETE Object delete                  
#####################################################################################################
def Assertion_6_1_8_4(self, log) :
 
    log.AssertionID = '6.1.8.4'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    user_name = 'testuser'
    authorization = 'on'
    rq_headers = self.request_headers() 

    root_link_key = 'AccountService'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        # GET user accounts
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris[root_link_key]['url'], rq_headers, authorization)
        assertion_status_ = self.response_status_check(self.sut_toplevel_uris[root_link_key]['url'], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS:                 
            pass
        elif not json_payload:  
            assertion_status = log.WARN
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (self.sut_toplevel_uris[root_link_key]['url']))
        else:   ## get Accounts collection from payload
            try :
                key = 'Accounts'
                acc_collection = (json_payload[key])['@odata.id']
            except : # no user accounts?
                assertion_status = log.WARN
                log.assertion_log('line', "~ no accounts collection was returned from GET %s" % self.sut_toplevel_uris[root_link_key]['url'])
            else:                 
                #DELETE 
                members = self.get_resource_members(acc_collection)
                found  = False
                for json_payload, headers in members:
                    # check if intended method is an allowable method for resource   
                    if (self.allowable_method('DELETE', headers) != True):      
                            assertion_status = log.FAIL
                            log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for DELETE" % json_payload['@odata.id'])
                            log.assertion_log('line', rf_utility.json_string(headers))
                    if json_payload['UserName'] == user_name:   
                        found = True  
                        if (self.allowable_method('DELETE', headers)):                    
                            json_payload_, headers_, status_ = self.http_DELETE(json_payload['@odata.id'], rq_headers, authorization)
                            assertion_status_ = self.response_status_check(json_payload['@odata.id'], status_, log, request_type = 'DELETE')      
                            # manage assertion status
                            assertion_status = log.status_fixup(assertion_status,assertion_status_)
                            break                  
                if found == False:
                    assertion_status = log.WARN
                    log.assertion_log('line', "~ note: DELETE could not be verified")
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )
                        
    log.assertion_log(assertion_status, None)
    return assertion_status
#
## end Assertion 6.1.8.4

###################################################################################################
# Name: Assertion_6_1_9(self, log)                                               
# Description: Other HTTP methods are not allowed and shall receive a 405 response.    
# Method: TRACE ~ should not be supported, expected status 405
#         OPTIONS ~ is not a Required one but it can be supported. Depends on server.           
###################################################################################################
def Assertion_6_1_9(self, log) :
 
    log.AssertionID = '6.1.9'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_TRACE(relative_uris[relative_uri], rq_headers, None, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_METHODNOTALLOWED, 'TRACE')          
        if(status== 405):
            assertion_status = log.PASS
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)

        '''json_payload, headers, status = self.http_OPTIONS(relative_uris[relative_uri], rq_headers, None, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_METHODNOTALLOWED, 'OPTIONS')      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)'''

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.1.9 

###################################################################################################
# Name: Assertion_6_1_11(self, log)                                               
# Description:     
#	All resources shall be made available using the JSON media type "application/json".		                                                            
###################################################################################################
def Assertion_6_1_11(self, log) :
 
    log.AssertionID = '6.1.11'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    rq_headers = self.request_headers()
    header_key = 'Content-Type'
    header_value = rf_utility.accept_type['json']
    rq_headers[header_key] = header_value
    authorization = 'on'

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.1.11

###################################################################################################
# Name: Assertion 6_1_12(self,log)
# Description:
# Redfish services shall make every resource available in a representation based on JSON, as specified in RFC4627.
# Receivers shall not reject a message because it is encoded in JSON, and shall offer at least one response representation based on JSON.
###################################################################################################
def Assertion_6_1_12(self,log) :
    log.AssertionID = '6.1.12'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    relative_uris = self.relative_uris
    print('Checking if all responses are in JSON')
    authorization = 'on'
    rq_headers = self.request_headers()

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)

        if status == 200 :
            if not json_payload:
                print ('The response received is not in JSON %s'% json_payload)
                assertion_status = log.FAIL
        else :
            continue
    log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion 6.1.12

#####################################################################################################
# Name: Assertion_6_1_14(self, log)                                               
# Description:     
#  ETah headers:  For certain requests and responses implementation shall support returning ETag headers               
#####################################################################################################
def Assertion_6_1_14(self, log) :
 
    log.AssertionID = '6.1.14'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    # get SUTs relative uris dictionary
    relative_uris = self.relative_uris

    authorization = 'on'
    rq_headers = self.request_headers()    
    # loop for each uri in relative uris dict
    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        #primitive_types = ['Edm.Boolean', 'Edm.DateTimeOffset', 'Edm.Decimal', 'Edm.Double', 'Edm.Guid', 'Edm.Int64', 'Edm.String']
        #print('The headers is %s' %headers)
        try:
            etag_ = headers['etag']
            if etag_ in headers['etag']:
                print('The ETag is present in %s' %relative_uri)
                print ('The etag is %s' %etag_)
                assertion_status= log.PASS
                continue
        except:
            print('ETag header not found in %s' %relative_uri)
            assertion_status= log.WARN
            continue

    assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)             
        # manage assertion status
    assertion_status = log.status_fixup(assertion_status,assertion_status_)

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.1.14


###################################################################################################
# Name: Assertion_6_1_13(self, log)                                               
# Description:     
# Services should support gzip compression when requested by the client. if service cannot respond 
# with gzip, 406 should be returned                                                        
###################################################################################################
def Assertion_6_1_13(self, log) :
 
    log.AssertionID = '6.1.13'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    relative_uris = self.relative_uris
    rq_headers = self.request_headers()
    header_key = 'Accept-Encoding'
    header_value = 'gzip'
    rq_headers[header_key] = header_value

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_NOTACCEPTABLE)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status == log.FAIL and status == rf_utility.HTTP_OK:                 
            log.assertion_log('line', '%s:%s is also an acceptable status' % (rf_utility.HTTP_OK, rf_utility.HTTP_status_string(rf_utility.HTTP_OK)) )   
            assertion_status = log.PASS              
        
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.1.13

###################################################################################################
# Name: Assertion_6_2_3(self, log)                                               
# Description:                                                  
#	A GET on the resource "/redfish" shall return the following body: json { "v1": "/redfish/v1/" }                 
###################################################################################################
def Assertion_6_2_3(self, log) :

    log.AssertionID = '6.2.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET(self.Redfish_URIs['Protocol_Version'], rq_headers, authorization)
    assertion_status_ = self.response_status_check(self.Redfish_URIs['Protocol_Version'], status, log)      
    # manage assertion status
    assertion_status = log.status_fixup(assertion_status,assertion_status_)
    if assertion_status_ != log.PASS:                 
        pass
    elif not json_payload:  
        assertion_status_ = log.WARN
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_) 
        log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (self.Redfish_URIs['Protocol_Version']))
    else:     
        # parse the json data returned and verify
        key ='v1'
        value = '/redfish/v1/'
        if key not in json_payload:
            assertion_status = log.FAIL
            log.assertion_log('line',  "~ unable to locate 'v1'  key in JSON payload returned from GET %s" % (self.Redfish_URIs['Protocol_Version']))           
        elif (json_payload[key] != value) :
            assertion_status = log.FAIL
            log.assertion_log('line', "~ invalid value returned from GET %s. Expected %s" % (json_payload[key], self.Redfish_URIs['Protocol_Version'], value))
               
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.2.3

###################################################################################################
# Name: Assertion 6_1_0(self,log)- HTTP_NOT_FOUND status added by Priyanka TTU
# Description:
# The following method check the URI status of 404 and is reported if found.
###################################################################################################
def Assertion_6_1_0(self,log) :
    log.AssertionID = '6.1.0'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    relative_uris = self.relative_uris
    print('Checking all URIs')
    authorization = 'on'
    rq_headers = self.request_headers()

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        '''if status == rf_utility.HTTP_OK:
            print('HTTP OK - 200 for ', relative_uri )'''

        if status == rf_utility.HTTP_NOT_FOUND:
            print ('HTTP Not Found- 404 for ', relative_uri , json_payload)
            log.assertion_log('TX_COMMENT',"WARN: GET %s failed : HTTP status %s:%s" % (relative_uris[relative_uri], status, rf_utility.HTTP_status_string(status)) )
            continue
    log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion 6.1.0

######################################################################################################################################################
# Name: Assertion 6_1_1(self,log)
# Description:
# A Redfish interface shall be exposed through a web service endpoint implemented using Hypertext Transfer Protocols, version 1.1 (RFCL616).
######################################################################################################################################################
def Assertion_6_1_1(self,log) :
    log.AssertionID = '6.1.1'
    assertion_status = log.WARN
    log.assertion_log('BEGIN_ASSERTION', None)
    relative_uris = self.relative_uris
    print('A web service endpoint is endpoint is the URL where your service can be accessed by a client application. It should always contain protocol://host:port/partOfThePath. In case of Redfish interface it shall be https ')
    authorization = 'on'
    rq_headers = self.request_headers()

    
    print('This assertion is checked by accessing the all redfish root resources through HTTP and if this passes, this is passes, else failed')
    json_payload, headers, status_1 = self.http_GET(self.Redfish_URIs['Service_Root'], rq_headers, authorization)
    json_payload, headers, status_2 = self.http_GET(self.Redfish_URIs['Protocol_Version'], rq_headers, authorization)
    json_payload, headers, status_3 = self.http_GET(self.Redfish_URIs['Service_Odata_Doc'], rq_headers, authorization)
    json_payload, headers, status_4 = self.http_GET(self.Redfish_URIs['Service_Metadata_Doc'], rq_headers, authorization)
    print('The different status are %s, %s, %s, %s' %(status_1, status_2, status_3, status_4))
    if ( status_1 == status_2 == status_3 == status_4 == 200) :
        assertion_status = log.PASS

    else:
        print ('This is a fail')
        assertion_status = log.FAIL
        #log.assertion_log('TX_COMMENT',"WARN: GET failed : HTTP status %s:%s" %( assertion_status, rf_utility.HTTP_status_string(assertion_status)) )


    log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion 6.1.1


#########################################################################################################################################################################
# Name: Assertion 6_1_2(self,log)
# Description:
# Each unique instance of a resource shall be identified by a URI; thus a URI cannot reference multiple resources though it may reference a single collection resource.
#########################################################################################################################################################################
def Assertion_6_1_2(self,log) :

    log.AssertionID = '6.1.2'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    print('URI provides a simple and extensible means for identifying a resource and each unique instance of a resource is identified by a URI. It is defined in clause 5, Reference Resolution, of RFC3986. ')
    authorization = 'on'
    relative_uris = self.relative_uris
    rq_headers = self.request_headers()    
    uri = set ()
    uniq = []

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        if status == rf_utility.HTTP_OK:
            print('HTTP OK - 200 for ', relative_uri )
            if relative_uri not in uri :
                uniq.append(relative_uri)
                uri.add(relative_uri)
                continue
            else :
                assertion_status = log.FAIL
                break         
                       
        elif status == rf_utility.HTTP_NOT_FOUND:
            print ('HTTP Not Found- 404 for ', relative_uri , json_payload)
            log.assertion_log('TX_COMMENT',"WARN: GET %s failed : HTTP status %s:%s" % (relative_uris[relative_uri], status, rf_utility.HTTP_status_string(status)) )
            continue

    log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion 6.1.2

###################################################################################################
# Name: Assertion_6_3_1(self, log)                                               
# Description: 
# 	The following Redfish-defined URIs shall be supported by a Redfish service and authorization 
#   should not be required to get the uri
#	/redfish The URI that is used to return the protocol version 
#	/redfish/v1/ The URI for the Redfish Service Root 
#	/redfish/v1/odata The URI for the Redfish OData Service Document 
#	/redfish/v1/metadata The URI for the Redfish schema Document                                                                 
###################################################################################################
def Assertion_6_3_1(self, log) :
 
    log.AssertionID = '6.3.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    # authorization should not be required for these GETs
    authorization = 'off'
    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET(self.Redfish_URIs['Protocol_Version'] , rq_headers, authorization)
    assertion_status_ = self.response_status_check(self.Redfish_URIs['Protocol_Version'], status, log)      
    # manage assertion status
    assertion_status = log.status_fixup(assertion_status,assertion_status_)
    if assertion_status == log.PASS:                 
        log.assertion_log('line',"~ GET %s : HTTP status %s:%s" % (self.Redfish_URIs['Protocol_Version'], status, rf_utility.HTTP_status_string(status)) ) 

    json_payload, headers, status = self.http_GET(self.Redfish_URIs['Service_Root'], rq_headers, authorization)
    assertion_status_ = self.response_status_check(self.Redfish_URIs['Service_Root'], status, log)      
    # manage assertion status
    assertion_status = log.status_fixup(assertion_status,assertion_status_)
    if assertion_status_ != log.PASS:                 
        pass
    else:             
        log.assertion_log('line',"~ GET %s : HTTP status %s:%s" % (self.Redfish_URIs['Service_Root'], status, rf_utility.HTTP_status_string(status)) ) 
    if assertion_status == log.PASS and json_payload:
        # dont need to do this?
        oem_key = 'OEM'
        # do a quick-check on the json payload -~ get the oem name from the root service payload
        stat, oem_name = rf_utility.json_get_key_value(json_payload, oem_key)
        if (stat != False):		             	
            #might be useful info...
            self.SUT_OEM['key'] = oem_key
            self.SUT_OEM['name'] = oem_name
      
    json_payload, headers, status = self.http_GET(self.Redfish_URIs['Service_Odata_Doc'], rq_headers, authorization)
    assertion_status_ = self.response_status_check(self.Redfish_URIs['Service_Odata_Doc'], status, log)      
    # manage assertion status
    assertion_status = log.status_fixup(assertion_status,assertion_status_)
    if assertion_status == log.PASS:
        log.assertion_log('line',"~ GET %s : HTTP status %s:%s" % (self.Redfish_URIs['Service_Odata_Doc'], status, rf_utility.HTTP_status_string(status)) ) 

    rq_headers ['Accept'] = rf_utility.accept_type['xml']
    json_payload, headers, status = self.http_GET(self.Redfish_URIs['Service_Metadata_Doc'], rq_headers, authorization)
    assertion_status_ = self.response_status_check(self.Redfish_URIs['Service_Metadata_Doc'], status, log)      
    # manage assertion status
    assertion_status = log.status_fixup(assertion_status,assertion_status_)
    if assertion_status == log.PASS:
        log.assertion_log('line',"~ GET %s : HTTP status %s:%s" % (self.Redfish_URIs['Service_Metadata_Doc'], status, rf_utility.HTTP_status_string(status)) ) 
    
    ## log completion status
    log.assertion_log(assertion_status, None)
    return assertion_status

#
## end Assertion 6.3.1

###################################################################################################
# Name: Assertion_6_3_2(self, log)                                               
# Description:     
#	the following URI without a trailing slash shall be either Redirected to the Associated 
#   Redfish-defined URI shown below or else shall be treated by the service as the equivalent URI 
#   to the associated Redfish-defined URI:
#		/redfish/v1     /redfish/v1/                                                       
###################################################################################################
def Assertion_6_3_2(self, log) :
 
    log.AssertionID = '6.3.2'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    root_redirect = [self.Redfish_URIs['Service_Root'][:-1]][0]

    json_payload, headers, status = self.http_GET(root_redirect, rq_headers, authorization)
    assertion_status_ = self.response_status_check(root_redirect, status, log)      
    # manage assertion status
    assertion_status = log.status_fixup(assertion_status,assertion_status_)
    if assertion_status_ != log.PASS:                 
        log.assertion_log('line', "~ Expected the service to treat %s equivalent to %s" % (root_redirect, self.Redfish_URIs['Service_Root']))
        
    ## log completion status
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.3.2

###################################################################################################
# Name: Assertion_6_3_3(self, log)      WIP unclear only tested in python 2.7.x                                   
# Description:     
#   All relative URIs used by the service shall start with a double forward slash ("//") and include 
#   the authority (e.g. //mgmt.vendor.com/redfish/v1/Systems) or a single forward slash ("/") and 
#   include the absolute-path e.g:/redfish/v1/Systems                                         
#
# Note: From https://www.w3.org/Protocols/rfcc2616/rfcc2616-sec5.html:
# one form is : GET http://www.w3.org/pub/WWW/TheProject.html HTTP/1.1
# antoher form is :     GET /pub/WWW/TheProject.html HTTP/1.1
###################################################################################################

def Assertion_6_3_3(self, log) :

    log.AssertionID = '6.3.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris

    authorization = 'on'
    rq_headers = self.request_headers()
    
    #1. single slash
    # example: GET /pub/WWW/TheProject.html HTTP/1.1
    # Host: www.w3.org
    '''for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)'''
         
    #TODO
    # httplib has url form limitation, using urllib2 for python 2.7
    # http://www.w3.org/pub/WWW/TheProject.html HTTP/1.1
    # try  path with //auth/path
    url ="https://"+ self.SUT_prop['DnsName'] + self.Redfish_URIs['Service_Root']+'Systems'
    # Made changes in accessing the url and opening the url and reading - Priyanka.
    json_payload, headers, status = self.http_GET(url, rq_headers, authorization)
    print('Status is %s' %status)

    if status != 200:
        assertion_status = log.FAIL

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.3.3

###################################################################################################
# Name: Assertion_6_4_1(self, log)                                               
# Description:     
# Redfish Services shall understand and be able to process the headers if in the specification the 
# value in the Required Column is set to "Yes" or "Conditional". It covers 6.4.2 as well- WIP	Priyanka                                                           
###################################################################################################

def Assertion_6_4_1(self, log) :
 
    log.AssertionID = '6.4.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()
    relative_uris = self.relative_uris
    #json_payload, headers, status = self.http_GET('/redfish/v1/Managers', rq_headers, authorization)
    #print('Headers is %s' %headers)
    #The headers mentioned below are the headers that are required and conditional.
    Headers = ['accept', 'odata-version', 'User-Agent','Host','Origin','X-Auth-Token','content-type','Authorization','If-Match']

    for relative_uri in relative_uris : 
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)

        try:
            c_type = headers['content-type']
            if c_type in headers['content-type']:
                headers['content-type'] = ''
                json_payload, headers1, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)

                if status != log.PASS:
                    assertion_status = log.PASS
                    continue

                else:
                    assertion_status = log.FAIL
                    break
        except :
            assertion_status = log.WARN         
    #assertion_status = log.status_fixup(assertion_status,assertion_status_)                    
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.1

# This function checks whether the HTTP GET method retrieve a resource without causing any side effects.- Priyanka
def verify_retrieve_resource(json_payload, assertion_status, self, log):
    key = '@odata.type'
    csdl_schema_model = self.csdl_schema_model
    if key not in json_payload:
        assertion_status = log.FAIL
        log.assertion_log('line', "Expected property %s for resource %s " % (key, json_payload['@odata.id']) )
    else:
        #verify singleton context url format
        if key in json_payload:
                namespace, typename = csdl_schema_model.get_resource_namespace_typename(json_payload['@odata.type'])
                if not typename:
                     assertion_status= log.FAIL
                     log.assertion_log('line', "The required property is a complex type" % (key, json_payload[property.Name]) )
                     
    return assertion_status  

           
###################################################################################################
# Name: Assertion_6_4_4(self, log)                                               
# Description:     
# The HTTP Get method shall be able to retrieve a resource without causing any side effects.-Priyanka                                                           
###################################################################################################

def Assertion_6_4_4(self, log):

    log.AssertionID = '6.4.4'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    rq_headers = self.request_headers()
    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris_no_members

    authorization = 'on'
    rq_headers = self.request_headers()
    # loop for each uri in relative uris dict
    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)             
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                             
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.4

###################################################################################################
# Name: Assertion_6_4_5(self, log)                                               
# Description:     
# The service shall ignore the content of the body on a GET.-Priyanka                                                           
###################################################################################################

def Assertion_6_4_5(self, log):

    log.AssertionID = '6.4.5'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    rq_headers = self.request_headers()
    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris_no_members

    authorization = 'on'
    rq_headers = self.request_headers()
    rq_body = {'@odata.id' : '123'}
    # loop for each uri in relative uris dict
    for relative_uri in relative_uris:
        try:
            json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, rq_body, authorization)
            if status == '200':
                assertion_status = log.FAIL
                
            else:
                assertion_status = log.WARN
        
        except:
            assertion = log.PASS

        #assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)             
        # manage assertion status
        #assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                             
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.5


###################################################################################################
# Name: Assertion_6_4_11(self, log)                                               
# Description:     
#	Services shall not require authentication in order to retrieve the service document.	                                                           
###################################################################################################
def Assertion_6_4_11(self, log) :
 
    log.AssertionID = '6.4.11'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'off'
    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET(self.Redfish_URIs['Service_Metadata_Doc'], rq_headers, authorization)
    assertion_status_ = self.response_status_check(self.Redfish_URIs['Service_Metadata_Doc'], status, log)      
    # manage assertion status
    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                      
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.11

###################################################################################################
# Name: Assertion_6_4_13()     Query Parameters                                         
# Description:     
#	Implementation shall return the 501 : Not Implemented status code for any query parameters
#   starting with "$" that are not supported, and should return an extended error indicating the
#   requested query parameter(s) not supported for this resource.	 
#   param example: http://collection?$skip=5 in spec        
#   Note: find resource to try a correct query            
#   params: section 5.1.x http://docs.oasis-open.org/odata/odata/v4.0/errata02/os/complete/part2-url-conventions/odata-v4.0-errata02-os-part2-url-conventions-complete.html#_Toc406398092                              
###################################################################################################
def Assertion_6_4_13(self, log) :
    
    log.AssertionID = '6.4.13'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on' 
    rq_headers = self.request_headers()
    query_param = '?$top=1'

    relative_uris = self.relative_uris
    #find alias in Include first?
    print('Beginning Assertion Test 6.4.13 for checking the status code with unsupported $')
    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                if 'Collection' in json_payload['@odata.type']:                  
                    query_url = json_payload['@odata.id'][:-1] + query_param
                    json_payload, headers, status = self.http_GET(query_url , rq_headers, authorization)
                    print('Status is %s' %status)
                    assertion_status_ = self.response_status_check(query_url, status, log, rf_utility.HTTP_NOTIMPLEMENTED)      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                    if status == 501 :
                        assertion_status = log.PASS
                        print('The status is %s for the query %s in the resource %s' %(status,query_param,relative_uri))
                        log.assertion_log(assertion_status, None)
                        return (assertion_status)
            else:      
                assertion_status = log.WARN
                log.assertion_log('line', "~ @odata.type (resource identifier property) not found in redfish resource %s" % (relative_uris[relative_uri]))
    
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.13

###################################################################################################
# Name: Assertion_6_4_14(self, log)   Query Parameters                                            
# Description:     
#		Implementations shall ignore unknown or unsupported query parameters that do not begin with 
#       "$" param example: http://collection?$skip=5 in spec                                                    
###################################################################################################
def Assertion_6_4_14(self, log) :
 
    log.AssertionID = '6.4.14'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    
    rq_headers = self.request_headers()
    query_param = '?top=1'

    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                if 'Collection' in json_payload['@odata.type']:                  
                    query_url = json_payload['@odata.id'][:-1] + query_param
                    json_payload, headers, status = self.http_GET(query_url , rq_headers, authorization)
                    assertion_status_ = self.response_status_check(query_url, status, log)                       
            else:      
                assertion_status_ = log.WARN
                log.assertion_log('line', "~ @odata.type (resource identifier property) not found in redfish resource %s" % (relative_uris[relative_uri]))

            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)


    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.14

###################################################################################################
# Name: Assertion_6_4_16(self, log)   Retrieving Collections                                            
# Description:     
#   Retrieved collections shall always include the count property to specify the total number of 
#   members in the collection.     
# Resource count property = Members@odata.count       
###################################################################################################
def Assertion_6_4_16(self, log) :

    log.AssertionID = '6.4.16'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()
    resource_count_key = 'Members@odata.count'

    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                if 'Collection' in json_payload['@odata.type']:                          
                    if resource_count_key not in json_payload:
                        assertion_status = log.FAIL
                        log.assertion_log('line', "Property %s not found for resource %s" %(resource_count_key, relative_uris[relative_uri]) )
            else:      
                assertion_status = log.WARN
                log.assertion_log('line', "~ @odata.type (resource identifier property) not found in redfish resource %s" % (relative_uris[relative_uri]))
                             
    log.assertion_log(assertion_status, None)
    return (assertion_status)
   
## end Assertion 6.4.16

###################################################################################################
# Name: Assertion_6_4_18(self, log)                                               
# Description:     
#   An attractive feature of the RESTful interfcace is the very limited number of operations which 
#   are supported.
# Method: HEAD is optional for services..
#   The HEAD method differs from the GET method in that it MUST NOT return message body information.  
#   However, all of the same meta information and status codes in the HTTP headers 
#   will be returned as though a GET method were processed, including authorization checks.                                                 
###################################################################################################
def Assertion_6_4_18(self, log) :
 
    log.AssertionID = '6.4.18'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris

    for relative_uri in relative_uris: 
        authorization = 'on'
        rq_headers = self.request_headers()
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)          
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS:                 
            continue
        else:
            # check if intended method is an allowable method for resource
            if (self.allowable_method('HEAD', headers)):
                # method is allowed ~ the service must 1. NOT return a payload
                authorization = 'on'
                rq_headers = self.request_headers()
                json_payload, headers, status = self.http_HEAD(relative_uris[relative_uri], rq_headers, authorization)
                assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, request_type = 'HEAD')      
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                if assertion_status_ != log.PASS:                 
                    continue
                # should not contain response body
                elif json_payload:
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ HEAD on %s resposne returned a payload: %s" % (relative_uris[relative_uri], rf_utility.json_string(json_payload)) )

                # method is allowed ~ the service must 2. FAIL the request without authorization
                authorization = 'off'
                rq_headers = self.request_headers()
                json_payload, headers, status = self.http_HEAD(relative_uris[relative_uri], rq_headers, authorization)
                if (status == rf_utility.HTTP_OK) :
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ HEAD on %s without authorization returned status %s:%s" % (relative_uris[relative_uri], status, rf_utility.HTTP_status_string(status)))

                elif (status != rf_utility.HTTP_UNAUTHORIZED):
                    assertion_status = log.WARN
                    log.assertion_log('line', "~ HEAD on %s expected HTTP UNAUTHORIZED; returned status %s:%s" % (relative_uris[relative_uri], status, rf_utility.HTTP_status_string(status)) )

                elif status == rf_utility.HTTP_NOT_FOUND:
                    log.assertion_log('TX_COMMENT',"WARN: GET %s failed : HTTP status %s:%s" % (relative_uris[relative_uri], status, rf_utility.HTTP_status_string(status)) )
                         
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.18


###################################################################################################
# Name: Assertion_6_4_21(self, log)                                               
# Description:     	
# Modification Request: 
# 6.4.21 Services return a status code 405 if the specified resource exists but does not support
# the requested operation
# Method: POST ~ try to modify a resource that does not support POST, expected result
# HTTP_METHODNOTALLOWED (405)    
###################################################################################################
def Assertion_6_4_21(self, log) : #POST

    log.AssertionID = '6.4.21'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    relative_uris = self.relative_uris
    rq_headers = self.request_headers()

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS:                 
            continue
        else:
            # check if intended method is an allowable method for resource
            if not (self.allowable_method('POST', headers)):
                if 'etag' not in headers:
                    assertion_status = log.WARN
                    log.assertion_log('line', "~ note: Etag exepcted in headers of %s: %s ~ not found" %(relative_uris[relative_uri], rf_utility.json_string(headers))) 
                    log.assertion_log('line', "~ note: Modifications to resource using If-None-Match header without Etag cannot be tested")
                else:
                    etag = headers['etag']
                    rq_body = {'Name': 'New Name'}
                    #log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s' % (relative_uris[relative_uri], rq_body))  
                    json_payload, headers, status = self.http_POST(relative_uris[relative_uri], rq_headers, rq_body, authorization)
                    assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_METHODNOTALLOWED, 'POST')         
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                    if assertion_status_ != log.PASS:                 
                        continue      
                    else:
                        #check if resource remain unchanged using etag and If-None-Match header
                        rq_headers = self.request_headers()
                        rq_headers['If-None-Match'] = etag
                        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
                        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_NOTMODIFIED)      
                        # manage assertion status
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        if assertion_status_ != log.PASS:                 
                            log.assertion_log('line', "~ POST %s : Resource might have updated unexpectedly" % (relative_uris[relative_uri]) )


    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.21

###################################################################################################
# Name: Assertion_6_4_23(self, log)                                               
# Description:   
#   Services shall support the PATCH method to update a resource. If the resource can never be 
#   updated, status code 405 shall be returned.  	
# Method: PATCH ~ try to modify a resource that does not support PATCH,
#               expected result HTTP_METHODNOTALLOWED (405)            
###################################################################################################
def Assertion_6_4_23(self, log) :
 
    log.AssertionID = '6.4.23'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS:                 
            continue
        else:
            # check if intended method is an allowable method for resource
            if not (self.allowable_method('PATCH', headers)):
                rq_body = {'Name' : "New Patch Name"}
                json_payload, headers, status = self.http_PATCH(relative_uris[relative_uri], rq_headers, rq_body, authorization)
                assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_METHODNOTALLOWED, 'PATCH')          
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                if assertion_status_ != log.PASS:                 
                    continue
                else:
                    #check if resource remain unchanged
                    #TODO check if etags is in headers then use that method too
                    json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
                    assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)          
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                    if assertion_status_ != log.PASS:                 
                        log.assertion_log('Unable to verify PATCH for resource readonly property' & (relative_uris[relative_uri]))
                        continue
                    elif json_payload:
                        if 'Name' in json_payload:
                            if ("New Patch Name" in json_payload['Name']) :
                                assertion_status = log.FAIL
                                log.assertion_log('line', "~ PATCH %s : Resource might have been updated unexpectedly" % (relative_uris[relative_uri]) )           
             
    log.assertion_log(assertion_status, None)

    return (assertion_status)

#
## end Assertion 6.4.23

###################################################################################################
# Name: Assertion_6_4_24(self, log)        - checked via csdl schema                                 
# Description: 
# Method: PATCH ~ If a property in the request can never be updated, such as when a property is
# read only, a status code of 200 shall be returned along with a representation of the resource 
# containing an annotation specifying the non-updatable property. In this success case, other 
# properties may be updated in the resource.	                                                           
###################################################################################################
def _Assertion_6_4_24(self, log) :
    log.AssertionID = '6.4.24'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    found = False

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                    for property in typename.Properties:
                        permisssions = csdl_schema_model.get_annotation(property, 'OData.Permissions')
                        if permisssions:
                            if permisssions.AttrValue:
                                if permisssions.AttrValue == 'OData.Permissions/Read':
                                    # check if intended method is an allowable method for resource
                                    if (self.allowable_method('PATCH', headers)):   
                                        #check property name in json_payload..if available request patch on it       
                                        if property.Name in json_payload.keys():                                                   
                                            rq_body = {property.Name: 'PatchName'}		
                                            json_payload, headers, status = self.http_PATCH(relative_uris[relative_uri], rq_headers, rq_body, authorization)
                                            assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, request_type = 'PATCH')      
                                            # manage assertion status
                                            assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                            if assertion_status_ != log.PASS:                 
                                                log.assertion_log('line', "~ PATCH on Read-only property %s" % (property.Name) )  
                                                continue          
                                            else:
                                                #TODO check extended error should have property name in msgargs annotation...
                                                json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
                                                assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
                                                # manage assertion status
                                                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                                if assertion_status_ != log.PASS:                 
                                                    log.assertion_log('Unable to verify PATCH for resource %s read-only Property %s' & (relative_uris[relative_uri], property.Name))
                                                    continue
                                                if not json_payload:
                                                    assertion_status = log.WARN
                                                    log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
                                                else:
                                                    if property.Name in json_payload.keys():
                                                        #check if resource remain unchanged, else FAIL. The object might have changed by another source changing the etag, so, in this case, checking value of property makes more sense than etags
                                                        if (json_payload[property.Name] == 'PatchName'):
                                                            assertion_status = log.FAIL
                                                            log.assertion_log('line', "~ PATCH on Property %s of resource %s might have been updated unexpectedly" % (property.Name, relative_uris[relative_uri]) )                                                                                         
    log.assertion_log(assertion_status, None)

    return (assertion_status)
#
## end Assertion 6.4.24

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
# Name: Assertion_6_4_24(self, log)             -checked via json schema                               
# Description: 
# Method: PATCH ~ If a property in the request can never be updated,  such as when a property is 
# read only, a status code of 200 shall be returned along with a representation of the resource 
# containing an annotation specifying the non-updatable property. In this success case, other 
# properties may be updated in the resource.	                                             
###################################################################################################
def Assertion_6_4_24(self, log) :
    log.AssertionID = '6.4.24'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    found = False

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    annotation_term = 'readonly'

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                            if 'properties' in json_metadata['definitions'][typename]:
                                for prop in json_metadata['definitions'][typename]['properties']:                                       
                                    if annotation_term in json_metadata['definitions'][typename]['properties'][prop]:
                                        if json_metadata['definitions'][typename]['properties'][prop][annotation_term]:
                                            # if true. check if intended method is an allowable method for resource
                                            if (self.allowable_method('PATCH', headers)):   
                                                #check property name in json_payload..if available request patch on it       
                                                if prop in json_payload.keys():                                                   
                                                    rq_body = {prop: 'PatchName'}		
                                                    json_payload, headers, status = self.http_PATCH(relative_uris[relative_uri], rq_headers, rq_body, authorization)
                                                    if status:
                                                        if status == rf_utility.HTTP_OK:
                                                            assertion_status = log.FAIL               
                                                            log.assertion_log('line', "~ PATCH passed on property %s with annotation term %s : %s (check document %s) which is an unexpected behavior" % (prop, annotation_term, json_metadata['definitions'][typename]['properties'][prop][annotation_term], schema_file))
                                                            continue                                                   
                                                    else:
                                                        #TODO check extended error should have property name in msgargs annotation...
                                                        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
                                                        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
                                                        # manage assertion status
                                                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                                        if assertion_status_ != log.PASS:                 
                                                            continue
                                                        if not json_payload:
                                                            assertion_status = log.WARN
                                                            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
                                                        else:
                                                            if prop in json_payload.keys():
                                                                #check if resource remain unchanged, else FAIL. The object might have changed by another source changing the etag, so, in this case, checking value of property makes more sense than etags
                                                                if (json_payload[property.Name] == 'PatchName'):
                                                                    assertion_status = log.FAIL
                                                                    log.assertion_log('line', "~ PATCH on Property %s of resource %s is a Read-only property according to its schema document %s, which might have been updated unexpectedly" % (prop, relative_uris[relative_uri]) )                                                                                         

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.24



###################################################################################################
# Name: Assertion_6_4_25(self, log)                                               
# Description:     
# Method: PUT ~ modify a resource that does not support modification (PUT), expected result 
# HTTP_METHODNOTALLOWED               
###################################################################################################
def Assertion_6_4_25(self, log) :
 
    log.AssertionID = '6.4.25'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS:                 
            continue
        else:
            # check if intended method is an allowable method for resource
            if not (self.allowable_method('PUT', headers)): 
                if 'etag' not in headers:
                    assertion_status = log.WARN
                    log.assertion_log('TX_COMMENT', "~ note: Etag exepcted in headers of %s:%s ~ not found" %(relative_uris[relative_uri], rf_utility.json_string(headers))) 
                    log.assertion_log('TX_COMMENT', "~ note: Modifications to resource using If-None-Match header without Etag cannot be tested")
                else:
                    etag = headers['etag']
                    #updating with request body
                    rq_body = {'Name': 'Put Name'}		
                    json_payload, headers, status = self.http_PUT(relative_uris[relative_uri], rq_headers, rq_body, authorization)
                    assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_METHODNOTALLOWED, 'PUT')            
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                    if assertion_status_ != log.PASS:                 
                        continue
                    elif etag:
                        #check if resource remain unchanged
                        rq_headers = self.request_headers()
                        rq_headers['If-None-Match'] = etag
                        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
                        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_NOTMODIFIED)         
                        # manage assertion status
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        if assertion_status_ != log.PASS:                 
                            log.assertion_log('line', "~ GET %s with If-None-Match provided an etag returned status %s:%s which indicates that this resource which does not allow PUT method might have been updated unexpectedly as a result of requesting a PUT method on it previously" % (relative_uris[relative_uri], status, rf_utility.HTTP_status_string(status)) )
                            log.assertion_log('XL_COMMENT', ('Checked if resource is modified using If-None-Match header and etag'))
                            continue
 
               
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.25

###################################################################################################
# Name: Assertion_6_4_26(self, log)                                     
# Description:                                                  
# 	Submitting a POST request to a resource representing a collection is equivalent to submitting the same request to 
#   the Members property of that resource. Services that support adding members to a collection shall support both forms.
###################################################################################################
def Assertion_6_4_26(self, log) :

    log.AssertionID = '6.4.26'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    header_name = 'Content-Type'

    rq_headers = self.request_headers()
    # get the collection of user accounts...

    root_link_key = 'SessionService'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris[root_link_key]['url'], rq_headers, authorization)
        assertion_status_ = self.response_status_check(self.sut_toplevel_uris[root_link_key]['url'], status, log)           
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS:                 
            pass
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (self.sut_toplevel_uris[root_link_key]['url']))
        else:
            ## get Sessions collection from payload
            try :
                key = 'Sessions'
                acc_collection = (json_payload[key])['@odata.id']
            except :
                assertion_status = log.WARN
                log.assertion_log('line', "~ \'Sessions\' not found in the payload from GET %s" % (self.sut_toplevel_uris[root_link_key]['url']))    
            else:         
                ## Found the key in the payload, try a GET on the link for a response header
                json_payload, headers, status = self.http_GET(acc_collection, rq_headers, authorization)
                assertion_status_ = self.response_status_check(acc_collection, status, log)      
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                if assertion_status_ != log.PASS: 
                    pass
                else:
                    # check if intended method is an allowable method for resource
                    if (self.allowable_method('POST', headers) != True):      
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for POST" % acc_collection)
                        log.assertion_log('line', rf_utility.json_string(headers))
                    else:
                        #check if user has members and if it has, do the post operation on members and check if it works
                        members = json_payload['Members']
                        if members == [] :
                            print('There are no members')
                        else:
                            for each_member in members:
                                each_member = each_member.get('@odata.id')
                                print('The members of the Session collection are %s' %each_member)
                                json_payload, headers, status = self.http_GET(each_member, rq_headers, authorization)
                                assertion_status = self.response_status_check(each_member, status, log)
                                if (assertion_status == log.PASS) :
                                    rq_body = {'UserName' : 'testuser' , 'Password' : '123' }
                                    rq_headers['Accept'] = rf_utility.accept_type['json']
                                    rq_headers['content-type'] = 'application/json'
                                    rq_headers['odata-version'] = '4.0'
                                    json_payload, headers, status = self.http_POST(each_member, rq_headers, rq_body, authorization)
                                    assertion_status = self.response_status_check(each_member, status, log)

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.26

###################################################################################################
# Name: Assertion_6_4_27(self, log)                                     
# Description:                                                  
# 	Services shall support the POST method for creating resources. If the resource does not offer anything to be created, 
#   a status code 405 shall be returned.
###################################################################################################
def Assertion_6_4_27(self, log) :

    log.AssertionID = '6.4.27'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    relative_uris = self.relative_uris
    csdl_schema_model = self.csdl_schema_model
    rq_body = {'Name': 'New Name'}

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
            if not (self.allowable_method('POST', headers)):
                json_payload, headers, status = self.http_POST(relative_uris[relative_uri], rq_headers, rq_body, authorization)
                assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_METHODNOTALLOWED, 'DELETE')       
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                if assertion_status_ != log.PASS:                 
                    continue           
                                           
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.27

###################################################################################################
# Name: Assertion_6_4_30(self, log)                                               
# Description:     
# Method: DELETE ~ try to modify a service that does not support DELETE,
#               expected result 405 METHOD NOT ALLOWED	                                                        
###################################################################################################
def Assertion_6_4_30(self, log) :
 
    log.AssertionID = '6.4.30'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS:                 
            continue
        elif not headers:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
        else:
            # check if intended method is an allowable method for resource
            if not (self.allowable_method('DELETE', headers)):
                json_payload, headers, status = self.http_DELETE(relative_uris[relative_uri], rq_headers, authorization)
                assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_METHODNOTALLOWED, 'DELETE')       
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                if assertion_status_ != log.PASS:                 
                    continue           
                else:
                    #check if the url still exists and returns status 200 on GET
                    # could also check via etag
                    json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
                    assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                    if assertion_status_ != log.PASS:                 
                        log.assertion_log('line', "~ Resource %s might have been deleted unexpectedly" % (relative_uris[relative_uri]) )
                        continue                   

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.30

###################################################################################################
# Name: Assertion_6_4_31(self, log) Actions (POST)                                          
# Description:     
#      Services shall support the POST method for sending actions.
# Note: this assertion will issue a POST to clear the system event log with request body...	  
# If the actions property within a resource does not specify a target property, then the URI of an 
# action shall be of the form: ResourceUri/Actions/QualifiedActionName                                                      
###################################################################################################

def Assertion_6_4_31(self, log) :

    log.AssertionID = '6.4.31'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_body = {'Action': 'ClearLog'}
    rq_headers = self.request_headers()
    root_link_key = 'Managers'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        members = self.get_resource_members(self.sut_toplevel_uris[root_link_key]['url'])                
        for json_payload_systems, headers in members:
            # perfcorm the POST ~ clear the system log..
            if 'LogServices' not in json_payload_systems:
                assertion_status = log.WARN
                log.assertion_log('line', "~ Expected LogServices in payload of %s  ~ Not found" % (json_payload_systems['@odata.id']))
            else:
                sub_members = self.get_resource_members(json_payload_systems['LogServices']['@odata.id'])
                #get members    
                for json_payload, headers in sub_members:
                    if 'Actions' in json_payload:
                        log.assertion_log('line', 'Action %s found' % (json_payload['Actions']['#LogService.ClearLog']['target']))
                        log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s' % (json_payload['@odata.id'], rq_body))  
                        json_payload_, headers_, status_ = self.http_POST(json_payload['@odata.id'], rq_headers, rq_body, authorization)
                        print('The status of POST method is %s' %status_)
                        assertion_status_ = self.response_status_check(json_payload['@odata.id'], status_, log, request_type = 'POST')          
                        # manage assertion status
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        if assertion_status_ != log.PASS:                 
                            log.assertion_log('line', 'POST on action %s at url %s failed' % (json_payload['Actions']['#LogService.ClearLog']['target'], json_payload['@odata.id']))
                            continue
                    else:
                        assertion_status_ = log.WARN
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        log.assertion_log('line', ('Could not find any action with target in resource %s' % (json_payload['@odata.id']) ))

    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.31

###################################################################################################
# Name: Assertion_6_4_32(self, log) Actions (POST)                                          
# Description:     
#   Custom actions are requested on a resource by sending the HTTP POST method to the URI of the 
#   action. If the actions property within a resource does not specify a target property, then the 
#   URI of an action shall be of the form: ResourceUri/Actions/QualifiedActionName- Tried checking with Dell Server		                                               
###################################################################################################

def Assertion_6_4_32(self, log) :

    log.AssertionID = '6.4.32'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    rq_body = {'ResetType': 'ForceOff'}
    root_link_key = 'Systems'
    
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        members = self.get_resource_members(self.sut_toplevel_uris[root_link_key]['url'])               
        for json_payload, headers in members:
            # perfcorm the POST ~ clear the system log..
            action_url= '/redfish/v1/Systems/System.Embedded.1'
            if 'Actions' in json_payload:
                       log.assertion_log('line', 'Action %s found' % (json_payload['Actions']['#ComputerSystem.Reset']['target']))
                       log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s' % (json_payload['Actions']['#ComputerSystem.Reset']['target']))  
                       json_payload_, headers_, status_ = self.http_POST(json_payload['Actions']['#ComputerSystem.Reset']['target'], rq_headers, rq_body, authorization)
                       assertion_status_ = self.response_status_check(json_payload['Actions']['#ComputerSystem.Reset']['target'], status_, log, request_type = 'POST')      
                       # manage assertion status
                       assertion_status = log.status_fixup(assertion_status,assertion_status_)
                       print('JSON payload %s is failing' %json_payload_)
                       print('Headers is %s' %headers_)
                       if assertion_status_ != log.PASS:                 
                           log.assertion_log('line', 'POST on action url %s failed' % (json_payload['Actions']['#ComputerSystem.Reset']['target']))
                           continue
                       else:

                           assertion_status_ = log.WARN
                           assertion_status = log.status_fixup(assertion_status,assertion_status_)
                           log.assertion_log('line', ('Could not find any action with target in resource %s' % (json_payload['@odata.id']) ))
                     
            else:

                assertion_status = log.WARN
                log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6_4_32

###################################################################################################
# Name: Assertion_6_4_32_old(self, log) Actions (POST)                                          
# Description:     
#   Custom actions are requested on a resource by sending the HTTP POST method to the URI of the 
#   action. If the actions property within a resource does not specify a target property, then the 
#   URI of an action shall be of the form: ResourceUri/Actions/QualifiedActionName		                                               
###################################################################################################
def Assertion_6_4_32_old(self, log) :

    log.AssertionID = '6.4.32.old'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()

    root_link_key = 'Managers'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        members = self.get_resource_members(self.sut_toplevel_uris[root_link_key]['url'])               
        for json_payload_systems, headers in members:
            # perfcorm the POST ~ clear the system log..
            action_url= json_payload_systems['LogServices']['@odata.id']
            if 'LogServices' not in json_payload_systems:
                assertion_status= log.WARN
                log.assertion_log('line', "~ Expected LogServices in payload of %s  ~ Not found" % (json_payload_systems['@odata.id']))
            else:
                sub_members = self.get_resource_members(action_url)
                #get members    
                for json_payload, headers in sub_members:
                    if 'Actions' in json_payload:
                        log.assertion_log('line', 'Action %s found' % (json_payload['Actions']['#LogService.ClearLog']['target']))
                        log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s' % (json_payload['Actions']['#LogService.ClearLog']['target']))  
                        json_payload_, headers_, status_ = self.http_POST(json_payload['Actions']['#LogService.ClearLog']['target'], rq_headers, None, authorization)
                        assertion_status_ = self.response_status_check(json_payload['Actions']['#LogService.ClearLog']['target'], status_, log, request_type = 'POST')      
                        # manage assertion status
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        print('JSON payload %s is failing' %json_payload_)
                        print('Headers is %s' %headers_)
                        if assertion_status_ != log.PASS:                 
                            log.assertion_log('line', 'POST on action url %s failed' % (json_payload['Actions']['#LogService.ClearLog']['target']))
                            continue
                    else:
                        assertion_status_ = log.WARN
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        log.assertion_log('line', ('Could not find any action with target in resource %s' % (json_payload['@odata.id']) ))
                         
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.32_old

###################################################################################################
# Name: Assertion_6_4_2_1(self, log)                                               
# Description:                                                  
# 	application/json shall be supported for requesting resources and application/xml shall be 
#   supported for requesting metadata. This assertion checks only the xml case for $metadata... 
###################################################################################################
def Assertion_6_4_2_1(self, log) :

    from xml.etree import ElementTree as ET

    log.AssertionID = '6.4.2.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    #   Service metadata does not require authentication
    authorization = 'off'

    rq_headers = self.request_headers()
    rq_headers['Accept'] = rf_utility.accept_type['xml']

    json_payload, headers, status = self.http_GET(self.Redfish_URIs['Service_Metadata_Doc'], rq_headers, authorization)
    log.assertion_log('line', "~ GET %s with Accept type '%s'" % (self.Redfish_URIs['Service_Metadata_Doc'], rf_utility.accept_type['xml']))
    assertion_status_ = self.response_status_check(self.Redfish_URIs['Service_Metadata_Doc'], status, log)         
    # manage assertion status
    assertion_status = log.status_fixup(assertion_status,assertion_status_)
    if assertion_status_ != log.PASS:                 
        pass
    else:   
        # check1: the response header should have the content type xml as requested    
        if rf_utility.accept_type['xml'] not in headers['content-type']:
            assertion_status = log.FAIL
            log.assertion_log('line', "Service did not support the Accept request for %s for %s" % (rf_utility.accept_type['xml'], self.Redfish_URIs['Service_Metadata_Doc']))

        #check2: the content returned in response body should be xml, validate it by parsing
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (self.Redfish_URIs['Service_Metadata_Doc']))
        else:
            try:
                xml = ET.fromstring(json_payload)
                if xml is None:
                    assertion_status = log.FAIL
                    log.assertion_log('line', "Service did not support the Accept request for %s for %s" % (rf_utility.accept_type['xml'], self.Redfish_URIs['Service_Metadata_Doc']))
            except ET.ParseError as e:
                assertion_status = log.FAIL
                log.assertion_log('line', "XML parse error for %s, exception: %s" % (
                                  self.Redfish_URIs['Service_Metadata_Doc'], e))

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.2.1

###################################################################################################
# Name: Assertion_6_4_2_2(self, log)   Request header : Content type                                    
# Description:                                                  
# 	charset=utf-8 shall be supported and required if there is a request body.
# Method:
#   First check POST without content type, should Fail, then try POST with content type, should PASS
#   try POST then PATCH as they both have request body should just be check against status 
#   HTTP_MEDIATYPENOTSUPPORTED to avoid checking bad request due to request body
###################################################################################################
def Assertion_6_4_2_2(self, log) :

    log.AssertionID = '6.4.2.2'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    header_name = 'Content-Type'

    rq_headers = self.request_headers()
    # get the collection of user accounts...
    user_name = 'xxuserxx'

    root_link_key = 'SessionService'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris[root_link_key]['url'], rq_headers, authorization)
        assertion_status_ = self.response_status_check(self.sut_toplevel_uris[root_link_key]['url'], status, log)           
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS:                 
            pass
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (self.sut_toplevel_uris[root_link_key]['url']))
        else:
            ## get Sessions collection from payload
            try :
                key = 'Sessions'
                acc_collection = (json_payload[key])['@odata.id']
            except :
                assertion_status = log.WARN
                log.assertion_log('line', "~ \'Sessions\' not found in the payload from GET %s" % (self.sut_toplevel_uris[root_link_key]['url']))    
            else:         
                ## Found the key in the payload, try a GET on the link for a response header
                json_payload, headers, status = self.http_GET(acc_collection, rq_headers, authorization)
                assertion_status_ = self.response_status_check(acc_collection, status, log)      
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                if assertion_status_ != log.PASS: 
                    pass
                else:
                    # check if intended method is an allowable method for resource
                    if (self.allowable_method('POST', headers) != True):      
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for POST" % acc_collection)
                        log.assertion_log('line', rf_utility.json_string(headers))
                    else:
                        #check if user already exists, if it does perfcorm a delete to clean up
                        members = self.get_resource_members(acc_collection)
                        for json_payload, headers in members:
                            if json_payload['UserName'] == user_name:    
                                log.assertion_log('TX_COMMENT', "~ note: the %s account pre-exists... deleting it now in prep for creation" % json_payload['UserName'])   
                                # check if intended method is an allowable method for resource
                                if (self.allowable_method('DELETE', headers)):         
                                    json_payload_, headers_, status_ = self.http_DELETE(json_payload['@odata.id'], rq_headers, authorization)
                                    assertion_status_ = self.response_status_check(json_payload['@odata.id'], status_, log, request_type = 'DELETE')      
                                    # manage assertion status
                                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                    if assertion_status_ != log.PASS: 
                                        break
                                else:
                                    assertion_status = log.FAIL
                                    log.assertion_log('line', "~ The response headers for %s do not indicate support for DELETE" % acc_collection)
                                    log.assertion_log('line', "~ Item %s already exists in %s and attempt to request DELETE failed, Try changing item configuration in the script" % (user_name, acc_collection))
                                    break
                        
                    if (assertion_status == log.PASS) : # Ok to create the session now
                        deleted =  False
                        rq_body = {'UserName' : user_name, 'Password' : '12345' }
                        #1. try POST without Content-Type, should FAIL    
                        rq_headers = dict()
                        rq_headers['Accept'] = rf_utility.accept_type['json']
                        rq_headers['odata-version'] = '4.0'                   
                        log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s and wihtout content type in request headers' % (acc_collection, rq_body))                     
                        json_payload, headers, status = self.http_POST(acc_collection, rq_headers, rq_body, authorization)
                        if not status:
                            assertion_status = log.WARN
                        elif (status == rf_utility.HTTP_CREATED):
                            assertion_status = log.FAIL
                            log.assertion_log('line', "POST (%s) with headers %s WITHOUT the required header %s : %s" % (rf_utility.HTTP_status_string(status), rq_headers ,header_name, rf_utility.content_type['utf8']))                 
                            try: 
                                account_url = headers['location']
                            except:
                                assertion_status = log.FAIL
                                log.assertion_log('line', "Location in header of POST expected ~ not found")
                            #delete it 
                            else:       
                                json_payload_, headers_, status_ = self.http_DELETE(account_url, rq_headers, authorization)
                                assertion_status_ = self.response_status_check(account_url, status, log, request_type = 'DELETE')      
                                # manage assertion status
                                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                if assertion_status_ != log.PASS: 
                                    log.assertion_log('line', "~ Item %s already exists in %s and attempt to request DELETE failed, Try changing item configuration in the script" % (user_name, acc_collection))
                                    log.assertion_log('line', "~ Assertion to test request body with header %s could not be completed" %(rf_utility.content_type['utf8']))
                                else: 
                                    deleted = True
                                    log.assertion_log('XL_COMMENT', "~ note: DELETE %s PASS" % (account_url))  
                                                                                 
                        # TODO check json+payload for roleid, is the reason why it did not pass was content-type or property not found?
                        if deleted:
                            #2. try POST with rf_utility.content_type['utf8'], should PASS
                            rq_headers['Content-Type'] = rf_utility.content_type['utf8']
                            log.assertion_log('line', "Requesting POST (%s) WITH the required header %s : %s and request body %s" % (acc_collection, header_name, rf_utility.content_type['utf8'], rq_body))
                            json_payload, headers, status = self.http_POST(acc_collection, rq_headers, rq_body, authorization)
                            assertion_status_ = self.response_status_check(acc_collection, status, log, rf_utility.HTTP_CREATED, 'POST')      
                            # manage assertion status
                            assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                                                                                 
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.2.2

###################################################################################################
# Name: Assertion_6_4_2_3(self, log)                                               
# Description:                                                  
# 	Services shall reject requests which specify an unsupported OData version.
###################################################################################################
def Assertion_6_4_2_3(self, log) :

    log.AssertionID = '6.4.2.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    relative_uris = self.relative_uris

    rq_headers = self.request_headers()
    header = 'odata-version'

    for relative_uri in relative_uris:
        #supported version
        version = '4.0'
        rq_headers[header] = version
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)     
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS:        
            continue
        if header in (h.lower() for h in headers):
            if version not in headers[header]:
                assertion_status = log.WARN
                log.assertion_log('line', "~ Response Header %s with value %s expected: found %s" % (header, version, headers[header]))

    for relative_uri in relative_uris:
        assertion_status_ = log.PASS
        #unsupported version
        version = '3.0'
        rq_headers[header] = version
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        if not status:
            assertion_status_ = log.WARN
        elif (status == rf_utility.HTTP_OK) :
            assertion_status_ = log.FAIL
            log.assertion_log('line', "~ GET: %s HTTP status %s:%s with request header: %s and incorrect value: %s passed, which is an unexpected behavior" % (relative_uris[relative_uri], status, rf_utility.HTTP_status_string(status), header, version))
        elif status == rf_utility.HTTP_NOT_FOUND:
            assertion_status_ = log.INCOMPLETE
            log.assertion_log('TX_COMMENT',"WARN: GET %s failed : HTTP status %s:%s" % (relative_uris[relative_uri], status, rf_utility.HTTP_status_string(status)) )  
       # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.2.3

###################################################################################################
# Name: Assertion_6_4_2_4(self, log)                                               
# Description:                                                  
# 	Services shall reject requests whithout BASIC authorization header
###################################################################################################
def Assertion_6_4_2_4(self, log) :

    log.AssertionID = '6.4.2.4'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    
    relative_uris = self.relative_uris
    header = 'Authorization'

    for relative_uri in relative_uris:
        assertion_status_ = log.PASS 
        #/redfish/v1/ can be requested without auth
        if relative_uris[relative_uri] == '/redfish/v1/':
            continue
        rq_headers = self.request_headers()
        authorization = 'on'
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        if not status:
            assertion_status_ = log.WARN
            continue
        elif (status == rf_utility.HTTP_UNAUTHORIZED):
            assertion_status_ = log.FAIL
            log.assertion_log('line', "~ GET: %s  HTTP status %s:%s with header: %s:%s and valid credentials failed" % (relative_uris[relative_uri], status, rf_utility.HTTP_status_string(status), header, authorization))
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status, assertion_status_)              
        # commenting out the following, service stops responding shortly after serveral wrong credential attempts..
        '''
        rq_headers = self.request_headers()
        authorization = 'off'
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        if not status:
            assertion_status = log.WARN
            continue
        if (status != rf_utility.HTTP_UNAUTHORIZED):
            assertion_status = log.FAIL
            log.assertion_log('line', "~ GET: %s HTTP status %s:%s with header: %s:%s passed which is an unexpected behaviour" % (relative_uris[relative_uri], status, rf_utility.HTTP_status_string(status), header, authorization))
        

        rq_headers = self.request_headers()
        rf_utility.http__set_auth_header(rq_headers, 'wrongid', 'wrongpass')
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        if not status:
            assertion_status = log.WARN
            continue
        if (status != rf_utility.HTTP_UNAUTHORIZED):
            assertion_status = log.FAIL
            log.assertion_log('line', "~ GET: %s HTTP status %s:%s with header: %s and invalid credentials passed which is an unexpected behaviour" % (relative_uris[relative_uri], status, rf_utility.HTTP_status_string(status), header))
        '''
    log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion 6.4.2.4

###################################################################################################
# Name: Assertion_6_4_2_5(self, log)   WIP    Specification requirement changes                                        
# Description:                                                  
# 	Services shall be able to understand and process User-Agent Request Header.  
###################################################################################################
def Assertion_6_4_2_5(self, log) :

    log.AssertionID = '6.4.2.5'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    relative_uris = self.relative_uris

    rq_headers = self.request_headers()
    header = 'User-Agent'
    rq_headers[header] = ''

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
            
    log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion 6.4.2.5

###################################################################################################
# Name: Assertion_6_4_2_6(self, log)   WIP    Specification requirement changes                                              
# Description:                                                  
# 	Services shall be able to understand and process 'Host' in the request header.
###################################################################################################
def Assertion_6_4_2_6(self, log) :

    log.AssertionID = '6.4.2.6'

    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    relative_uris = self.relative_uris

    rq_headers = self.request_headers()
    header = 'Host'
    rq_headers[header] = self.SUT_prop['DnsName']

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
    
    log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion 6.4.2.6

###################################################################################################
# Name: Assertion_6_5_1(self, log)   Response Headers                                            
# Description:               
# Redfish services shall be able to return the headers in the following table 
# as defined by the HTTP 1.1 specification if the value in the Required column is set to "yes" .  
# Requesting a GET in this assertion
# -OdataVersion
# -Content-Type
# -Server
# -Link-header (found link)
# -cache-control
# -Access Control ~ Allow-origin (found x-frame-options with origin response) 
# -Allow : returned on GET or HEAD
# -www-authenticate
###################################################################################################
def Assertion_6_5_1(self, log) :

    log.AssertionID = '6.5.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    relative_uris = self.relative_uris

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue                
        else:
            assertion_status = response_header_check(headers, relative_uris[relative_uri], log)       

    if (assertion_status == log.WARN or assertion_status == log.FAIL):
        log.assertion_log('line', "~ One or more WARNings or FAILures has occured ~ check the %s file for details" % log.TextLogPath)

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.1



###################################################################################################
# Name: response_header_check(headers, url) 
# params: headers : reponse header 
#         url : The resource to which the reponse header belongs                                            
# Description:               
#   Check the response header for required, conditional and additional headers FAIL if any required 
#   header is not foundAdvisory WARN if any header not in the response header table in spec is found
###################################################################################################
def response_header_check(headers, url, log):
    required_headers = ['odata-version', 'content-type', 'server', 'link', 'cache-control', 'allow']
    conditional_headers = ['etag', 'location']
    additional_headers = ['content-encoding', 'content-length', 'via', 'max-forwards']
    # what we think is required in context
    # example: http://pretty-rfcc.herokuapp.com/rfcC2617 : The 401 (Unauthorized) 
    # response message is used by an origin server to challenge the authorization of a user agent. 
    # This response MUST include a WWW-Authenticate header field containing at least one challenge applicable to the requested resource
    # x-auth-token: if there is a session
    # access-control-allow-origin : Not so sure, found x-frame-options with origin response
    # Prevents or allows requests based on originating domain. Used to prevent CSrfc attacks.
    contextual_headers = ['access-control-allow-origin', 'www-authenticate', 'x-auth-token']

    assertion_status = log.PASS
    assertion_status_1 = log.PASS
    assertion_status_2 = log.PASS

    #check on root then check on top level links
    for req_header in required_headers:
        # normalize
        if req_header not in (h.lower() for h in headers):
            assertion_status_1 = log.FAIL
            #TX_COMMENT only gets written to the text log file..
            log.assertion_log('TX_COMMENT', "FAIL: Required header[%s] expected but not found in response header of resource %s" % (req_header, url))
    for cond_header in conditional_headers:
        if cond_header in headers:
            log.assertion_log('TX_COMMENT','Note: Conditional header[%s] found in response header of resource %s' %(cond_header, url))
    for add_header in additional_headers:
        if add_header in headers:
            log.assertion_log('TX_COMMENT','Note: header[%s] found in response header of resource %s' %(add_header, url))
    for cxt_header in contextual_headers:
        if cxt_header in headers:
            log.assertion_log('TX_COMMENT','Note: header[%s] found in response header of resource %s' %(cxt_header, url))
    for header in headers:
        if header.lower() not in required_headers and header.lower() not in conditional_headers and header.lower() not in additional_headers:
            assertion_status_2 = log.WARN
            log.assertion_log('TX_COMMENT', "WARN: header[%s] not expected but found in response header of resource %s" % (header, url))

    #Check status, FAIL takes precedence, the WARN, then PASS
    assertion_status = assertion_status_1 if (assertion_status_1 == log.FAIL or assertion_status_1 == log.WARN) else assertion_status_2 
    return assertion_status

# End response_header_check

###################################################################################################
# Name: Assertion_6_5_2_6(self, log)                                               
# Description:     
#	Location
#   Conditional
#   rfcC 2616, Section 14.30
#   Indicates a URI that can be used to request a representation of the resource.
#   Shall be returned if a new resource was created.            
###################################################################################################
def Assertion_6_5_2_6(self, log):

    log.AssertionID = '6.5.2.6'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    #1. new resource creation, create user account
    # get the collection of user accounts...
    response_key = 'location'
    user_name = 'testuser'
    root_link_key = 'AccountService'

    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris[root_link_key]['url'], rq_headers, authorization)
        assertion_status_ = self.response_status_check(self.sut_toplevel_uris[root_link_key]['url'], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            pass
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (self.sut_toplevel_uris[root_link_key]['url']))
        else:
            ## get Accounts collection from payload
            try :
                key = 'Accounts'
                acc_collection = (json_payload[key])['@odata.id']
            except :
                assertion_status = log.WARN
                log.assertion_log('line', "~ \'Accounts\' not found in the payload from GET %s" % (self.sut_toplevel_uris[root_link_key]['url']))    
            else:
                json_payload, headers, status = self.http_GET(acc_collection, rq_headers, authorization)
                assertion_status_ = self.response_status_check(acc_collection, status, log)      
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                if assertion_status_ != log.PASS: 
                    pass     
                else:
                    # check if intended method is an allowable method for resource
                    if (self.allowable_method('POST', headers) != True):      
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for POST" % acc_collection)
                        log.assertion_log('line', rf_utility.json_string(headers))
                    else:
                        #check if user already exists, if it does perfcorm a delete to clean up
                        members = self.get_resource_members(acc_collection)
                        for json_payload, headers in members:
                            if json_payload['UserName'] == user_name:       
                                log.assertion_log('TX_COMMENT', "~ note: the %s account pre-exists... deleting it now in prep for creation" % json_payload['UserName'])   
                                # check if intended method is an allowable method for resource
                                if (self.allowable_method('DELETE', headers)):         
                                    json_payload_, headers_, status_ = self.http_DELETE(json_payload['@odata.id'], rq_headers, authorization)
                                    assertion_status_ = self.response_status_check(json_payload['@odata.id'], status_, log, request_type = 'DELETE')      
                                    # manage assertion status
                                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                    if assertion_status_ != log.PASS: 
                                        break
                                    else: 
                                        log.assertion_log('XL_COMMENT', "~ note: DELETE for %s : %s PASS" % (user_name, json_payload['@odata.id']))
                                        break
                                else:
                                    assertion_status = log.FAIL
                                    log.assertion_log('line', "~ The response headers for %s do not indicate support for DELETE" % json_payload['@odata.id'])
                                    log.assertion_log('line', "~ Item already exists in %s and attempt to request DELETE failed, Try changing item configuration in the script" % json_payload['@odata.id'])
                                    break
                        
                    if (assertion_status == log.PASS) : # Ok to create the user now                                   
                        rq_body = {'UserName' : 'testuser' , 'Password' : 'testpass' , 'RoleId' : 'Administrator' }    
                        log.assertion_log('TX_COMMENT', 'Requesting POST for resource %s with request body %s' % (acc_collection, rq_body))                                                         
                        json_payload, headers, status = self.http_POST(acc_collection, rq_headers, rq_body, authorization)
                        assertion_status_ = self.response_status_check(acc_collection, status, log, rf_utility.HTTP_CREATED , request_type = 'POST')      
                        # manage assertion status
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        if assertion_status_ != log.PASS:                           
                            log.assertion_log('line', "~ note: %s in headers for POST for resource %s could not be verified" % (response_key, acc_collection))
                                             
                        else:
                            response_key = 'location'
                            if response_key not in headers:
                                assertion_status = log.FAIL
                                log.assertion_log('line', "~ note: Post for object creation for resource %s : %s expected %s in headers ~ not found" % (user_name, acc_collection, response_key))
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.2.6


###################################################################################################
# Name: Assertion_6_5_2_6_1(self, log)                                               
# Description:     
#	Location   Conditional  rfcC 2616, Section 14.30
#   Indicates a URI that can be used to request a representation of the resource.
#   Location and X-Auth-Token shall be included on responses which create user sessions.            
###################################################################################################
def Assertion_6_5_2_6_1(self, log):

    log.AssertionID = '6.5.2.6.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    #2.creation of user sessions   
    root_link_key = 'SessionService'

    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris[root_link_key]['url'], rq_headers, authorization)
        assertion_status_ = self.response_status_check(self.sut_toplevel_uris[root_link_key]['url'], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            pass  
        elif not json_payload:
            assertion_status_ = log.WARN
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (self.sut_toplevel_uris[root_link_key]['url']))
        else:
            #get sessions
            if 'Sessions' not in json_payload:
                 assertion_status = log.FAIL
                 log.assertion_log('line', "~ Sessions expected in the response payload of %s ~ not found" % ( self.sut_toplevel_uris[root_link_key]['url']))
            else:
                try:
                    sessions_url = json_payload['Sessions']['@odata.id']
                except:
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ Sessions expected in the response payload of %s ~ not found" % ( self.sut_toplevel_uris[root_link_key]['url']))
                else:
                    json_payload, headers, status = self.http_GET(sessions_url, rq_headers, authorization)
                    assertion_status_ = self.response_status_check(sessions_url, status, log)      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                    if assertion_status_ != log.PASS: 
                        pass  
                    else:
                        authorization = 'off'
                        rq_headers = self.request_headers()
                        response_key = 'location'
                        rq_body = {'UserName': self.SUT_prop['LoginName'], 'Password': self.SUT_prop['Password']}
                        rq_headers['Content-Type'] = 'application/json'
                        log.assertion_log('TX_COMMENT', 'Requesting POST for resource %s with request body %s' % (sessions_url, rq_body))    
                        json_payload, headers, status = self.http_POST(sessions_url, rq_headers, rq_body, authorization)
                        assertion_status_ = self.response_status_check(sessions_url, status, log, rf_utility.HTTP_CREATED , request_type = 'POST')      
                        # manage assertion status
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        if assertion_status_ != log.PASS:    
                            log.assertion_log('line', "~ note: %s in headers for POST for resource %s could not be verified" % (response_key, sessions_url))  
                            pass  
                        else:
                            #session created
                            if response_key not in headers:
                                assertion_status = log.FAIL
                                log.assertion_log('line', "~ note: Post for object creation for resource %s expected %s in headers ~ not found" % (sessions_url, response_key))
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.2.6.1

###################################################################################################
# Name: Assertion_6_5_3(self, log)                                               
# Description:               
# Redfish services shall be able to return the headers in the following table as defined by the
# HTTP 1.1 specification if the value in the Required column is set to "yes" .                                  
# 	link header: a Link header satisfying rel=describedby shall be returned on GET and HEAD.
#   In addition to links from the resource, the URL of the JSON schema for the resource shall be
#   returned with a `rel=describedby`
###################################################################################################
def Assertion_6_5_3(self, log) :

    log.AssertionID = '6.5.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    relative_uris = self.relative_uris
    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uri, rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uri, status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue         
        else:
            key = 'Link'
            if key not in headers:
               assertion_status = log.FAIL
               log.assertion_log('line', "Header %s required but not found in response header GET ~ %s : FAIL" % (key, relative_uri))
               log.assertion_log('line', rf_utility.json_string(headers))
            else:
                #link = re.search(r"<.*?(.json/>)", headers[key]).group()
                if 'rel=describedby' not in headers[key]:
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ GET~ %s expected a json url link followed by rel=describedby in response header" % (relative_uri))
                    log.assertion_log('line', rf_utility.json_string(headers))

        json_payload, headers, status = self.http_HEAD(relative_uri, rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uri, status, log)
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue 
        else:
            key = 'Link'
            if key not in headers:
               assertion_status = log.FAIL
               log.assertion_log('line', "Header %s required but not found in response header HEAD ~ %s : FAIL" % (key, relative_uri))
               log.assertion_log('line', rf_utility.json_string(headers))
            elif 'rel=describedby' not in headers[key]:
                assertion_status = log.FAIL
                log.assertion_log('line', "~ HEAD~ %s expected a json url link followed by rel=describedby in response header" % (relative_uri))
                log.assertion_log('line', rf_utility.json_string(headers))
    
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.3

###################################################################################################
# Name: Assertion_6_5_6_2(self, log)                                               
# Description:               
# Status Code: 200 OK The request was successfully completed and includes a representation in its body.
###################################################################################################
def Assertion_6_5_6_2(self, log) :

    log.AssertionID = '6.5.6.2'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    relative_uris = self.relative_uris

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue   
                    
        elif json_payload is None:
            assertion_status = log.FAIL
            log.assertion_log('line', "GET with status %s, response body not found ~ %s" % (status, relative_uris[relative_uri]))

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.6.2

###################################################################################################
# Name: Assertion_6_5_6_3(self, log)    WIP                                           
# Description:     
#	Status Code:	201 Created
# A request that created a new resource completed successfully. The Location header shall be set to
# the canonical URI for the newly created resource. A representation of the newly created resource
# may be included in the response body. Accounts POST and sessions POST covered in 6.1.8.1 
###################################################################################################           

def Assertion_6_5_6_3(self, log) :

    log.AssertionID = '6.5.6.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    
    return (assertion_status)
#
## end Assertion 6.5.6.3

###################################################################################################
# Name: Assertion_6_5_6_5(self, log)                                               
# Description:               
# Status Code:  204 No Content
# The request succeeded, but no content is being returned in the body of the response.
###################################################################################################

def Assertion_6_5_6_5(self, log) :

    log.AssertionID = '6.5.6.5'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    rq_headers = self.request_headers()
    relative_uris = self.relative_uris
    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uri, rq_headers, authorization)
        if status == 204:
            print('The request for te resource %s has succeeded, but no content is being returned in the body of the response' %relative_uri)
            continue
    
        else :
            continue

    log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion 6.5.6.5

###################################################################################################
# Name: Assertion_6_5_6_6(self, log)                                               
# Description:               
# Status Code:  301 Moved Permanently The requested resource resides under a different URI
###################################################################################################
def Assertion_6_5_6_6(self, log) :

    log.AssertionID = '6.5.6.6'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()

    relative_uris = self.relative_uris
    response = None

    for relative_uri in relative_uris:
        url_redirect = relative_uris[relative_uri][:-1]                    
        response = rf_utility.http__req_resp(self.SUT_prop, 'GET', url_redirect, rq_headers, None, authorization)
        if not response:
            assertion_status_ = log.WARN
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
        else:
            # check for redirect... 
            assertion_status_ = self.response_status_check(url_redirect, response.status, log, rf_utility.HTTP_MOVEDPERMANENTLY)      
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            if assertion_status_ != log.PASS: 
                continue 
            else:
                try:
                    redirect_location = response.getheader('location')               
                except:
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ Expected Location in the headers of GET: %s with status %s:%s, not found" %(url_redirect,response.status, rf_utility.HTTP_status_string(response.status)))
                    log.assertion_log('line', rf_utility.json_string(rq_headers))

    log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion 6.5.6.6

###################################################################################################
# Name: Assertion_6_5_6_8(self, log)                                               
# Description:     
# Method: POST ~ 304 Not Modified
###################################################################################################		                                                        

def Assertion_6_5_6_8(self, log) :
 
    log.AssertionID = '6.5.6.8'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    root_link_key = 'AccountService'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris[root_link_key]['url'], rq_headers, authorization)
        assertion_status_ = self.response_status_check(self.sut_toplevel_uris[root_link_key]['url'], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            pass
        elif not json_payload:
            assertion_status = log.WARN
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (self.sut_toplevel_uris[root_link_key]['url']))
        else:
            ## get Accounts collection from payload
            try :
                key = 'Accounts'
                acc_collection = (json_payload[key])['@odata.id']
            except :
                assertion_status = log.WARN
                log.assertion_log('line', "~ \'Accounts\' not found in the payload from GET %s" % (self.sut_toplevel_uris[root_link_key]['url']))
    
            else:            
                ## Found the key in the payload, try a GET on the link for a response header 
                json_payload, headers, status = self.http_GET(acc_collection, rq_headers, authorization)
                assertion_status_ = self.response_status_check(acc_collection, status, log)      
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                if assertion_status_ != log.PASS: 
                    pass
                    # check if intended method is an allowable method for resource  
                elif not (self.allowable_method('POST', headers)):
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for POST" % acc_collection)
                    log.assertion_log('line', rf_utility.json_string(headers))
                else:
                    members = self.get_resource_members(acc_collection)
                    for json_payload, headers in members:
                        if 'etag' not in headers:
                            assertion_status = log.WARN
                            log.assertion_log('line', "~ note: Etag exepcted in headers of %s: %s ~ not found" %(json_payload['@odata.id'], rf_utility.json_string(headers))) 
                            log.assertion_log('line', "~ note: Modifications to resource using If-None-Match header without Etag cannot be tested")
                        else:
                            etag = headers['etag']
                            rq_headers = self.request_headers()
                            rq_headers['If-None-Match'] = etag
                            json_payload_, headers_, status_ = self.http_GET(json_payload['@odata.id'], rq_headers, authorization)
                            assertion_status_ = self.response_status_check(json_payload['@odata.id'], status_, log, rf_utility.HTTP_NOTMODIFIED)      
                            # manage assertion status
                            assertion_status = log.status_fixup(assertion_status,assertion_status_)
                            if assertion_status_ != log.PASS: 
                                log.assertion_log('XL_COMMENT', ('Checked if resource is modified using If-None-Match header and etag' ))
                                continue
                            else:
                                log.assertion_log('XL_COMMENT', "~ POST : status code %s as expected" % (status) )   
                                log.assertion_log('XL_COMMENT', ('Checked if resource is modified using If-None-Match header and etag' ))

    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )                    

    log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion 6.5.6.8

###################################################################################################
# Name: Assertion_6_5_6_9(self, log)                                               
# Description: 
# 400 Bad Request
# The request could not be processed because it contains missing or invalid information 
# (such as validation error on a field, a missing required value, and so on).
# An extended error shall be returned in the response body, as defined in section Extended Error Handling.                                                 
###################################################################################################
def Assertion_6_5_6_9(self, log) :

    log.AssertionID = '6.5.6.9'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    
    authorization = 'off' # this prevents the http__GET() from setting an authorization header and overwriting the 'wrongid' one set below
    relative_uris = self.relative_uris
    rq_headers = self.request_headers()
    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        query_url = json_payload['@odata.id'][:-1]
        json_payload, headers, status = self.http_GET(query_url, rq_headers, authorization)
        assertion_status_ = self.response_status_check(query_url, status, log, rf_utility.HTTP_NOT_FOUND)          
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        print('Got a 404 status for a bad request for the url %s' %query_url)
        log.assertion_log(assertion_status, None)
        return assertion_status

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.6.9
###################################################################################################

# Name: Assertion_6_5_6_10(self, log)                                               
# Description:                                                  
# 	401 Unauthorized 
#   The authentication credentials included with this request are missing or invalid
###################################################################################################
def Assertion_6_5_6_10(self, log) :

    log.AssertionID = '6.5.6.10'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    
    authorization = 'off' # this prevents the http__GET() from setting an authorization header and overwriting the 'wrongid' one set below
    header = 'authorization'
    relative_uris = self.relative_uris

    for relative_uri in relative_uris:
        #/redfish/v1/ can be requested without auth
        if relative_uris[relative_uri] == '/redfish/v1/':
            continue
        rq_headers = self.request_headers()
        log.assertion_log('line', 'Requesting GET %s without header %s... ' % (relative_uris[relative_uri], header))
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_UNAUTHORIZED)
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
       
        rq_headers = self.request_headers()
        rf_utility.http__set_auth_header(rq_headers, 'wrongid', 'wrongpass')
        log.assertion_log('line', 'Requesting GET %s with invalid credentials for header %s... ' % (relative_uris[relative_uri], header))
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_UNAUTHORIZED)
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.6.10

###################################################################################################
# Name: Assertion_6_5_6_13(self, log)                                               
# Description:     
# 405 Method Not Allowed
# The HTTP verb specified in the request (e.g. DELETE, GET, HEAD, POST, PUT, PATCH) is not supported 
# for this request URI. The response shall include an Allow header which provides a list of methods 
# that are supported by the resource identified by the Request-URI.        
###################################################################################################              
def Assertion_6_5_6_13(self, log) :
 
    log.AssertionID = '6.5.6.13'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    relative_uris = self.relative_uris

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue  
        else:
            # attempt to modify type... which should not be modifiable         
            rq_body = {'@odata.type' : 'RedfishService.x.y.z'}                  
            try:
                # check if intended method is an allowable method for resource
                if not (self.allowable_method('PATCH', headers)): 
                    json_payload, headers, status = self.http_PATCH(relative_uris[relative_uri], rq_headers, rq_body, authorization)
                    assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_METHODNOTALLOWED, 'PATCH')    
                    if 'allow' in headers:
                        print('Allow is present and the value is : %s' %headers['allow'])
                        print('Status is %s' %status)
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
            except:
                assertion_status_ = log.WARN
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                log.assertion_log('line', "~ ~ OPERATIONAL ERROR PATCH on resource %s" % (relative_uris[relative_uri] ))
            try:
                # check if intended method is an allowable method for resource
                if not (self.allowable_method('PUT', headers)):   
                    json_payload, headers, status = self.http_PUT(relative_uris[relative_uri], rq_headers, rq_body, authorization)
                    assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_METHODNOTALLOWED, 'PUT')      
                    
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
            except:
                assertion_status_ = log.WARN
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                log.assertion_log('line', "~ OPERATIONAL ERROR PUT on resource %s" % (relative_uris[relative_uri] ))
            try:
                # check if intended method is an allowable method for resource
                if not (self.allowable_method('POST', headers)): 
                    json_payload, headers, status = self.http_POST(relative_uris[relative_uri], rq_headers, rq_body, authorization)
                    assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_METHODNOTALLOWED, 'POST')      
                    
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
            except:
                assertion_status_ = log.WARN
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                log.assertion_log('line', "~ ~ OPERATIONAL ERROR POST on resource %s" % (relative_uris[relative_uri] ))
            try:
                # check if intended method is an allowable method for resource
                if not (self.allowable_method('DELETE', headers)):     
                    json_payload, headers, status = self.http_DELETE(relative_uris[relative_uri], rq_headers, authorization)
                    assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_METHODNOTALLOWED, 'DELETE')      
                    
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
            except:
                assertion_status_ = log.WARN
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)     
                log.assertion_log('line', "~ ~ OPERATIONAL ERROR DELETE on resource %s" % (relative_uris[relative_uri] ))

    log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion 6.5.6.13

###################################################################################################
# Name: Assertion_6_5_10(self, log)                                               
# Description:           OData Service Document    
# The OData Service Document shall be returned as a JSON object, using the MIME type application/json. 
# i.e the content type should be json..
###################################################################################################
def Assertion_6_5_10(self, log) :

    log.AssertionID = '6.5.10'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    url = self.Redfish_URIs['Service_Odata_Doc']

    rq_headers = self.request_headers()
    json_payload, headers, status = self.http_GET(url, rq_headers, authorization)
    assertion_status_ = self.response_status_check(url, status, log)      
    # manage assertion status
    assertion_status = log.status_fixup(assertion_status,assertion_status_)
    if assertion_status_ != log.PASS: 
        pass
    elif not json_payload:
        assertion_status = log.FAIL
        log.assertion_log('line', "Expected a json response from %s" %(url))

    elif 'content-type' not in headers or rf_utility.content_type['json'] not in headers['content-type']:
            assertion_status = log.FAIL
            log.assertion_log('line', "Expected a response headers with content type %s" %rf_utility.content_type['json'])

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.10

###################################################################################################
# Name: Assertion_6_5_11(self, log)                                               
# Description:    OData Service Document           
# The JSON object shall contain a context property named "@odata.context" with a value of
# "/redfish/v1/$metadata". This context tells a generic OData client how to find the service metadata 
# describing the types exposed by the service.
###################################################################################################
def Assertion_6_5_11(self, log) :

    log.AssertionID = '6.5.11'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    url = self.Redfish_URIs['Service_Odata_Doc']

    rq_headers = self.request_headers()
    json_payload, headers, status = self.http_GET(url, rq_headers, authorization)
    assertion_status_ = self.response_status_check(url, status, log)      
    # manage assertion status
    assertion_status = log.status_fixup(assertion_status,assertion_status_)
    if assertion_status_ != log.PASS: 
        pass
    elif not json_payload:
        assertion_status_ = log.WARN
         # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (url))
    else:
        key = '@odata.context'
        exp_value = "/redfish/v1/$metadata"
        if key not in json_payload:
            assertion_status = log.FAIL
            log.assertion_log('line', "Expected property %s in Odata service document json content " % (key) )
        elif json_payload[key] != exp_value:
            assertion_status = log.FAIL
            log.assertion_log('line', "Expected property %s with value %s in Odata service document json content, found: %s  " % (key, exp_value, json_payload[key]) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.11

###################################################################################################
# Name: Assertion_6_5_12(self, log)                                               
# Description:        OData Service Document       
# The JSON object shall include a property named "value" whose value is a JSON array containing an
# entry for the service root and each resource that is a direct child of the service root.
###################################################################################################
def Assertion_6_5_12(self, log) :

    log.AssertionID = '6.5.12'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    url = self.Redfish_URIs['Service_Odata_Doc']
    service_root = self.Redfish_URIs['Service_Root']

    rq_headers = self.request_headers()

    json_payload, headers, status = self.http_GET(url, rq_headers, authorization)
    assertion_status_ = self.response_status_check(url, status, log)      
    # manage assertion status
    assertion_status = log.status_fixup(assertion_status,assertion_status_)
    if assertion_status_ != log.PASS: 
        pass
    elif not json_payload:
        assertion_status_ = log.WARN
         # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (url))
    else:   
        value_found = False
        key = 'value'
        s_entry = 'Service'

        if key not in json_payload:               
            assertion_status = log.FAIL
            log.assertion_log('line', "Expected property %s not in %s " % (key, url) )

        else:
           # checking JSON array containing an entry for the service root
            if not any(s_entry in entry['name'] for entry in json_payload[key]):             
                assertion_status = log.FAIL
                log.assertion_log('line', "GET(%s) ~ Expected Service root resource \"%s\" in payload ~ not found" % (url, s_entry) )

            # checking if array contains each resource that is a direct child of the service root           
            for entries in self.sut_toplevel_uris:
                if not any(entries in entry['name'] for entry in json_payload[key]):    
                    assertion_status = log.FAIL
                    log.assertion_log('line', "GET(%s) ~ Expected Service root resource \"%s\" in payload ~ not found" % (url, entries) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.12

###################################################################################################
# Name: Assertion_6_5_13(self, log)                                            
# Description:         OData Service Document      
# Each entry shall be represented as a JSON object and shall include 
# a "name" property whose value is a user-friendly name of the resource,
# a "kind" property whose value is "Singleton" for individual resources
# (including collection resources) or "EntitySet" for top-level resource collections,
# TODO and a "url" property whose value is the relative URL for the top-level resource.- Did testing whether url contains the top-level resource which is -/redfish/v1/
###################################################################################################
def Assertion_6_5_13(self, log) :

    log.AssertionID = '6.5.13'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    url = self.Redfish_URIs['Service_Odata_Doc']

    rq_headers = self.request_headers()
    json_payload, headers, status = self.http_GET(url, rq_headers, authorization)
    assertion_status_ = self.response_status_check(url, status, log)      
    # manage assertion status
    assertion_status = log.status_fixup(assertion_status,assertion_status_)
    if assertion_status_ != log.PASS: 
        pass
    elif not json_payload:
        assertion_status_ = log.WARN
         # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (url))
    else:
        key = 'value'
        for entries in json_payload[key]: 
            if 'name' not in entries or 'kind' not in entries or 'url' not in entries:
                assertion_status = log.FAIL
                log.assertion_log('line', "Expected properties named 'name', 'kind' and 'url' in Odata service document json content, found: %s  " % (entries) )
            else:
                url=  urlparse(entries['url'])
                if entries['kind'] != ('Singleton' or 'EntitySet') or (('/redfish/v1') not in url.path) or not entries['name']:
                    assertion_status = log.FAIL
                    log.assertion_log('line', "Expected resource %s expected to be the direct child of root service %s in Odata service document json content, found: %s  " % (key, entries['name'], entries['url']) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.13

###################################################################################################
# Name: verify_collection_urlcxt(json_payload)                              
# Description: verifying @odata.context for collection resources to formats specified in spec  
###################################################################################################
def verify_collection_urlcxt(json_payload, assertion_status, self, log):
    key = '@odata.context'
    if key not in json_payload:
        assertion_status = log.FAIL
        log.assertion_log('line', "Expected property %s for resource %s " % (key, json_payload['@odata.id']) )
    else:
        #verify collection context url format
        metadata_url = "/redfish/v1/$metadata#"
        # remove version from odata.type... 
        collection_resource_type = rf_utility.parse_unversioned_odata_type(json_payload['@odata.type']) 
        collection_resource_path = None
        odata_id = (json_payload['@odata.id']).rsplit('/v1/', 1)[1]
        if odata_id:
            odata_id = odata_id[:-1]
            collection_resource_path = odata_id
        #contexturl_regex = re.match('(/redfish/v1/\$metadata#)(\w+.+\/\w+|.\w+)(\/\$entity)?$', json_payload['@odata.context'])

        if collection_resource_path:
            if metadata_url not in json_payload[key] or (collection_resource_type not in json_payload[key] and collection_resource_path not in json_payload[key]):
                assertion_status = log.FAIL
                log.assertion_log('line', "Expected property %s with value with format: 'MetadataUrl#CollectionResourceType' or 'MetadataUrl#CollectionResourcePath' for collectoin resource %s, found: %s" % (key, json_payload['@odata.id'],json_payload[key]) )
                                                
            else:
                if metadata_url not in json_payload[key] or (collection_resource_type not in json_payload[key]):
                    assertion_status = log.FAIL
                    log.assertion_log('line', "Expected property %s with value with format: 'MetadataUrl#CollectionResourceType' or 'MetadataUrl#CollectionResourcePath' for collectoin resource %s, found: %s" % (key, json_payload['@odata.id'],json_payload[key]) )
                               
    return assertion_status

###################################################################################################
# Name: verify_singleton_urlcxt(json_payload)                             
# Description: verifying @odata.context for single resources to formats specified in spec   
###################################################################################################  
def verify_singleton_urlcxt(json_payload, assertion_status, self, log):
    key = '@odata.context'
    if key not in json_payload:
        assertion_status = log.FAIL
        log.assertion_log('line', "Expected property %s for resource %s " % (key, json_payload['@odata.id']) )
    else:
        #verify singleton context url format
        metadata_url = "/redfish/v1/$metadata#"
        resource_type = rf_utility.parse_unversioned_odata_type(json_payload['@odata.type'])
        resource_path = None
        odata_id = (json_payload['@odata.id']).rsplit('/v1/', 1)[1]
        if odata_id:
           # odata_id = odata_id[:-1]
            resource_path = odata_id

        selectlist = '' # list of properties - Todo
        entity_ = '$entity'
        if resource_path:
            if metadata_url not in json_payload[key] or (resource_type not in json_payload[key] and (resource_path not in json_payload[key] or entity_ not in json_payload[key].rsplit('/', 1)[1])):
                assertion_status = log.FAIL
                log.assertion_log('line', "Expected property %s with value with format: 'MetadataUrl#ResourceType[(Selectlist)]' or 'MetadataUrl#ResourcePath[(Selectlist)]$entity' for collectoin resource %s, found: %s" % (key, json_payload['@odata.id'],json_payload[key]) )
                                     
        else:
            if metadata_url not in json_payload[key] or (resource_type not in json_payload[key]):
                assertion_status = log.FAIL
                log.assertion_log('line', "Expected property %s with value with format: 'MetadataUrl#ResourceType[(Selectlist)]' or 'MetadataUrl#ResourcePath[(Selectlist)]$entity' for collectoin resource %s, found: %s" % (key, json_payload['@odata.id'],json_payload[key]) )
                                            
    return assertion_status   

def verify_singleton_urlcxt_new(json_payload, assertion_status, self, log):
    key = '@odata.type'
    csdl_schema_model = self.csdl_schema_model
    if key not in json_payload:
        assertion_status = log.FAIL
        log.assertion_log('line', "Expected property %s for resource %s " % (key, json_payload['@odata.id']) )
    else:
        #verify singleton context url format
        if key in json_payload:
                namespace, typename = csdl_schema_model.get_resource_namespace_typename(json_payload['@odata.type'])
                if namespace and typename:
                    #structural property
                    for property in typename.Properties:
                        #still need to implement. get the annotation term-Required on create and save the name and typr in the dictionary
                        for annotations in property.Annotations :
                            if annotations.Term == 'Redfish.Required' :
                                if property.Name not in json_payload[property.Name] :
                                    assertion_status= log.FAIL
                                elif isinstance(json_payload[property.Name],dict) :
                                    assertion_status= log.FAIL
                                    log.assertion_log('line', "The required property is a complex type" % (key, json_payload[property.Name]) )
                        
    return assertion_status     
       
###################################################################################################
# Name: Assertion_6_5_14(self, log)                             
# Description:          
#   Context-Property     
# The JSON object shall contain a context property named "@odata.context".
# The value of the context property shall be the context URL that describes 
# the resource according to OData-Protocol
# The context URL for a resource singleton/collection is of the form:
#     Form1: MetadataUrl#ResourceType[(Selectlist)] / MetadataUrl#CollectionResourceType
#     Form2: MetadataUrl#ResourcePath[(Selectlist)]/$entity / MetadataUrl#CollectionResourcePath
###################################################################################################      
def Assertion_6_5_14(self, log):

    log.AssertionID = '6.5.14'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    rq_headers = self.request_headers()
    relative_uris = self.relative_uris_no_members

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                if 'Collection' in json_payload['@odata.type']:  
                    assertion_status = verify_collection_urlcxt(json_payload, assertion_status, self, log)
                    #check members of collection context url
                    members = self.get_resource_members(json_payload = json_payload)     
                    for json_payload, headers in members:
                        assertion_status = verify_singleton_urlcxt(json_payload, assertion_status, self, log)                                               
                else:   
                    #check singleton context url                 
                    assertion_status = verify_singleton_urlcxt_new(json_payload, assertion_status,self,log)
                                             
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.14



###################################################################################################
# Name: Assertion_6_5_15(self, log)                             
# Description:          
# Context-Property     
# If a response contains a subset of the properties defined in the Redfish Schema for a type, then the context URL 
# shall specify the subset of properties included. An asterix (*) can be used to specify "all structural properties" for a 
# given resource.
###################################################################################################      
def Assertion_6_5_15(self, log):

    log.AssertionID = '6.5.15'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    rq_headers = self.request_headers()
    relative_uris = self.relative_uris_no_members

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                if 'Collection' in json_payload['@odata.type']:  
                    assertion_status = verify_collection_urlcxt(json_payload, assertion_status, self, log)
                    #check members of collection context url
                    members = self.get_resource_members(json_payload = json_payload)     
                    for json_payload, headers in members:
                        assertion_status = verify_singleton_urlcxt(json_payload, assertion_status, self, log)                                               
                else:   
                    #check singleton context url                 
                    assertion_status = verify_singleton_urlcxt_new(json_payload, assertion_status,self,log)
                                             
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.15

###################################################################################################
# Name: Assertion_6_5_14_old(self, log)    WIP spec changes
#       incorrect -todo change to regex                            
# Description:          
#   Context-Property     
# The JSON object shall contain a context property named "@odata.context".
# The value of the context property shall be the context URL that describes 
# the resource according to OData-Protocol
# The context URL for a resource singleton/collection is of the form:
#     Form1: MetadataUrl#ResourceType[(Selectlist)] / MetadataUrl#CollectionResourceType
#     Form2: MetadataUrl#ResourcePath[(Selectlist)]/$entity / MetadataUrl#CollectionResourcePath
###################################################################################################
def Assertion_6_5_14_old(self, log):

    log.AssertionID = '6.5.14.old'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    rq_headers = self.request_headers()
    relative_uris = self.relative_uris_no_members

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                if 'Collection' in json_payload['@odata.type']:  
                    assertion_status = verify_collection_urlcxt(json_payload, assertion_status, self, log)
                    #check members of collection context url
                    members = self.get_resource_members(json_payload = json_payload)     
                    for json_payload, headers in members:
                        assertion_status = verify_singleton_urlcxt(json_payload, assertion_status, self, log)                                               
                else:   
                    #check singleton context url                 
                    assertion_status = verify_singleton_urlcxt(json_payload, assertion_status,self,log)
                                             
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.14_old

###################################################################################################
# Name: Assertion_6_5_17(self, log)                                               
# Description:           Resource Identifier Property   
# Resources in a response shall include a unique identifier property named "@odata.id". 
###################################################################################################
def Assertion_6_5_17(self, log) :

    log.AssertionID = '6.5.17'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    relative_uris = self.relative_uris

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
            key = '@odata.id'
            if key not in json_payload:
                assertion_status = log.FAIL
                log.assertion_log('line', "Expected property %s in response body " % (key) )
            elif json_payload[key] is None:
                assertion_status = log.FAIL
                log.assertion_log('line', "Expected property %s with a unique identifier in json body " % (key) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.17

###################################################################################################
# Name: Assertion_6_5_18(self, log)                                               
# Description:           Resource Identifier Property   
# Resources identifiers shall be represented in JSON payloads as strings that conform to the rules
# for URI paths as defined in Section 3.3, Path of rfcCL986. Our case: Resources within the same
# authority as the request URI shall always start with a single  forward slash ("/"). Resources 
# within a different authority as the request URI shall start with a double-slash ("//") followed 
# by the authority and path to the resource 
###################################################################################################
def Assertion_6_5_18(self, log) :

    log.AssertionID = '6.5.18'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    url = self.Redfish_URIs['Service_Root']

    rq_headers = self.request_headers()
    relative_uris = self.relative_uris

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        if(json_payload is not None and '@odata.type' in json_payload and isinstance(json_payload['@odata.type'],str)) :
            print ('Resources identifiers represented in JSON payloads are represented as strings that conform to the rules for %s' %relative_uri)
        else :
            print ('Resources identifiers represented in JSON payloads are not represented as strings that conform to the rules for %s' %relative_uri)
            assertion_status = log.FAIL

# for URI paths as defined in Section 3.3
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
            response_key = '@odata.id'
            if response_key not in json_payload:
                assertion_status = log.FAIL
                log.assertion_log('line', "Expected property %s in respose body " % (response_key) )
            elif json_payload[response_key] is None:
                assertion_status = log.FAIL
                log.assertion_log('line', "Expected property %s with a unique identifier in json body " % (response_key) )
            elif json_payload[response_key][0] != '/':
                    assertion_status = log.FAIL
                    log.assertion_log('line','%s value shall always start with a single forward slash ("/"), found: %s' %(response_key, json_payload[response_key]))
                   
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.18

###################################################################################################
# Name: Assertion_6_5_19(self, log)                                               
# Description:    Type Property  
# All resources in a response shall include a type property named "@odata.type". 
# The value of the type property shall be an absolute URL that specifies the type of the resource 
# and shall be of the form: #*Namespace*.*TypeName*
###################################################################################################
def Assertion_6_5_19(self, log) :
    log.AssertionID = '6.5.19'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    url = self.Redfish_URIs['Service_Root']

    rq_headers = self.request_headers()
    relative_uris = self.relative_uris

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
            response_key = '@odata.type'
            if response_key not in json_payload:
                assertion_status = log.FAIL
                log.assertion_log('line', "Expected property %s in response body " % (response_key) )
            elif json_payload[response_key] is None:
                assertion_status = log.FAIL
                log.assertion_log('line', "Expected property %s with a value of form #Namespace.TypeName in json body " % (response_key) )
            else:
                collection = re.match(r"(#)(\w+)(\.)(.+)", json_payload[response_key] , re.I)
                # Can be checked furthr with the namespace and typename
                if collection is None:
                    assertion_status = log.FAIL
                    log.assertion_log('line','%s value should match the form: #Namespace.TypeName, found: %s' %(response_key, json_payload[response_key]))
  
                
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.19

###################################################################################################
# check_datetime_property_in_payload() -todo fix regex
#   This function check the payload for a property
###################################################################################################
def check_datetime_property_in_payload(property_name, json_payload):
    #check payload, if it has the property, it must follow the format..
    for key in json_payload:
        if key == property_name:
            #use dateutils library instead? or todo regex
            collection = re.match("", json_payload[property_name])
            #or
            #isotime = datetime.datetime.strptime(json_payload['Time'], "%Y-%m-%dT%H:%M:%S%fZ")
            if collection is None:
                return False
    return True

###################################################################################################
# check_datetime_suffix_in_payload() -todo fix regex
#   This function check the payload for a property
###################################################################################################
def check_datetime_suffix_in_payload(property_name, json_payload):
    #check payload, if it has the property, it must follow the format..
    for key in json_payload:
        if key == property_name:
            #use dateutils library instead? or todo regex
            collection = re.match(r"", json_payload[property_name])
            #or
            #isotime = datetime.datetime.strptime(json_payload['Time'], "%Y-%m-%dT%H:%M:%S%fZ")
            if collection is not None:
                if 't' in collection.group(6) or 'z' in collection.group(12):
                    return False
    return True

def validate_time(time):
    time_t = time.split(':')
    if len(time_t) < 3:
        return False
    try:
        hh = int(time_t[0])
        mm = int(time_t[1])
        ss = int(time_t[2])
    except :
        return False
    return True


def validate(date_text):
    date_text = date_text.split('-')
    if len(date_text) != 3:
        return False
    try:
        year = int(date_text[0])
        month = int(date_text[1])
        day = int(date_text[2])
        if(year<1000):
            return False
        if month<1 or month >12:
            return False
        if day<1 or day >31:
            return False
    except :
        return False
    return True

###################################################################################################
# Name: Assertion_6_5_20(self, log)                                         
# Description:   Primitive properties shall be returned as JSON values according to the following table
###################################################################################################
def Assertion_6_5_20(self, log):
    log.AssertionID = '6.5.20'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()
    primitive_types = json.dumps({'Edm.Boolean':'boolean', 'Edm.DateTimeOffset':'datetime', 'Edm.Decimal':'decimal', 'Edm.Double':'double', 'Edm.Guid':'object', 'Edm.Int64':'int', 'Edm.String':'str'})
    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    count = 0
    #find alias in Include first?
    for relative_uri in relative_uris:
        if 'Root Service' in relative_uri:
                json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                    if '@odata.context' in json_payload:
                        resource = json_payload['@odata.context']
                        #r = requests.get(resource)
                        #print('The response is %s' %r)
                        rq_headers['Content-Type'] = rf_utility.content_type['xml']
                        rq_headers['Accept'] = rf_utility.accept_type['json_xml']
                        response,headers,status = self.http_GET(resource,rq_headers,None)
                        if isinstance(response, dict):
                            # received JSON, skip
                            print('Resource URI {}: received JSON content from @odata.context {}'
                                  .format(relative_uris[relative_uri], resource))
                            continue
                        response = response.decode('utf-8')
                        print('The response is %s' %response)
                        doc = minidom.parseString(response)
                        dataServices = doc.getElementsByTagName('edmx:Reference')
                        file_ = json.loads(primitive_types)
                        for d in dataServices:
                            uris = d.getAttribute('Uri')
                            print('The uri is %s' %uris)
                            #schema = uris.split('Schemas/')
                            schema = uris.rsplit('/', 1)
                            schema = schema[1]
                            print(schema)
                            uris = "http://redfish.dmtf.org/schemas/v1/"+schema
                            print(uris)
                            f = urllib.request.urlopen(uris)
                            myfile = f.read()
                            count = count + 1
                            #myfile = myfile.decode('utf-8')
                            # print(myfile)
                            if count < 40:
                                    doc = minidom.parseString(myfile)
                                    entity = doc.getElementsByTagName('Property')
                                    for e in entity:
                                        name = e.getAttribute('Name')
                                        type_ = e.getAttribute('Type')

                                        print('The name & type is %s %s' %(name,type_))
                                        if type_ in primitive_types:
                                            print('This is primitive type')
                                            if name in json_payload:
                                                    print(str(type(json_payload[name])))
                                                    j = str(type(json_payload[name])).split('\'')
                                                    type_1 = j[1]
                                                    if(type_1 == file_[type_]):
                                                        assertion_status = log.PASS
                                                    else:
                                                        assertion_status = log.FAIL
                                            else:
                                                continue

                                        else:
                                            continue
                            else:
                                break
  
                                                                                                                    
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.20


###################################################################################################
# Name: Assertion_6_5_21(self, log)  - Done by Priyanka                                           
# Description:   DateTime Values/Property   
# DateTime values shall be returned as JSON strings according to the ISO 8601 "extended" format,
# with time offset or UTC suffix included, of the form:
#  `*YYYY*-*MM*-*DD* T *hh*:*mm*:*ss*[.*SSS*] (Z | (+ | ~ ) *hh*:*mm*)` 
# validation pattern '([-+][0-1][0-9]:[0-5][0-9])'
###################################################################################################
def Assertion_6_5_21(self, log):
    log.AssertionID = '6.5.21'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?
    date_time = 'DateTime'
    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
            if date_time in json_payload:  
                value = json_payload['DateTime'] 
                if 'T' not in value:
                    assertion_status = log.FAIL
                    log.assertion_log('line','T should be capital in the %s of uri %s' %(value, relative_uri))                   
               
                day = value.rsplit('T',1)    
                print('Day is %s' %day[0]) 
                if(validate(day[0])) :             
                    time = day[1]
                    if 'Z' in time :
                        separator = 'Z'
                    elif '+' in time:
                        separator = '+'
                    elif '-' in time:
                        separator = '-'                      
                    time_1 = time.split(separator)
                    time_1 = time_1[0]
                    time_2 = time_1[1]  
                    if(validate_time(time_1)):
                        assertion_status = log.PASS
                    else:
                        assertion_status = log.FAIL
                        log.assertion_log('line', ' Time is not having valid format HH:MM:SS')                                     
                else :      
                    assertion_status = log.FAIL
                    log.assertion_log('line', ' Date is not having valid format YYYY-MM-DD')
    
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end assertion 6.5.21

###################################################################################################
# Name: Assertion_6_5_22(self, log)    Checked in 6.5.21                                     
# Description:   DateTime Values   
# The 'T' separator and 'Z' suffix shall be capitals.
###################################################################################################
def Assertion_6_5_22(self, log) :

    log.AssertionID = '6.5.22'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                        if property.Name == 'DateTime':                          
                            if not check_datetime_suffix_in_payload(property.Name, json_payload):
                                assertion_status = log.FAIL
                                log.assertion_log('line','%s value should have capital T and Z, found: %s' %(property.Name, json_payload[property.Name]))
            else:      
                assertion_status = log.WARN
                log.assertion_log('line', "~ @odata.type (resource identifier property) not found in redfish resource %s" % (relative_uris[relative_uri]))
                    
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.22

###################################################################################################
# Name: Assertion_6_5_23(self, log)                                          
# Description:   Collection Properties
# Collection-valued properties may contain a subset of the members of the full collection. The value 
# of the next link property shall be an opaque URL that the client can use to retrieve the next set 
# of collection members. The next link property shall only be present if the number of resources
# requested is greater than the number of resources returned.
###################################################################################################
def Assertion_6_5_23(self, log) :

    log.AssertionID = '6.5.23'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    relative_uris = self.relative_uris_no_members

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                if 'Collection' in json_payload['@odata.type']:  
                    nextlink = 'Members@odata.nextLink'                 
                    for key in json_payload:
                        if key == nextlink:
                            print ('The nextlink is present in uri %s' %relative_uri)
                            if json_payload[key] is None:
                                assertion_status = log.FAIL
                                log.assertion_log('line','property %s should have a value, found %s' %(key, json_payload[key]))
                            else:
                                url= urlparse(json_payload[key])
                                if not url.path:
                                    assertion_status = log.FAIL
                                    log.assertion_log('line','%s value should be url to retrieve next set of collection, found %s' %(nextlink, json_payload[key]))

            else:      
                assertion_status = log.WARN
                log.assertion_log('line', "~ @odata.type (resource identifier property) not found in redfish resource %s" % (relative_uris[relative_uri]))
    
                               
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.23

###################################################################################################
# Name: Assertion_6_5_23_1        wip                              
# Description:   Collection Properties
# The next link property shall only be present if the number of resources requested is greater than 
# the number of resources returned.
###################################################################################################
def Assertion_6_5_23_1(self, log) :

    log.AssertionID = '6.5.23.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    relative_uris = self.relative_uris_no_members
    count = 0
    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                if 'Collection' in json_payload['@odata.type']:
                    # WIP check member count and check len(Members) if len members < count, nextlink must be present..
                    # Added a code to count 'odata.count' and the length of members and calculated if it's <= with the count- Priyanka
                    member_count = json_payload['Members@odata.count']
                    for member in json_payload :
                        if 'Members' in json_payload :
                            member_array = json_payload['Members']
                            for m in member_array:
                                count = count+1
                    if count<=member_count: 
                        for key in json_payload:
                            nextlink = 'Members@odata.nextLink'
                            if key == nextlink:
                                if json_payload[key] is None:
                                    assertion_status = log.FAIL
                                    log.assertion_log('line','property %s should have a value, found %s' %(nextlink, json_payload[key]))

                            else :
                                assertion_status = log.FAIL
                                log.assertion_log('line', 'property %s should be present in the resource %s' %(nextlink,relative_uri))

            else:      
                assertion_status = log.WARN
                log.assertion_log('line', "~ @odata.type (resource identifier property) not found in redfish resource %s" % (relative_uris[relative_uri]))
                              
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.23.1

###################################################################################################
# Name: Assertion_6_5_24()                               
# Description:   Collection Properties   
# The total number of resources (members) available in the Resource Collection is represented through the
# count property. The count property shall be named "Members@odata.count" and its value shall be the
# total number of members available in the Resource Collection.
###################################################################################################
def Assertion_6_5_24(self, log) :

    log.AssertionID = '6.5.24'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    relative_uris = self.relative_uris_no_members

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                if 'Collection' in json_payload['@odata.type']:  
                    odata_count = 'Members@odata.count'
                    found = False
                    for key in json_payload.keys():
                        if key.endswith(odata_count): # why do we need to check this?
                            found = True  
                            print ('%s found in %s' %(odata_count,relative_uri))       
                            if json_payload[key] is None:
                                assertion_status = log.FAIL
                                log.assertion_log('line','property %s should have a value, found %s' %(odata_count, json_payload[key]))
                            elif not isinstance(json_payload[key], int):
                                assertion_status = log.FAIL
                                log.assertion_log('line','property %s should have an Integer type value, found %s' %(odata_count, json_payload[key]))
                            break
               
                    if found == False:
                        assertion_status = log.FAIL
                        log.assertion_log('line', "Expected property %s not found in Collection-type resource: %s" % (odata_count, relative_uris[relative_uri]) )
            else:      
                assertion_status = log.WARN
                log.assertion_log('line', "~ @odata.type (resource identifier property) not found in redfish resource %s" % (relative_uris[relative_uri]))
                                         
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.24

###################################################################################################
# Name: Assertion_6_5_25(self, log):                              
# Description:  The Members of the Resource Collection of resources are returned as a JSON array, 
# where each element of the array is a JSON object whose type is specified in the Redfish Schema document describing the containing type. 
# The name of the property representing the members of the collection shall be "Members". The Members property shall not be null. Empty collections shall be returned in JSON as an empty array.
###################################################################################################
def Assertion_6_5_25(self, log) :

    log.AssertionID = '6.5.25'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    relative_uris = self.relative_uris_no_members

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                if 'Collection' in json_payload['@odata.type']: 
                    #making changes to check the count first, if it's 0, still there should be an empty member array 
                    count = json_payload['Members@odata.count']
                    if count == 0:
                         member = 'Members'
                         if member in json_payload.keys(): 
                             print('%s is present in %s' %(member,relative_uri)) 
                             if not isinstance(json_payload[member], list):
                                 assertion_status = log.FAIL
                                 log.assertion_log('line','property %s should have an empty or nonempty array in its value, found %s' %(member, json_payload[member]))
                                 break
                             else:
                                 print('The property has an empty array for %s' %json_payload['@odata.type'])
                         else:
                              assertion_status = log.FAIL
                              log.assertion_log('line', "Expected property %s not found in Collection-type resource: %s" % (member, relative_uris[relative_uri]) )

            else:                                                       
                assertion_status = log.WARN
                log.assertion_log('line', "~ @odata.type (resource identifier property) not found in redfish resource %s" % (relative_uris[relative_uri]))                        
 
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.25

###################################################################################################
# Name: Assertion_6_5_26(self, log)                                               
# Description:    Action Representation 
# Actions are represented by a property nested under "Actions"  whose name is the unique URI that 
# identifies the action. This URI shall be of the form: #Namespace.ActionName
###################################################################################################
def Assertion_6_5_26(self, log) :

    log.AssertionID = '6.5.26'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    relative_uris = self.relative_uris
    csdl_schema_model = self.csdl_schema_model

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
            key = 'Actions'
            if key in json_payload:  
                for action in json_payload[key]:
                    # get namespace by parsing odata.id and then find out the name of the action witihn typename to compare accurately
                    collection = re.match(r"(#)(\w+)(\.)(.+)", action , re.I)
                    if collection is None:
                        assertion_status = log.FAIL
                        log.assertion_log('line','%s value should match the format: #Namespace.ActionName, found: %s' %(key, action)) 

                    else: # match namespace and action name
                        action = action.rsplit('#',1)
                        check_1 = action[1]
                        namespace_1 = check_1.rsplit('.',1)
                        namespace = namespace_1[0]
                        check = namespace_1[1]
                        print ('The namespace is %s' %namespace +'_v1.xml')
                        doc = minidom.parse(os.getcwd()+'/redfish-1.0.0/metadata/'+ namespace + '_v1.xml')
                        dataServices = doc.getElementsByTagName('Action')[0]
                        if (dataServices.getAttribute('Name')== check):
                            assertion_status = log.PASS
                            print('The schema file has the same action name as in the response')
                        else :
                             assertion_status = log.FAIL
                             log.assertion_log('line', 'Action %s could not be found within the Resource Type %s . Even though it is of the valid format \'#Namespace.ActionName\' but the values for \'Namespace\' and \'ActionaName\' could not be matched in its schema' %(key, namespace))
                             continue
                        '''namespace, typename = csdl_schema_model.get_resource_namespace_typename(json_payload['@odata.type'])
                        print('Namespace is %s and typename is %s' %(namespace,typename))
                        if namespace and typename:
                            if not csdl_schema_model.verify_action_name_recur(namespace, typename, action):
                                assertion_status = log.FAIL
                                log.assertion_log('line', 'Action %s could not be found within the Resource Type %s in its schema file: %s. Even though it is of the valid format \'#Namespace.ActionName\' but the values for \'Namespace\' and \'ActionaName\' could not be matched in its schema' %(key, action, namespace.SchemaUri, action.rsplit('.', 1), typename.Name ))''' 
    assertion_status = log.status_fixup(assertion_status,assertion_status_)                            
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.26

###################################################################################################
# Name: check_reference_type(json_payload['Links'])
# Description: This function checks the value of Links which could be 
#              a reference to single related resource id (single-valued) or an array of 
#              related resource ids (collection-valued). If none matches, returns False
###################################################################################################
def check_reference_type(links):
    reference_found = True  
    if isinstance(links, dict):
        if any(isinstance(links[key], dict) or isinstance(links[key], list) for key in links):
            for key in links:
                if '@odata.count' in key:
                    continue
                if isinstance(links[key], dict):
                    if '@odata.id' not in links[key].keys():
                        reference_found = False
                elif isinstance(links[key], list):
                    for reference in links[key]:
                        if '@odata.id' not in reference.keys():
                            reference_found = False
                else:
                    reference_found = False
        else:
            reference_found = False
    else:
        reference_found = False

    return reference_found

###################################################################################################
# Name: Assertion_6_5_28()                                           
# Description:           Links Property
# The links property shall be named "Links" and shall contain a property for each non-contained 
# reference property defined in the Redfish Schema for that type. For single-valued reference 
# properties, the value of the property shall be the single related resource id. For collection-
# valued reference properties, the value of the property shall be the array of related resource ids.
###################################################################################################
def Assertion_6_5_28(self, log) :

    log.AssertionID = '6.5.28'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
            # only try to validate property if its returned in the payload for this resource, in this assertion we are not chekcing if Links was a required property. we are just validating that if its in the payload, its following the single/collection
            if 'Links' in json_payload:            
                if not check_reference_type(json_payload['Links']):
                    assertion_status = log.FAIL
                    log.assertion_log('line', 'The \'Links\' property in resource %s is expected to contain either a single-valued or collection-valued reference property as described in Redfish Specification. Not found, instead found \'Links\' : %s' % (relative_uris[relative_uri], rf_utility.json_string(json_payload['Links'])))
                         
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.28

###################################################################################################
# Name: Assertion_6_5_30(self, log)        WIP                                      
# Description:    Additional Annotations
# A resource representation in JSON may include additional annotations represented as properties
# whose name is of the form: [PropertyName]@Namespace.TermName
# collection = re.match(r"(\w+)(@)(\w+)(\.)(\w+)", json_payload[additional_property.Name] , re.I)
###################################################################################################
def Assertion_6_5_30(self, log) :

    log.AssertionID = '6.5.30'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                #TODO compare json schema and payload and verify format for any/all additional properties.. 
         
    log.assertion_log(assertion_status, None)

    return (assertion_status)
#
## end Assertion 6.5.30

###################################################################################################
# Name: Assertion_6_5_31(self, log)                                               
# Description:    Resource Collections 
# Resource collections are returned as a JSON object. The JSON object shall include a context,
# resource count, and array of values, and may include a next link for partial results.
###################################################################################################
def Assertion_6_5_31(self, log) :

    log.AssertionID = '6.5.31'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    key1= '@odata.context'
    key2= 'Members@odata.count'
    key3= 'Members'
    key4= 'Members@odata.nextlink' 

    relative_uris = self.relative_uris_no_members
    rq_headers = self.request_headers()

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                if 'Collection' in json_payload['@odata.type']:  
                    if key1 not in json_payload:
                        assertion_status = log.FAIL
                        log.assertion_log('line','Required Property: %s expected but not found in json response for collection %s' %(key1, relative_uris[relative_uri]))

                    elif key2 not in json_payload:
                        assertion_status = log.FAIL
                        log.assertion_log('line','Required Property: %s expected but not found in json response for collection %s' %(key3, relative_uris[relative_uri]))

                    elif key4 not in json_payload:
                        log.assertion_log('TX_COMMENT','Conditional Property: %s not found in json response for collection %s' %(key4, relative_uris[relative_uri]))
                        
                    elif key3 not in json_payload:
                        assertion_status = log.FAIL
                        log.assertion_log('line','Required Property: %s expected but not found in json response for collection %s' %(key2, relative_uris[relative_uri]))

    log.assertion_log(assertion_status, None)

    return (assertion_status)  
#
## end Assertion 6.5.31


###################################################################################################
# Name: Assertion_6_5_8(self, log)                                               
# Description:    Referencing Other Schemas
# The service metadata shall include the namespaces for each of the Redfish resource types, along with
# the "RedfishExtensions.v1_0_0" namespace.
###################################################################################################
def Assertion_6_5_8(self, log) :

    log.AssertionID = '6.5.8'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    relative_uris = self.relative_uris
    rq_headers = self.request_headers()
    direc = os.getcwd()+'/redfish-1.0.0/json-schema/'
    ext = '.json'
    file_dict = {} # Create an empty dict
    
    # Select only files with the ext extension
    txt_files = [i for i in os.listdir(direc) if os.path.splitext(i)[1] == ext]
    for i in range (0, len(txt_files)):
        txt_files[i] = txt_files[i].split('.json')[0]
        #txt_files[i]= txt_files[i][0]
    # Iterate over your txt files
    list1 = []

    for relative_uri in relative_uris:
        rq_headers['Accept'] = rf_utility.accept_type['json']
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
            if '@odata.context' in json_payload:
                resource = json_payload['@odata.context']
                #r = requests.get(resource)
                #print('The response is %s' %r)
                rq_headers['Accept'] = rf_utility.accept_type['xml']
                response,headers,status = self.http_GET(resource,rq_headers,None)
                if isinstance(response, dict):
                    # received JSON, skip
                    print('Resource URI {}: received JSON content from @odata.context {}'
                          .format(relative_uris[relative_uri], resource))
                    continue
                response = response.decode('utf-8')
                print('The response is %s' %response)
                doc = minidom.parseString(response)
                dataServices = doc.getElementsByTagName('edmx:Reference')
                extension = doc.getElementsByTagName('edmx:Include')
                print('The extension is %s' %extension)
                for v in extension:                   
                    a = v.getAttribute('Namespace')
                    print('The valus is %s' %a)  
                    list1.append(a)
                    if 'RedfishExtensions.v1_0_0' in a :
                            print('RedfishExtensions.v1_0_0 is present in %s' %relative_uri)
                    else:
                        continue
             
                '''for ref in dataServices:                   
                    namespace = ref.getElementsByTagName('edmx:Include')[0].getAttribute('Namespace')  
                    if namespace not in list1:                                   
                        list1.append(namespace)'''
            else :
                assertion_status = log.FAIL
                log.assertion_log('line', 'No ~(@odata.context)found in payload for %s' %relative_uri)

    if list1 in txt_files:
         assertion_status = log.PASS
         print('Pass: Metadata file list is %s and local file list is %s along with RedfishExtensions.v1_0_0 ' %(list1,txt_files)) 

    else :
        assertion_status = log.FAIL
        print('Local file list is %s' %(txt_files))   

    print('The list is %s' %list1)
    diff = list(set(list1) - set(txt_files))
    print('The files that are not in metadata %s' %diff)
    log.assertion_log(assertion_status, None)
    return (assertion_status)  
#
## end Assertion 6.5.8

###################################################################################################
# Name: Assertion_6_5_9(self, log)                                               
# Description:    Referencing Other Schemas
# The service metadata shall include an entity container that defines the top level resources and Resource Collections.
###################################################################################################
def Assertion_6_5_9(self, log) :

    log.AssertionID = '6.5.9'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    relative_uris = self.relative_uris
    rq_headers = self.request_headers()
    direc = os.getcwd()+'/redfish-1.0.0/metadata/'


    for relative_uri in relative_uris:
        rq_headers['Accept'] = rf_utility.accept_type['json']
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
            if '@odata.context' in json_payload:
                resource = json_payload['@odata.context']
                if 'ServiceRoot' in resource :
                        #r = requests.get(resource)
                        #print('The response is %s' %r)
                        rq_headers['Accept'] = rf_utility.accept_type['xml']
                        response,headers,status = self.http_GET(resource,rq_headers,None)
                        if isinstance(response, dict):
                            # received JSON, skip
                            print('Resource URI {}: received JSON content from @odata.context {}'
                                  .format(relative_uris[relative_uri], resource))
                            continue
                        response = response.decode('utf-8')
                        print('The response is %s' %response)
                        doc = minidom.parseString(response)
                        dataServices = doc.getElementsByTagName('edmx:DataServices')
                        entity = ET.Element('Schema')
                        element = ET.SubElement(entity, 'EntityContainer')

                        print('The element is %s' %element)
                        '''for v in entity :
                                name = v.getAattribute('Name')                      
                                extends = v.getAattribute('Extends')
                                print('The name and extends value is %s %s' %(name,extends))'''
                        if element is not None:
                            print('EntityContainer is present in %s' %relative_uri)             
                        else:
                            print('EntityContainer is not present in %s' %relative_uri)
                            assertion_status = log.FAIL
                            continue
                else :
                    continue
                '''for ref in dataServices:                   
                    namespace = ref.getElementsByTagName('edmx:Include')[0].getAttribute('Namespace')  
                    if namespace not in list1:                                   
                        list1.append(namespace)'''
            else :
                assertion_status = log.FAIL
                log.assertion_log('line', 'No ~(@odata.context)found in payload for %s' %relative_uri)

    log.assertion_log(assertion_status, None)
    return (assertion_status)  
#
## end Assertion 6.5.9

###################################################################################################
# Name: Assertion_6_5_35(self, log)                                          
# Description:   Partial Resource Results
# Responses representing a single resource shall not be broken into multiple results.
###################################################################################################
def Assertion_6_5_35(self, log) :

    log.AssertionID = '6.5.35'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    relative_uris = self.relative_uris_no_members

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                if 'Collection' not in json_payload['@odata.type']:                  
                    if '@odata.nextLink' in json_payload:
                        print ('The nextlink is present in uri %s, which shows that single resource is broken into multiple results' %relative_uri)
                        assertion_status = log.FAIL
                        #log.assertion_log('line','property %s should not have a value, found %s' %(response_key, json_payload[key]))
                        log.assertion_log('line', 'The nextlink is present in uri %s, which shows that single resource is broken into multiple results' %relative_uri)
            else:      
                assertion_status = log.WARN
                log.assertion_log('line', "~ @odata.type (resource identifier property) not found in redfish resource %s" % (relative_uris[relative_uri]))
    
                               
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.35


###################################################################################################
# Name: Assertion_POST_Test(self, log)                                               
# Description:    POST actions on the resources 
# POST actions are performed on the resources that suppots POST and the status code is validated
# Test performed by Priyanka
###################################################################################################

def Assertion_POST_Test(self, log) :

    #log.AssertionID = '6.4.31'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    print('Beginning POST Testing')
    rq_body = {'Action': 'GracefulRestart'}
    rq_headers = self.request_headers()
  
    
    json_payload, headers, status = self.http_POST('/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Manager.Reset', rq_headers, rq_body, authorization)
    print('json payload is %s and status is %s', json_payload, status)
    assertion_status = self.response_status_check(json_payload['@odata.id'], status, log, request_type = 'POST')          
    # manage assertion status
    assertion_status = log.status_fixup(assertion_status)
    if assertion_status != log.PASS: 
        print('The POST action is not provided by the Refish Service')                
        #log.assertion_log('line', 'POST on action %s at url %s failed' % (json_payload['Actions']['#LogService.ClearLog']['target'], json_payload['@odata.id']))
                          
    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion POST Test

# This function checks if the Registry name and Message key checked in 6.5.40 are in camel case or not
def camel(s):
    return (s != s.lower() and s != s.upper())

## end def camel

###################################################################################################
# Name: Assertion_6_5_40_old(self, log)                                               
# Description:    RegistryName is the name of the registry. The registry name shall be Pascal-cased. 
# Test performed by Priyanka
###################################################################################################
def Assertion_6_5_40_old(self, log) :

    log.AssertionID = '6.5.40_old'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    #url = self.Redfish_URIs['Service_Odata_Doc']
    relative_uris = self.relative_uris
    rq_headers = self.request_headers()
    for relative_uri in relative_uris:
        if 'Registries' in relative_uri:
            json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
            if 'Members' in json_payload:
                members = json_payload['Members']
                for uri in members:
                    uri_ = uri['@odata.id']
                    json_payload_, headers_, status = self.http_GET(uri_, rq_headers, authorization)
                    type_ = json_payload_['@odata.type']
                    package = type_.rsplit('#',1)
                    name = package[1]
                    if '_' in name:
                        separator = '_'
                    elif '.' in name:
                        separator = '.'
                    name_ = name.rsplit(separator,1)
                    message_key = name_[1]
                    name_= name_[0]                  
                    r_name = name_.rsplit(separator,-1)
                    registry_name = r_name[0]
                    major_version = r_name[1]
                    minor_version = r_name [2]
                    print('The RegistryName is %s and MajorVersion is %s and MessageKey is %s' %(registry_name, major_version, message_key))
                    status = camel(registry_name)
                    status_1 = camel(message_key)
                    print('%s %s' %(status, status_1))

                    if ( status == True and status_1 == True):
                        assertion_status = log.PASS
                    else:
                        assertion_status = log.FAIL

    log.assertion_log(assertion_status, None)

    return (assertion_status)
#
## end Assertion 6.5.40_old

###################################################################################################
# Name: Assertion_6_5_40(self, log)                                               
# Description: This section includes the testinng for all the 'Message Object' 
# Test performed by Priyanka
###################################################################################################

def Assertion_6_5_40(self, log) :

    log.AssertionID = '6.5.40'
    assertion_status =  log.WARN
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    #url = self.Redfish_URIs['Service_Odata_Doc']
    relative_uris = self.relative_uris
    rq_headers = self.request_headers()
    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        if (self.allowable_method('PATCH', headers)):
            rq_body = {'Name' : 'New Name'}
            json_payload, headers, status = self.http_PATCH(relative_uris[relative_uri], rq_headers, rq_body, authorization)   

            if 'error' in json_payload : 
                message_error = json_payload['error']
                message_object = message_error['@Message.ExtendedInfo']
                message_object = message_object[0]
                print('Message object is %s' %message_object)
                if 'Message' in message_object :
                    if 'MessageId' in message_object:
                        name = message_object['MessageId']
                        if '_' in name:
                            separator = '_'
                        elif '.' in name:
                            separator = '.'
                        name_ = name.rsplit(separator,1)
                        message_key = name_[1]
                        name_= name_[0]                  
                        r_name = name_.rsplit(separator,-1)
                        registry_name = r_name[0]
                        major_version = r_name[1]
                        minor_version = r_name [2]
                        print('The RegistryName is %s and MajorVersion is %s and MessageKey is %s' %(registry_name, major_version, message_key))
                        status = camel(registry_name)
                        status_1 = camel(message_key)
                        print('%s %s' %(status, status_1))
                        if ( status == True and status_1 == True):
                            assertion_status = log.PASS
                        else:
                            assertion_status = log.FAIL

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.5.40

###################################################################################################
# Name: Assertion_6_1_6(self, log)                                               
# Description:    The unique identifier part of a URI shall be unique within the implementation.
###################################################################################################

def Assertion_6_1_6(self, log) :

    log.AssertionID = '6.1.6'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    print('The service and the resource paths shall be unique')
    # get SUTs relative uris dictionary
    relative_uris = self.relative_uris

    authorization = 'on'
    rq_headers = self.request_headers()
    resource_path = set()
    for relative_uri in relative_uris:
        print('The uri is %s' %relative_uri)
        try:
            json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
            print('Printing %s' %relative_uris[relative_uri])
            uri = relative_uris[relative_uri].split('/redfish/v1')
            root = uri[0]
            service = uri[1]
            print('Printing ..... %s %s' %(root,service))
            if (service == '/') :
                print('This is root service, go to other url')
                continue
            
            else:
                if service not in resource_path:
                    resource_path.add(service)
                else:
                    print('The resource path already existing and not unique')
                    assertion_status= log.FAIL
                    break
        except:
            assertion_status = log.FAIL

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.1.6
###################################################################################################



###################################################################################################
# Name: Assertion_6_1_7(self, log)                                               
# Description:    URIs, as described in RFCL986, may also contain a query (?query) and a frag (#frag) 
# components.  Queries are addressed in the section Query Parameters.  Fragments (frag) shall be ignored
# by the server when used as the URI for submitting an operation. 
# Test performed by Priyanka
###################################################################################################

def Assertion_6_1_7(self, log) :

    log.AssertionID = '6.1.7'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    # get SUTs relative uris dictionary
    relative_uris = self.relative_uris

    authorization = 'on'
    rq_headers = self.request_headers()
    print('Beginning assertion 6.1.7')
    query = '#123'
    for relative_uri in relative_uris:
        relative_uri = relative_uri + query
        try:
            json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
            assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)    
            #print('The status is %s', status)         
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
        except:
            assertion_status = log.FAIL

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.1.7
###################################################################################################


###################################################################################################
# Name: Assertion_6_4_24_xml(self, log)             -checked via xml schema                               
# Description: 
# Method: PATCH ~ If a property in the request can never be updated,  such as when a property is 
# read only, a status code of 200 shall be returned along with a representation of the resource 
# containing an annotation specifying the non-updatable property. In this success case, other 
# properties may be updated in the resource.	                                             
###################################################################################################
def Assertion_6_4_24_xml(self, log) :
    log.AssertionID = '6.4.24_xml'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    found = False

    authorization = 'on'
    rq_headers = self.request_headers()

    csdl_schema_model = self.csdl_schema_model
    relative_uris = self.relative_uris
    #find alias in Include first?

    annotation_term = 'readonly'

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
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
                #print (os.getcwd())
                doc = minidom.parse(os.getcwd()+'\\redfish-1.0.0\\metadata\\'+ typename + '_v1.xml')
                dataServices = doc.getElementsByTagName('PropertyValue')[1]
                if (dataServices.getAttribute('Property')=='Updatable'):
                    if(dataServices.getAttribute('Bool')=='false'):
                        print ('Cannot be updated and the status of GET operation is')
                        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
                        print(' %s' %status)
                    else:
                        print('Do the patch')
                        rq_body = {prop: 'PatchName'}		
                        json_payload, headers, status = self.http_PATCH(relative_uris[relative_uri], rq_headers, rq_body, authorization)   
                                             
                if namespace and typename:
                    json_metadata, schema_file = rf_utility.get_resource_json_metadata(namespace, self.json_directory)                  
                    if json_metadata and schema_file:           
                        if verify_typename_in_json_metadata(typename, json_metadata):
                            if 'properties' in json_metadata['definitions'][typename]:
                                for prop in json_metadata['definitions'][typename]['properties']:                                       
                                    if annotation_term in json_metadata['definitions'][typename]['properties'][prop]:
                                        if json_metadata['definitions'][typename]['properties'][prop][annotation_term]:
                                            # if true. check if intended method is an allowable method for resource
                                            if (self.allowable_method('PATCH', headers)):   
                                                #check property name in json_payload..if available request patch on it       
                                                if prop in json_payload.keys():                                                   
                                                    rq_body = {prop: 'PatchName'}		
                                                    json_payload, headers, status = self.http_PATCH(relative_uris[relative_uri], rq_headers, rq_body, authorization)
                                                    if status:
                                                        if status == rf_utility.HTTP_OK:
                                                            assertion_status = log.FAIL               
                                                            log.assertion_log('line', "~ PATCH passed on property %s with annotation term %s : %s (check document %s) which is an unexpected behavior" % (prop, annotation_term, json_metadata['definitions'][typename]['properties'][prop][annotation_term], schema_file))
                                                            continue                                                   
                                                    else:
                                                        #TODO check extended error should have property name in msgargs annotation...
                                                        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
                                                        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
                                                        # manage assertion status
                                                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                                        if assertion_status_ != log.PASS:                 
                                                            continue
                                                        if not json_payload:
                                                            assertion_status = log.WARN
                                                            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (relative_uris[relative_uri]))
                                                        else:
                                                            if prop in json_payload.keys():
                                                                #check if resource remain unchanged, else FAIL. The object might have changed by another source changing the etag, so, in this case, checking value of property makes more sense than etags
                                                                if (json_payload[property.Name] == 'PatchName'):
                                                                    assertion_status = log.FAIL
                                                                    log.assertion_log('line', "~ PATCH on Property %s of resource %s is a Read-only property according to its schema document %s, which might have been updated unexpectedly" % (prop, relative_uris[relative_uri]) )                                                                                         

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 6.4.24_xml


# run(self, log):
# Takes sut obj and logger obj 
###################################################################################################
def run(self, log): 
      
    assertion_status = Assertion_6_1_0(self,log)
    assertion_status = Assertion_6_1_1(self,log)
    # Assertion 6_1_2 - Each unique instance of a resource shall be identified by a URI; thus a URI cannot reference multiple resources though it may reference a single collection resource.
    assertion_status = Assertion_6_1_2(self,log)
    # Assertion 6.1.3 - This is client specific and not the Redfish Service rule.
    # assertion_status = Assertion_6_1_3(self,log)

    assertion_status = Assertion_6_1_6(self,log)
    #Fragments shall be ignored by the server when used as the URI
    assertion_status = Assertion_6_1_7(self, log)
    # Create/update/delete an Account: these next 3 assertions need to be run in series
    # ...POST/create a new session for the account and it calls internally 6.1.8.1.1 and 6.1.8.1.2
    assertion_status = Assertion_6_1_8_1(self, log)
    # ...GET account collection
    assertion_status = Assertion_6_1_8_2(self, log)
    # ...PATCH/update the new account note: this assertion expects 6_1_8_1 to run prior to this
    assertion_status = Assertion_6_1_8_3(self, log)
    # ...DELETE the new session that was created above note: this assertion expects 6_1_8_1 to run prior to this
    assertion_status = Assertion_6_1_8_4(self, log) 
    assertion_status = Assertion_6_1_9(self, log)
    # Assertion 6.1.10 is client specific - All Redfish Clients shall correctly handle HTTP redirect.
    assertion_status = Assertion_6_1_11(self, log)
    assertion_status = Assertion_6_1_12(self, log)
    assertion_status = Assertion_6_1_13(self, log)
    assertion_status = Assertion_6_1_14(self, log)
    # Assertion 6.2.1 -The root URI for this version of the Redfish protocol shall be "/redfish/v1/" is duplicate and is tested in 6.3.1
    # Assertion 6.2.3 - Any resource discovered through links found by accessing the root service or any service or resource 
    # referenced using references from the root service shall conform to the same version of the protocol supported by the 
    #root service. This can't be tested now as just the version 1 of Redfish is released
    assertion_status = Assertion_6_2_3(self, log)
    assertion_status = Assertion_6_3_1(self, log) 
    assertion_status = Assertion_6_3_2(self, log)
    assertion_status = Assertion_6_3_3(self, log)
    # Assertion_6_4_1 Required Column and Conditional one are checked in this
    assertion_status = Assertion_6_4_1(self,log)
    assertion_status = Assertion_6_4_2_1(self, log)
    assertion_status = Assertion_6_4_2_2(self, log)          
    assertion_status = Assertion_6_4_2_3(self, log)           
    assertion_status = Assertion_6_4_2_4(self, log)
    # Specification requirement changes           
    assertion_status = Assertion_6_4_2_5(self, log)            
    #Specification requirement changes   
    assertion_status = Assertion_6_4_2_6(self, log) 
    # Assertion_6_4_4 Tried doing it - Priyanka
    assertion_status = Assertion_6_4_4(self,log)
    assertion_status = Assertion_6_4_5(self, log)
    #-assertion_status = Assertion_6_5_13(self, log)                 
    #-assertion_status = Assertion_POST_Test(self, log)                                    
    #-assertion_status = Assertion_6_4_11(self, log)
    # Assertion 6.4.13 tested for the fragments that is ignored in the uri- Priyanka           
    assertion_status = Assertion_6_4_13(self, log) 
    assertion_status = Assertion_6_4_14(self, log)   
    #-assertion_status = Assertion_6_4_15(self, log)
    assertion_status = Assertion_6_4_16(self, log)  
    assertion_status = Assertion_6_4_18(self, log)  
    assertion_status = Assertion_6_4_21(self, log)    
    assertion_status = Assertion_6_4_23(self, log)
    assertion_status = Assertion_6_4_24(self, log)
    #assertion_status = Assertion_6_4_24_xml(self, log)
    assertion_status = Assertion_6_4_25(self, log) 
    assertion_status = Assertion_6_4_26(self, log)   
    assertion_status = Assertion_6_4_27(self, log)      
    assertion_status = Assertion_6_4_30(self, log)
    assertion_status = Assertion_6_4_32(self, log)  
    #-assertion_status = Assertion_6_4_32_old(self, log)  
    if 'AllowAction_LogServiceClearLog' in self.SUT_prop:
        if (self.SUT_prop['AllowAction_LogServiceClearLog'] == 'yes'):
            assertion_status = Assertion_6_4_31(self, log)
            assertion_status = Assertion_6_4_32(self, log)
        else:
            print("\nNote: assertions 6.4.31 and 6.4.32 skipped as per json configuration file setting\n")
            log.assertion_log('TX_COMMENT', "Note: assertions 6.4.31 and 6.4.32 skipped as per json configuration file setting\n")       
             
         
    assertion_status = Assertion_6_5_1(self, log) 
    #-assertion_status = Assertion_6_5_2_4(self, log)
    assertion_status = Assertion_6_5_2_6(self, log)
    assertion_status = Assertion_6_5_2_6_1(self, log)
    assertion_status = Assertion_6_5_3(self, log)             
    assertion_status = Assertion_6_5_6_2(self, log)
    #duplicate, or find another resource to POST
    assertion_status = Assertion_6_5_6_3(self, log) 
    assertion_status = Assertion_6_5_6_5(self,log)
    assertion_status = Assertion_6_5_6_6(self, log)
    assertion_status = Assertion_6_5_6_8(self, log) 
    assertion_status = Assertion_6_5_6_9(self, log)
    # commenting out the following, service stops responding shortly after serveral wrong credential attempts..
    assertion_status = Assertion_6_5_6_10(self, log) 
    #-assertion_status = Assertion_6_5_6_13(self, log)
    assertion_status = Assertion_6_5_8(self, log)
    assertion_status = Assertion_6_5_9(self,log)
    assertion_status = Assertion_6_5_10(self, log)
    assertion_status = Assertion_6_5_11(self, log)           
    assertion_status = Assertion_6_5_12(self, log)
    assertion_status = Assertion_6_5_13(self, log)
    # fix regex
    assertion_status = Assertion_6_5_14(self, log)
    #-assertion_status = Assertion_6_5_15(self, log)
    assertion_status = Assertion_6_5_17(self, log)
    assertion_status = Assertion_6_5_18(self, log)
    #-assertion_status = Assertion_6_5_19(self, log)
    #WIP - Assertion_6.5.20 is pending
    assertion_status = Assertion_6_5_20(self, log) 
    assertion_status = Assertion_6_5_21(self, log)        
    #assertion_status = Assertion_6_5_22(self, log)
    assertion_status = Assertion_6_5_23(self, log)
    assertion_status = Assertion_6_5_23_1(self, log)
    assertion_status = Assertion_6_5_24(self, log)
    assertion_status = Assertion_6_5_25(self, log)
    assertion_status = Assertion_6_5_26(self, log)
    assertion_status = Assertion_6_5_28(self, log)
    #WIP It'a a may condition
    #assertion_status = Assertion_6_5_30(self, log)
    #-assertion_status = Assertion_6_5_31(self, log)
    assertion_status = Assertion_6_5_35(self, log)
    assertion_status = Assertion_6_5_40(self,log)
