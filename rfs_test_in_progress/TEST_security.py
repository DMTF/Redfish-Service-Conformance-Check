# Copyright Notice:
# Copyright 2016-2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/LICENSE.md

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
REDFISH_SPEC_VERSION = "Version 1.0.2"

###################################################################################################
# Name: Assertion_9_3_1(self, log)  Authentication/Sessions                                             
# Description:     
# Service shall support both "Basic Authentication" (Assertion 9.3.1.4) and "Redfish Session Login 
#   Authentication" (This assertion)
#  The response to the POST request to create a session includes: an X-Auth-Token header that 
#  contains a "session auth token" that the client can use an subsequent requests, and a "Location
# header that contains a link to the newly created session resource. The JSON response body that 
# contains a full representation of the newly created session object? ~ i dont see it
###################################################################################################      
def Assertion_9_3_1(self, log) :
 
    log.AssertionID = '9.3.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    
    relative_uris = self.relative_uris                   
    session_key = 'x-auth-token'
    x_auth_token = None
    session_location = None

    #Create session
    authorization = 'on'
    rq_headers = self.request_headers()
    session_uri = None
    root_link_key = 'Sessions'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        session_uri = self.sut_toplevel_uris[root_link_key]['url']
    else:
        for rel_uris in self.relative_uris:
            if rel_uris.endswith('Sessions'):
                session_uri = self.relative_uris[rel_uris]
    if session_uri:        
        json_payload, headers, status = self.http_GET(session_uri, rq_headers, authorization)
        assertion_status_ = self.response_status_check(session_uri, status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            pass
            # check if intended method is an allowable method for resource
        elif not (self.allowable_method('POST', headers)):
            assertion_status = log.WARN
            log.assertion_log('line', "~ the response headers for %s do not indicate support for POST" % session_uri)
        else:
            # request body to create session
            rq_body = {'UserName': self.SUT_prop['LoginName'], 'Password': self.SUT_prop['Password']}
            log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s' % (session_uri, rq_body))  
            json_payload, headers, status = self.http_POST(session_uri, rq_headers, rq_body, authorization)
            assertion_status_ = self.response_status_check(session_uri, status, log, rf_utility.HTTP_CREATED, 'POST')      
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            if assertion_status_ != log.PASS: 
                pass
            elif headers:
                #session created
                # get location from the response header
                if 'location' in headers:   
                    session_location = headers['location']                        
                #get x-auth-token to request GETS using this session
                session_key = 'x-auth-token'
                if session_key not in headers:           
                    assertion_status = log.FAIL
                    log.assertion_log('line',"Response header for POST on %s does not contain key: %s, which is required so that the client can use this session as authentication method for subsequent requests." %(session_uri, session_key))
                elif not headers[session_key]:
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ Expected header %s to have a value with session auth token, which is required so that the client can use this session as authentication method for subsequent requests ~ Not found" % (session_key)) 
                else:
                    x_auth_token = headers[session_key]  
                    #try GETs on service root links with session key
                    rq_headers = self.request_headers()
                    #auth off and use session key
                    authorization = 'off'
                    rq_headers[session_key] = x_auth_token
                    for relative_uri in relative_uris:
                        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
                        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
                        # manage assertion status
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)

                #Terminate this session
                if session_location:
                    authorization = 'on'
                    rq_headers = self.request_headers()
                    json_payload, headers, status = self.http_DELETE(session_location, rq_headers, authorization)
                    assertion_status_ = self.response_status_check(session_location, status, log, request_type = 'DELETE')      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)

    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 9.3.1

###################################################################################################
# Name: Assertion_9_3_1_1(self, log)  Authentication/Sessions                                         
# Description:     
# The response to the POST request to create a session includes: an X-Auth-Token header that contains
#  a "session auth token" that the client can use an subsequent requests	       
###################################################################################################
def Assertion_9_3_1_1(self, log) :
 
    log.AssertionID = '9.3.1.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
                             
    #Create session
    authorization = 'on'
    rq_headers = self.request_headers()
    session_location = None

    session_uri = None
    root_link_key = 'Sessions'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        session_uri = self.sut_toplevel_uris[root_link_key]['url']
    else:
        for rel_uris in self.relative_uris:
            if rel_uris.endswith('Sessions'):
                session_uri = self.relative_uris[rel_uris]
    if session_uri:
        json_payload, headers, status = self.http_GET(session_uri, rq_headers, authorization)
        assertion_status_ = self.response_status_check(session_uri, status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            pass
            # check if intended method is an allowable method for resource
        elif not (self.allowable_method('POST', headers)):
            assertion_status = log.WARN
            log.assertion_log('line', "~ the response headers for %s do not indicate support for POST" % session_uri)
        else:
            rq_body = {'UserName': self.SUT_prop['LoginName'], 'Password': self.SUT_prop['Password']}
            log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s' % (session_uri, rq_body))  
            json_payload, headers, status = self.http_POST(session_uri, rq_headers, rq_body, authorization)
            assertion_status_ = self.response_status_check(session_uri, status, log, rf_utility.HTTP_CREATED, 'POST')      
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            if assertion_status_ != log.PASS: 
                pass
            else:
                #session created
                # get location from the response header
                if 'location' in headers:   
                    session_location = headers['location']   
                # verify x-auth-token in header
                session_key = 'x-auth-token'
                if session_key not in headers:
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ Expected header %s to be in the response header of %s ~ Not found" % (session_key, session_uri))
                elif not headers[session_key]:
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ Expected header %s to have a value with session auth token, which is required so that the client can use this session as authentication method for subsequent requests ~ Not found" % (session_key))          

                #Terminate this session
                if session_location:
                    authorization = 'on'
                    rq_headers = self.request_headers()
                    json_payload, headers, status = self.http_DELETE(session_location, rq_headers, authorization)
                    assertion_status_ = self.response_status_check(session_location, status, log, request_type = 'DELETE')      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)

    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 9.3.1.1

###################################################################################################
# Name: Assertion_9_3_1_2(self, log)  Authentication/Sessions                                          
# Description:      	       
# The response to the POST request to create a session includes: a "Location header that contains a 
# link to the newly created session resource.
###################################################################################################
def Assertion_9_3_1_2(self, log):
 
    log.AssertionID = '9.3.1.2'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    
    #Create session
    authorization = 'on'
    rq_headers = self.request_headers()

    session_uri = None
    root_link_key = 'Sessions'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        session_uri = self.sut_toplevel_uris[root_link_key]['url']
    else:
        for rel_uris in self.relative_uris:
            if rel_uris.endswith('Sessions'):
                session_uri = self.relative_uris[rel_uris]
    if session_uri:
        json_payload, headers, status = self.http_GET(session_uri, rq_headers, authorization)
        assertion_status_ = self.response_status_check(session_uri, status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            pass
            # check if intended method is an allowable method for resource
        elif not (self.allowable_method('POST', headers)):
            assertion_status = log.WARN
            log.assertion_log('line', "~ the response headers for %s do not indicate support for POST" % session_uri)
        else:
            rq_body = {'UserName': self.SUT_prop['LoginName'], 'Password': self.SUT_prop['Password']}
            log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s' % (session_uri, rq_body))  
            json_payload, headers, status = self.http_POST(session_uri, rq_headers, rq_body, authorization)
            assertion_status_ = self.response_status_check(session_uri, status, log, rf_utility.HTTP_CREATED, 'POST')      
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            if assertion_status_ != log.PASS: 
                pass
            elif headers:
                #session created
                # verify location in the response header
                location_key = 'location'
                if location_key not in headers:
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ Expected header %s to be in the response header of POST %s ~ Not found" % (location_key, session_uri))   
                elif not headers['location']:
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ Expected header %s to have a value with a url pointing to a newly created session ~ Not found" % (location_key))   
                else:
                    session_location = headers[location_key]
                    authorization = 'on'
                    rq_headers = self.request_headers()
                    json_payload, headers, status = self.http_DELETE(session_location, rq_headers, authorization)
                    assertion_status_ = self.response_status_check(session_location, status, log, request_type = 'DELETE')      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 9.3.1.2

###################################################################################################
# Name: Assertion_9_3_1_3(self, log)  Authentication/Sessions                                        
# Description:     	       
# The response to the POST request to create a session includes:
#  The JSON response body that contains a full representation of the newly created session object
###################################################################################################  
def Assertion_9_3_1_3(self, log):
    log.AssertionID = '9.3.1.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()                       
    # the session object keys are traced as per redfish specification. See section 9.2.4.3
    session_response_keys = ['@odata.context', '@odata.id', '@odata.type', 'Id', 'Name', 'Description', 'UserName']

    #Create session
    authorization = 'on'
    rq_headers = self.request_headers()
    session_uri = None
    root_link_key = 'Sessions'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        session_uri = self.sut_toplevel_uris[root_link_key]['url']
    else:
        for rel_uris in self.relative_uris:
            if rel_uris.endswith('Sessions'):
                session_uri = self.relative_uris[rel_uris]
    if session_uri:
        json_payload, headers, status = self.http_GET(session_uri, rq_headers, authorization)
        assertion_status_ = self.response_status_check(session_uri, status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            pass
            # check if intended method is an allowable method for resource
        elif not (self.allowable_method('POST', headers)):
            assertion_status = log.WARN
            log.assertion_log('line', "~ the response headers for %s do not indicate support for POST" % session_uri)
        else:
            rq_body = {'UserName': self.SUT_prop['LoginName'], 'Password': self.SUT_prop['Password']}
            log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s' % (session_uri, rq_body))  
            json_payload, headers, status = self.http_POST(session_uri, rq_headers, rq_body, authorization)
            assertion_status_ = self.response_status_check(session_uri, status, log, rf_utility.HTTP_CREATED, 'POST')      
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            if assertion_status_ != log.PASS: 
                pass
            elif not (headers or json_payload):
                assertion_status = log.WARN
            else:
                #session created
                # get location from the response header
                if 'location' in headers:   
                    session_location = headers['location']      
                # verify JSON response body with full representation of newly created session object as per Redfish specification 
                if not any(key in json_payload.keys() for key in session_response_keys):
                    assertion_status = log.FAIL
                    try:
                        log.assertion_log('line', "~ The response body of newly created session: %s does not contain a full representation of the session object. Response body returned contains: %s" % (session_location, rf_utility.json_string(json_payload)))
                    except:
                        log.assertion_log('line', "~ The response body of newly created session does not contain a full representation of the session object. Response body returned contains: %s" % (rf_utility.json_string(json_payload)))
                else:
                    for key in session_response_keys:
                        if key not in json_payload.keys():
                            try:
                                log.assertion_log('line', "~ The response body of newly created session: %s does not contain the key: %s. Requirement is that must contain full respresentation of a session object described in the Redfish specification" % (session_location, key))
                            except:
                                log.assertion_log('line', "~ The response body of newly created session does not contain the key: %s as required by the Redfish specification" % (key))
                
                #Terminate this session
                if session_location:
                    authorization = 'on'
                    rq_headers = self.request_headers()
                    json_payload, headers, status = self.http_DELETE(session_location, rq_headers, authorization)
                    assertion_status_ = self.response_status_check(session_location, status, log, request_type = 'DELETE')      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    log.assertion_log(assertion_status, None) 
    return (assertion_status)
#
## end Assertion 9.3.1.3

###################################################################################################
# Name: Assertion_9_3_1_4(self, log)  Authentication                                             
# Description:      
# Services shall not require a client to create a session when Basic Auth is used. 
# Note did a test with session + basic auth, requests failed
###################################################################################################
def Assertion_9_3_1_4(self, log) :
 
    log.AssertionID = '9.3.1.4'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    #auth on, no session
    authorization = 'on'
    rq_headers = self.request_headers()
    relative_uris = self.relative_uris 
    authorization_key = 'Authorization'

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 9.3.1.4

###################################################################################################
# Name: Assertion_9_3_2_1(self, log)  HTTP Header Security                                            
# Description:     
# All write activities shall be authenticated, i.e. POST, except for The POST operation to the 
# Sessions service/object needed for authentication     
###################################################################################################
def Assertion_9_3_2_1(self, log) :
 
    log.AssertionID = '9.3.2.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    unauth_payload  = None
    auth_payload = None

    authorization = 'on'

    log.assertion_log('line', "~note: this assertions sub-invokes Assertion 9.3.3.1")

    rq_headers = self.request_headers()
    session_uri = None
    root_link_key = 'Sessions'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        session_uri = self.sut_toplevel_uris[root_link_key]['url']
    else:
        for rel_uris in self.relative_uris:
            if rel_uris.endswith('Sessions'):
                session_uri = self.relative_uris[rel_uris]
    if session_uri:
        json_payload, headers, status = self.http_GET(session_uri, rq_headers, authorization)
        assertion_status_ = self.response_status_check(session_uri, status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            pass
        # check if intended method is an allowable method for resource
        elif (self.allowable_method('POST', headers) != True):      
            assertion_status = log.FAIL
            log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for POST" % json_payload['@odata.id'])
            log.assertion_log('line', rf_utility.json_string(headers))
        else:          
            rq_headers = self.request_headers()
            rq_body = {'UserName': self.SUT_prop['LoginName'], 'Password': self.SUT_prop['Password']}
            rq_headers['Content-Type'] = 'application/json'
            '''1: Do a POST on session without auth, it should pass'''
            authorization = 'off'
            log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s with session authorization' % (session_uri, rq_body))  
            json_payload, headers, status = self.http_POST(session_uri, rq_headers, rq_body, authorization)
            assertion_status_ = self.response_status_check(session_uri, status, log, rf_utility.HTTP_CREATED, 'POST')      
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            if assertion_status_ != log.PASS: 
                pass
                # check if intended method is an allowable method for resource
            elif (self.allowable_method('DELETE', headers)): 
                try:    
                    session_location = headers['location']
                except:
                    assertion_status = log.WARN
                    log.assertion_log('line', "~ Expected Location in the headers of POST for %s ~ not found" %(session_uri))
                    log.assertion_log('line', rf_utility.json_string(headers))                      
                else:
                    rq_headers = self.request_headers()
                    authorization = 'on'
                    #DELETE session here
                    json_payload_, headers_, status_ = self.http_DELETE(session_location, rq_headers, authorization)
                    assertion_status_ = self.response_status_check(session_location, status_, log, request_type = 'DELETE')      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                    if assertion_status_ != log.PASS: 
                        pass
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    '''2: Now do a POST on an account without authorization, it should FAIL '''
    rq_headers = self.request_headers()
    authorization = 'on'
    # get the collection of user accounts...
    auth_payload = None
    unauth_payload = None

    if (assertion_status != log.FAIL):
        rq_headers = self.request_headers()
        # get the collection of user accounts...
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
                            log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for POST" % json_payload['@odata.id'])
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
                                        assertion_status_ = self.response_status_check(json_payload['@odata.id'], status_, log, request_type='DELETE')
                                        # manage assertion status
                                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                        if assertion_status_ != log.PASS: 
                                            break
                                        else: 
                                            log.assertion_log('XL_COMMENT', "~ note: DELETE for %s : %s PASS. HTTP status %s:%s" % (user_name, json_payload['@odata.id'], status_, rf_utility.HTTP_status_string(status_)))
                                            break
                                    else:
                                        assertion_status = log.FAIL
                                        log.assertion_log('line', "~ The response headers for %s do not indicate support for DELETE" % json_payload['@odata.id'])
                                        log.assertion_log('line', "~ Item already exists in %s and attempt to request DELETE failed, Try changing item configuration in the script" % json_payload['@odata.id'])                        
                                        break

                        if (assertion_status == log.PASS) : # Ok to create the user now
                                    
                            rq_body = {'UserName' : 'testuser' , 'Password' : 'testpass' , 'RoleId' : 'Administrator' }

                            # turn auth off for POST, it should not pass
                            authorization = 'off' 
                            rq_headers = self.request_headers()
                            log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s without authorization' % (acc_collection, rq_body))  
                            unauth_payload, headers, status = self.http_POST(acc_collection, rq_headers, rq_body, authorization)
                            assertion_status_ = self.response_status_check(acc_collection, status, log, rf_utility.HTTP_UNAUTHORIZED, 'POST')      
                            # manage assertion status
                            assertion_status = log.status_fixup(assertion_status,assertion_status_)
                            if assertion_status_ != log.PASS: 
                                pass
                            else:
                                #do POST with auth to get json_payload to compare if extended error has any privilages info
                                rq_headers = self.request_headers()
                                authorization = 'on' 
                                log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s with authorization' % (acc_collection, rq_body))  
                                auth_payload, headers, status = self.http_POST(acc_collection, rq_headers, rq_body, authorization)
                                assertion_status_ = self.response_status_check(acc_collection, status, log, rf_utility.HTTP_CREATED, 'POST')      
                                # manage assertion status
                                assertion_status = log.status_fixup(assertion_status,assertion_status_)

        else:
            assertion_status = log.WARN
            log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )
         
    run_sub_assertion = False
    if ((unauth_payload) or (auth_payload)):
        run_sub_assertion = True

    if (run_sub_assertion == False):
        log.assertion_log('line', "~ note: Assertion failures have prevented sub-invocation of related assertions")
        log.assertion_log(assertion_status, None)
        return(assertion_status)
    else:
        # completion status for this assertion...
        log.assertion_log(assertion_status, None)

        #subinvoke assertion
        Assertion_9_3_3_1(unauth_payload,auth_payload, log)                       
 
    return (assertion_status)
#
## end Assertion 9.3.2.1

###################################################################################################
# Name: Assertion_9_3_3_1(unauth_payload,auth_payload, log)  HTTP Header Security                                            
# Description:  POST
# Extended error messages shall NOT provide privileged info when authentication failures occur  
###################################################################################################
def Assertion_9_3_3_1(unauth_payload,auth_payload, log) :
 
    log.AssertionID = '9.3.3.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

     # check to see privilegd info in unauth payload
    assertion_status = checkPrivilegedinfo(unauth_payload,auth_payload, log)

    log.assertion_log(assertion_status, None)
    return (assertion_status)    
#end Assertion 9.3.3.1
           
###################################################################################################
# Name: checkPrivilegedinfo (nauth_payload, auth_payload)                                               
# Description:     
#	compare authorized and unauthorized response body, unauthorized payload should not provide 
#   privilaged information
# Assumption: any information that an authorized payload has for which authentication is required, 
# is privilaged info             
###################################################################################################
def checkPrivilegedinfo(unauth_load, auth_payload, log):
    
    assertion_status = log.PASS

    if (Python3 == True):
        unauth_payload =  b'unauth_load'
    else:
        unauth_payload = unauth_load

    # check for any matches...
    for key in auth_payload.keys():
        if (Python3 == True):
            bkey = b'key'
        else:
            bkey = key

        if (bkey in unauth_payload):
            if (unauth_payload[bkey] == auth_payload[bkey]):
                assertion_status = log.FAIL
                log.assertion_log('line', "~ Unatuhorized payload has Property \'%s\' : \'%s\' which maybe a privilaged information %s" % (key, unauth_payload[key], auth_payload[key]) )

    # print the extended error for info in xl_comment TODO
    #log.assertion_log('line', "~ Unatuhorized payload has Property \'%s\' : \'%s\' which maybe a privilaged information %s" % (key, check_payload[key], object_payload[key]) )
    return (assertion_status)

###################################################################################################
# Name: Assertion_9_3_2_2(self, log)  HTTP Header Security                                            
# Description:     
# All write activities shall be authenticated, i.e. PATCH/PUT 
# TODO - should also test PATCH account with session key?    
###################################################################################################
def Assertion_9_3_2_2(self, log) :
 
    log.AssertionID = '9.3.2.2'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    unauth_payload = ''
    auth_payload = ''
    rq_headers = self.request_headers()
    account_url = ''
    user_name = 'testuser'

    root_link_key = 'AccountService'

    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:

        log.assertion_log('line', "~ note: this assertion sub-invokes Assertion 9.3.3.2")

        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris[root_link_key]['url'], rq_headers, authorization)
        assertion_status_ = self.response_status_check(self.sut_toplevel_uris[root_link_key]['url'], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            pass
        elif not json_payload:
            assertion_status= log.WARN
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (self.sut_toplevel_uris[root_link_key]['url']))
        else: ## get Accounts collection from payload
            try :
                key = 'Accounts'
                acc_collection = (json_payload[key])['@odata.id']

            except : # no user accounts?
                assertion_status = log.WARN
                log.assertion_log('line', "~ no accounts collection was returned from GET %s" % self.sut_toplevel_uris[root_link_key]['url'])

            else:
                deleted = False
                user_exist = False
                #create temp account then delete it
                #check if user already exists, if it does perfcorm a delete to clean up
                members = self.get_resource_members(acc_collection)
                for json_payload, headers in members:
                    if json_payload['UserName'] == user_name:
                        user_exist = True
                        account_url = json_payload['@odata.id']
                        break

                if user_exist == False:                           
                    json_payload, headers, status = self.http_GET(acc_collection, rq_headers, authorization)
                    assertion_status_ = self.response_status_check(acc_collection, status, log)      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                    if assertion_status_ != log.PASS: 
                        pass
                    # check if intended method is an allowable method for resource
                    elif (self.allowable_method('POST', headers) != True):      
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for POST" % json_payload['@odata.id'])
                        log.assertion_log('line', rf_utility.json_string(headers))
                    else:
                        #create it
                        rq_body = {'UserName': 'testuser', 'Password': 'testpass', 'RoleId' : 'Administrator'}
                        log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s' % (acc_collection, rq_body))  
                        json_payload, headers, status = self.http_POST(acc_collection, rq_headers, rq_body, authorization)
                        assertion_status_ = self.response_status_check(acc_collection, status, log, rf_utility.HTTP_CREATED, 'POST')      
                        # manage assertion status
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        if assertion_status_ != log.PASS: 
                            log.assertion_log('line', "~ note: Item %s to test PUT/PATCH could not be created through script due to service errors stated, Try adding a user on the system through server management and reconfigure request body." % (user_name) )
                        else:
                            try:
                                account_url = headers['location']
                            except: 
                                assertion_status = log.WARN
                                log.assertion_log('line', "~ note: Location header expected in response for POST %s ~ not found" % (user_name))
                                log.assertion_log('line', "~ note: Could not obtain url of the newly created object, cannot request a PATCH for %s in this assertion" % (user_name))

                if (assertion_status == log.PASS or account_url != ''):
                    #got past either creating new or using existing user account
                    found = False
                    #get on account_url 
                    json_payload, headers, status = self.http_GET(account_url, rq_headers, authorization)
                    assertion_status_ = self.response_status_check(account_url, status, log)      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                    if assertion_status_ != log.PASS: 
                        pass
                    else:
                        # check if required method is an allowable method
                        if (self.allowable_method('PATCH', headers) != True):      
                            assertion_status = log.WARN
                            log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for PATCH" % json_payload['@odata.id'])
                            log.assertion_log('line', rf_utility.json_string(headers))
                                                
                        else:
                            etag = ''
                            patch_key = 'RoleId'   
                            patch_value = 'Operator'
                            try:
                                etag = headers['etag']    
                            except:
                                assertion_status = log.WARN
                                log.assertion_log('line', "~ note: Expected Etag in headers returned from %s ~ not found" %(json_payload['@odata.id']))
                                log.assertion_log('line', rf_utility.json_string(headers))                                                                                       
                                                           
                            rq_body = {'UserName': 'testuser', 'Password': 'testpass' , 'RoleId' : patch_value}
                                
                            #1: Turn auth = off and do a PATCH, it is not an expected behavior, hence it should FAIL
                            authorization = 'off' #turn auth off
                            rq_headers = self.request_headers() 
                            unauth_payload, headers, status = self.http_PATCH(account_url, rq_headers, rq_body, authorization)
                            assertion_status_ = self.response_status_check(account_url, status, log, rf_utility.HTTP_UNAUTHORIZED, 'PATCH')      
                            # manage assertion status
                            assertion_status = log.status_fixup(assertion_status,assertion_status_)
                            if assertion_status_ != log.PASS: 
                                pass                                   
                            else:
                                #check if resource remain unchanged
                                if etag is not '':
                                    rq_headers = self.request_headers()
                                    rq_headers['If-None-Match'] = etag
                                    authorization = 'on' #turn auth on
                                    json_payload, headers, status = self.http_GET(account_url, rq_headers, authorization)
                                    assertion_status_ = self.response_status_check(account_url, status, log, rf_utility.HTTP_NOTMODIFIED)      
                                    # manage assertion status
                                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                    if assertion_status_ != log.PASS: 
                                        log.assertion_log('line', "~ PATCH %s : Resource might have updated unexpectedly" % (account_url) )
                                        log.assertion_log('line', "~ Status expected %s, response status = %s" % (rf_utility.HTTP_NOTMODIFIED, status))
                                        log.assertion_log('XL_COMMENT', ('Checked if resource is modified using If-None-Match header and etag' ))
                                    else:                                                           
                                        #2: Turn auth = on and do a PATCH, to get json_payload to compare if extended error has any privilages info
                                        authorization = 'on' 
                                        rq_headers = self.request_headers()
                                        auth_payload, headers, status = self.http_PATCH(account_url, rq_headers, rq_body, authorization)
                                        assertion_status_ = self.response_status_check(account_url, status, log, request_type='PATCH')
                                        # manage assertion status
                                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                         
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    run_sub_assertion = False
    if ((unauth_payload) or (auth_payload)):
        run_sub_assertion = True

    if (run_sub_assertion == False):
        log.assertion_log('line', "~ note: Assertion failures have prevented sub-invocation of related assertions")
        log.assertion_log(assertion_status, None)
        return(assertion_status)
    else:
        # completion status for this assertion...
        log.assertion_log(assertion_status, None)

        #subinvoke assertion
        Assertion_9_3_3_2(unauth_payload,auth_payload, log)

    return(assertion_status)                 

#
## end Assertion 9.3.2.2

###################################################################################################
# Name: Assertion_9_3_3_2()  HTTP Header Security                                            
# Description:  PATCH
# Extended error messages shall NOT provide privileged info when authentication failures occur  
###################################################################################################
def Assertion_9_3_3_2(unauth_payload,auth_payload, log) :
 
    log.AssertionID = '9.3.3.2'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

     # check to see privielegd info in unauth payload
    assertion_status = checkPrivilegedinfo(unauth_payload,auth_payload, log)

    log.assertion_log(assertion_status, None)
    return (assertion_status)   

#end Assertion 9.3.3.2

###################################################################################################
# Name: Assertion_9_3_2_3(self, log)  HTTP Header Security                                            
# Description:     
# All write activities shall be authenticated, i.e. DELETE   
# TODO - should also test DELETE account with session key?  
###################################################################################################  
def Assertion_9_3_2_3(self, log) :
 
    log.AssertionID = '9.3.2.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    unauth_payload = ''
    auth_payload = ''
    rq_headers = self.request_headers()
    account_url = ''
    user_name = 'testuser'

    root_link_key = 'AccountService'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        log.assertion_log('line', "~ note: this assertion sub-invokes Assertion 9.3.3.3")
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris[root_link_key]['url'], rq_headers, authorization)
        assertion_status_ = self.response_status_check(self.sut_toplevel_uris[root_link_key]['url'], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            pass
        elif not json_payload:
            assertion_status = log.WARN  
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (self.sut_toplevel_uris[root_link_key]['url']))
        else: ## get Accounts collection from payload
            try :
                key = 'Accounts'
                acc_collection = (json_payload[key])['@odata.id']
            except : # no user accounts?
                assertion_status = log.WARN
                log.assertion_log('line', "~ no accounts collection was returned from GET %s" % self.sut_toplevel_uris[root_link_key]['url'])
            else:
                deleted = False
                user_exist = False
                #create temp account then delete it
                #check if user already exists, if it does perfcorm a delete to clean up
                members = self.get_resource_members(acc_collection)
                for json_payload, headers in members:
                    if json_payload['UserName'] == user_name:
                        user_exist = True
                        account_url = json_payload['@odata.id']
                        break

                if user_exist == False:
                    #do a GET on acc_collection and check if POST is allowed 
                    json_payload, headers, status = self.http_GET(acc_collection, rq_headers, authorization)
                    assertion_status_ = self.response_status_check(acc_collection, status, log)      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                    if assertion_status_ != log.PASS: 
                        pass
                    # check if intended method is an allowable method for resource
                    elif (self.allowable_method('POST', headers) != True):      
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for POST" % json_payload['@odata.id'])
                        log.assertion_log('line', rf_utility.json_string(headers))
                    else:
                        #create it                        
                        rq_body = {'UserName': 'testuser', 'Password': 'testpass', 'RoleId' : 'Administrator'}
                        log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s' % (acc_collection, rq_body))  
                        json_payload, headers, status = self.http_POST(acc_collection, rq_headers, rq_body, authorization)
                        assertion_status_ = self.response_status_check(acc_collection, status, log, rf_utility.HTTP_CREATED, 'POST')      
                        # manage assertion status
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        if assertion_status_ != log.PASS: 
                            log.assertion_log('line', "~ note: Item %s to test DELETE could not be created through script due to service errors stated, Try adding a user on the system through server management and reconfigure request body." % (user_name) )
                        else:
                            try:
                                account_url = headers['location']
                            except: 
                                assertion_status = log.WARN
                                log.assertion_log('line', "~ note: Location header expected in response for POST %s ~ not found" % (user_name))
                                log.assertion_log('line', "~ note: Could not obtain url of the newly created object, cannot request a DELETE for %s in this assertion" % (user_name))

                if (assertion_status == log.PASS or account_url != ''):
                        #got past either creating new or using existing user account
                        found = False
                        #get on account_url 
                        json_payload, headers, status = self.http_GET(account_url, rq_headers, authorization)
                        assertion_status_ = self.response_status_check(account_url, status, log)      
                        # manage assertion status
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        if assertion_status_ != log.PASS: 
                            pass                
                        else:
                            # check if intended method is an allowable method for resource       
                            if (self.allowable_method('DELETE', headers) != True):      
                                assertion_status = log.WARN
                                log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for DELETE" % json_payload['@odata.id'])
                                log.assertion_log('line', rf_utility.json_string(headers))
                                            
                            else:  
                                #1.auth off
                                authorization = 'off' #turn auth off
                                rq_headers = self.request_headers()     
                                unauth_payload, headers, status = self.http_DELETE(json_payload['@odata.id'], rq_headers, authorization)
                                assertion_status_ = self.response_status_check(json_payload['@odata.id'], status, log, rf_utility.HTTP_UNAUTHORIZED, 'DELETE')      
                                # manage assertion status
                                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                if assertion_status_ != log.PASS: 
                                    pass
                                else:
                                    #2.auth on, to get json_payload to compare if extended error has any privilages info
                                    authorization = 'on' 
                                    rq_headers = self.request_headers()      
                                    auth_payload, headers, status = self.http_DELETE(json_payload['@odata.id'], rq_headers, authorization)
                                    assertion_status_ = self.response_status_check(json_payload['@odata.id'], status, log, request_type = 'DELETE')             
                                    # manage assertion status
                                    assertion_status = log.status_fixup(assertion_status,assertion_status_)

    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    run_sub_assertion = False
    if ((unauth_payload) or (auth_payload)):
        run_sub_assertion = True

    if (run_sub_assertion == False):
        log.assertion_log('line', "~ note: Assertion failures have prevented sub-invocation of related assertions")
        log.assertion_log(assertion_status, None)
        return(assertion_status)
    else:
        # completion status for this assertion...
        log.assertion_log(assertion_status, None)

        #subinvoke assertion
        Assertion_9_3_3_3(unauth_payload,auth_payload, log)
          
    return (assertion_status)

#end Assertion 9.3.2.3

###################################################################################################
# Name: Assertion_9_3_3_3()  HTTP Header Security                                            
# Description:  DELETE
# Extended error messages shall NOT provide privileged info when authentication failures occur  
###################################################################################################
def Assertion_9_3_3_3(unauth_payload,auth_payload, log) :
 
    log.AssertionID = '9.3.3.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

     # check to see privielegd info in unauth payload
    assertion_status = checkPrivilegedinfo(unauth_payload,auth_payload, log)

    log.assertion_log(assertion_status, None)
    return (assertion_status)  

#end Assertion 9.3.3.3

###################################################################################################
# Name: Assertion_9_3_7(self, log)   HTTP Header Authentication                                    
# Description:    HTTP Headers for authentication shall be processed before other headers that may 
# affect the response, i.e.: etag, If-Modified, etc.
# Note:
# There could be other responses that can get affected. For now, the assertion checks for
# 'If-None-Match' with wrong auth
###################################################################################################
def Assertion_9_3_7(self, log) :

    log.AssertionID = '9.3.7'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris

    for relative_uri in relative_uris:
        #/redfish/v1/ can be requested without auth
        if relative_uris[relative_uri] == '/redfish/v1/':
            continue
        # to get an initial etag
        authorization = 'on'
        rq_headers = self.request_headers()
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            continue
        elif 'etag' in headers:
            etag = headers['etag']
        #GET on resources with etag and wrong auth
        authorization = 'off'
        rq_headers = self.request_headers()
        auth = rf_utility.http__set_auth_header(rq_headers, 'wrong id', 'wrongpass')
        rq_headers['If-None-Match'] = etag
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)
        assertion_status_ = self.response_status_check(relative_uris[relative_uri], status, log, rf_utility.HTTP_UNAUTHORIZED)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)

    log.assertion_log(assertion_status, None)

    return (assertion_status)

#
## end Assertion 9.3.7

###################################################################################################
# Name: Assertion_9_3_8(self, log)   HTTP Header Authentication                                          
# Description:   HTTP Cookies shall NOT be used to authenticate any activity i.e.: GET, POST, 
#   PUT/PATCH, and DELETE.
# -testing for GETs
# usage of cookie: store cookie from header when session is created, Cookie: value
# next send a request using Set-Cookie in header w/o x-auth token 
# Note : cookies are not being returned (this is an indication that the service is conformant) 
#   Verfcication method: For this assertion, we set a variable cookie_found in http__req_common() 
#   in rfc_service. If at any request, 'set-cookie' was returned, the variable wouldve been set to 
#   True (if the service returns cookies this is an indication of a non-conformant service)
###################################################################################################
def Assertion_9_3_8(self, log):

    log.AssertionID = '9.3.8'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    if(self.cookie_info[0] == True):
        assertion_status = log.FAIL
        for item in self.cookie_info[1]:
            log.assertion_log('line', "~ Cookie was returned by the service for request %s on resource %s" % (item[0], item[1]))
            
    log.assertion_log(assertion_status, None)

    return (assertion_status)
#
## end Assertion 9.3.8

###################################################################################################
# Name: Assertion_9_3_11_1()   Session Lifecycle Management                                    
# Description: A Redfish session is terminated when the client Logs-out. 
# This is accomplished by perfcorming a DELETE to the Session resource identified by the link returned 
# in the Location header when the session was created, or the SessionId returned in the response data.
# The ability to DELETE a Session by specifying the Session resource ID allows an administrator with 
# sufficient privilege to terminate other users sessions from a different session.
###################################################################################################

def Assertion_9_3_11_1(self, log) :
 
    log.AssertionID = '9.3.11.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
                
    session_key = 'x-auth-token'
    x_auth_token = None
    session_location = None

    #Create session
    authorization = 'on'
    rq_headers = self.request_headers()
    session_uri = None
    root_link_key = 'Sessions'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        session_uri = self.sut_toplevel_uris[root_link_key]['url']
    else:
        for rel_uris in self.relative_uris:
            if rel_uris.endswith('Sessions'):
                session_uri = self.relative_uris[rel_uris]
    if session_uri:
        json_payload, headers, status = self.http_GET(session_uri, rq_headers, authorization)
        assertion_status_ = self.response_status_check(session_uri, status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            pass
            # check if intended method is an allowable method for resource
        elif not (self.allowable_method('POST', headers)):
            assertion_status = log.WARN
            log.assertion_log('line', "~ the response headers for %s do not indicate support for POST" % session_uri)
        else:
            # request body to create session
            rq_body = {'UserName': self.SUT_prop['LoginName'], 'Password': self.SUT_prop['Password']}
            log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s' % (session_uri, rq_body))  
            json_payload, headers, status = self.http_POST(session_uri, rq_headers, rq_body, authorization)
            assertion_status_ = self.response_status_check(session_uri, status, log, rf_utility.HTTP_CREATED, 'POST')      
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            if assertion_status_ != log.PASS: 
                pass
            else:
                #session created
                #get location of session to terminate it
                location_key = 'location'
                if location_key not in headers:
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ Expected header %s to be in the response header of POST %s ~ Not found" % (location_key, session_uri))   
                elif not headers[location_key]:
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ Expected header %s to have a value with a url pointing to a newly created session ~ Not found" % (location_key))   
                else:
                    session_location = headers[location_key]
                    authorization = 'on'
                    rq_headers = self.request_headers()
                    json_payload, headers, status = self.http_DELETE(session_location, rq_headers, authorization)
                    assertion_status_ = self.response_status_check(session_location, status, log, request_type= 'DELETE')      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)

                #TODO get sessionid from response data                
                
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) ) 

    log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion 9.3.11.1

###################################################################################################
# Name: Assertion_9_3_12()   :Redfish Login Sessions                                         
# Description: The URI for establishing a session can be found in the SessionService's Session property
#  or in the Service Root's Links Section under the Sessions property.  Both URIs shall be the same.
###################################################################################################
def Assertion_9_3_12(self, log) :

    log.AssertionID = '9.3.12'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    
    #check root service links for session url
    json_payload, headers, status = self.http_GET(self.Redfish_URIs['Service_Root'], rq_headers, authorization)
    assertion_status_ = self.response_status_check(self.Redfish_URIs['Service_Root'], status, log)      
    # manage assertion status
    assertion_status = log.status_fixup(assertion_status,assertion_status_)
    if assertion_status_ != log.PASS: 
        pass    
    ## check payload for links
    elif not json_payload:
        assertion_status = log.WARN
        log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (self.Redfish_URIs['Service_Root']))
    else:
        payload = json_payload
        #1. check service roots 'Links' section
        key = 'Links' 
        if key in payload:
            for subkey in payload[key]:
                if 'Sessions' in subkey:
                    try:
                        sessionurl_link = (payload[key])[subkey]['@odata.id']
                    except:
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ note: Expected @0data.id for property %s" % (subkey))
        else:
            assertion_status = log.FAIL
            log.assertion_log('line', "~ note: Expected %s in property of url %s" % (key, self.Redfish_URIs['Service_Root']))

        #2. check SessioService's property 'Sessions'
        key = 'SessionService'
        if key in payload:
            try:
                root_service_link = (payload[key])['@odata.id']
                json_payload, headers, status = self.http_GET(root_service_link, rq_headers, authorization)
                assertion_status_ = self.response_status_check(root_service_link, status, log)      
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                if assertion_status_ != log.PASS: 
                    pass
                else: 
                    if 'Sessions' in json_payload:
                        sessionurl_sessions = json_payload['Sessions']['@odata.id'] 
                    else:
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ note: Expected 'Sessions' in resource %s" % (root_service_link))
            except:
                assertion_status = log.FAIL
                log.assertion_log('line', "~ note: Expected @0data.id for property %s" % (key))

        else:
            assertion_status = log.FAIL
            log.assertion_log('line', "~ note: Expected %s in property of url %s" % (key, self.Redfish_URIs['Service_Root']))


        if sessionurl_link is not None and sessionurl_sessions is not None:
            if sessionurl_link != sessionurl_sessions:
                assertion_status = log.FAIL
                log.assertion_log('line', "~ note: Expected session links %s and %s to be the same" % (sessionurl_link, sessionurl_sessions))       

    log.assertion_log(assertion_status, None)

    return (assertion_status)
#
## end Assertion 9.3.12

###################################################################################################
# Name: Assertion_9_3_13(self, log) Protocols TLS                                        
# Description:  Implementations shall only use compliant TLS connections to transport the data between 
#   any third party authentication service and clients. Therefore, the POST to create a new session 
#   shall 'only' be supported with HTTPS, and all requests that use Basic Auth shall 'require' HTTPS.
###################################################################################################
def Assertion_9_3_13(self, log) :
 
    log.AssertionID = '9.3.13'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()

    session_uri = None
    root_link_key = 'Sessions'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        session_uri = self.sut_toplevel_uris[root_link_key]['url']
    else:
        for rel_uris in self.relative_uris:
            if rel_uris.endswith('Sessions'):
                session_uri = self.relative_uris[rel_uris]
    if session_uri:
        json_payload, headers, status = self.http_GET(session_uri, rq_headers, authorization)
        assertion_status_ = self.response_status_check(session_uri, status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            pass   
        elif headers:  
            # check if intended method is an allowable method for resource             
            if not (self.allowable_method('POST', headers)):      
                assertion_status = log.WARN
                log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for POST" % json_payload['@odata.id'])
                log.assertion_log('line', rf_utility.json_string(headers))  
                log.assertion_log('line', "Due to the service error stated, POST to create a new session shall only be supported with HTTPS can not be tested") 
            else:     
                # POST session with HTTPS
                rq_headers = self.request_headers()
                authorization = 'off'            
                rq_body = {'UserName': self.SUT_prop['LoginName'], 'Password': self.SUT_prop['Password']}
                https_url = "https://" + self.SUT_prop['DnsName'] + session_uri
                rq_body = json.dumps(rq_body)
                response = rf_utility.http__req_resp(self.SUT_prop, "POST", https_url, rq_headers, rq_body, authorization)
                assertion_status_ = self.response_status_check(https_url, response.status, log, rf_utility.HTTP_CREATED, 'POST')      
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                if assertion_status_ != log.PASS: 
                    pass
                else:
                    try:
                        session_location = response.getheader('location')
                    except:
                        assertion_status = log.WARN
                        log.assertion_log('line', "~ Expected Location in the headers of POST for %s, not found" %(session_uri))
                        log.assertion_log('line', rf_utility.json_string(headers))
                    else:
                        authorization = 'on'
                        rq_headers = self.request_headers()                   
                        #DELETE session
                        json_payload, headers, status = self.http_DELETE(session_location, rq_headers, authorization)
                        assertion_status_ = self.response_status_check(session_location, status, log, request_type = 'DELETE')      
                        # manage assertion status
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        if assertion_status_ != log.PASS: 
                            pass
                                        
                #2.POST session with HTTP
                rq_headers = self.request_headers()
                authorization = 'off'
                rq_body = {'UserName': self.SUT_prop['LoginName'], 'Password': self.SUT_prop['Password']}
                http_url = "http://" + self.SUT_prop['DnsName'] + session_uri
                rq_body = json.dumps(rq_body) 
                response = rf_utility.http__req_resp(self.SUT_prop, "POST", http_url, rq_headers, rq_body, authorization)        
                if (response.status == rf_utility.HTTP_CREATED) :
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ POST for Session creation for user name %s passed without the required HTTPS on url %s : HTTP status %s:%s, which is not the required behavior" % (self.SUT_prop['LoginName'], session_uri, response.status, rf_utility.HTTP_status_string(response.status)))                    
                    try:
                        session_location = response.getheader('location')
                    except:
                        assertion_status = log.WARN
                        log.assertion_log('line', "~ Expected Location in the headers of POST for %s, not found" %(session_uri))
                        log.assertion_log('line', rf_utility.json_string(headers))
                    else:                   
                        #DELETE session
                        authorization = 'on'
                        rq_headers = self.request_headers()
                        json_payload, headers, status = self.http_DELETE(session_location, rq_headers, authorization)
                        assertion_status_ = self.response_status_check(session_location, status, log, request_type = 'DELETE')      
                        # manage assertion status
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                         
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 9.3.13

###################################################################################################
# Name: Assertion_9_3_13_1(self, log)   Protocols TLS                                      
# Description:  Implementations shall only use compliant TLS connections to transport the data between 
#   any third party authentication service and clients therefore all requests that use Basic Auth 
#   shall 'require' HTTPS.
###################################################################################################
def Assertion_9_3_13_1(self, log) :
 
    log.AssertionID = '9.3.13.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    authorization = 'on'
    rq_headers = self.request_headers()
    relative_uris = self.relative_uris 

    for relative_uri in relative_uris:
        #/redfish/v1/ can be requested without auth
        if relative_uris[relative_uri] == '/redfish/v1/':
            continue
        # GET with HTTPS
        https_url = "https://" + self.SUT_prop['DnsName'] + relative_uris[relative_uri]
        response = rf_utility.http__req_resp(self.SUT_prop, "GET", https_url, rq_headers, None, authorization)    
        assertion_status_ = self.response_status_check(https_url, response.status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)

        # GET with HTTP
        http_url = "http://" + self.SUT_prop['DnsName'] + relative_uris[relative_uri]
        response = rf_utility.http__req_resp(self.SUT_prop, "GET", http_url, rq_headers, None, authorization)    
        if (response.status == rf_utility.HTTP_OK) :
            assertion_status = log.FAIL
            log.assertion_log('line',"~ GET %s passed without the required protocol 'HTTPS' : HTTP status %s:%s, which is not the expected status" % (http_url, response.status, rf_utility.HTTP_status_string(response.status)) )           
        elif response.status == rf_utility.HTTP_NOT_FOUND:
            log.assertion_log('TX_COMMENT',"WARN: GET %s failed : HTTP status %s:%s" % (http_url, response.status, rf_utility.HTTP_status_string(response.status)) )       


    log.assertion_log(assertion_status, None)
    return (assertion_status)  
#
## end Assertion 9.3.13.1

###################################################################################################
# Name: Assertion_9_3_14(self, log)   AccountService    WIP                                
# Description: Implementations may support exporting user accounts with passwords, but shall do so using
#   encryption methods to protect them. Encryption mechanism found on page 114 
###################################################################################################

###################################################################################################
# Name: Assertion_9_3_15(self, log)   AccountService     bit unclear...                           
# Description:    1. User accounts shall support ETags and shall support atomic operations
# Note: with each atomic operation on accounts, request with etag in header?
# Note 2: User management activity is atomic, so GET POST PATCH DELETE on account objects?
###################################################################################################
def Assertion_9_3_15(self, log) :

    log.AssertionID = '9.3.15'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    etag_header = 'etag'
    atomic_operation = ['POST', 'PATCH', 'DELETE']

    root_link_key = 'AccountService'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris[root_link_key]['url'], rq_headers, authorization)
        assertion_status_ = self.response_status_check(self.sut_toplevel_uris[root_link_key]['url'], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            pass
                
        elif not json_payload: ## get Accounts collection from Account Service response
            assertion_status = log.WARN
            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (self.sut_toplevel_uris[root_link_key]['url']))
        else:
            try :
                key = 'Accounts'
                acc_collection = (json_payload[key])['@odata.id']
            except : # no user accounts?
                assertion_status = log.WARN
                log.assertion_log('line', "~ no accounts collection was returned from GET %s" % self.sut_toplevel_uris[root_link_key]['url'])           
            else:
                ## Found the key in the payload, try a GET on the link for a response header
                    json_payload, headers, status = self.http_GET(acc_collection, rq_headers, authorization)
                    assertion_status_ = self.response_status_check(acc_collection, status, log)      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                    if assertion_status_ != log.PASS: 
                        pass
                    else:
                        members = self.get_resource_members(json_payload = json_payload)
                        for json_payload, headers in members:
                            #1. check for etag
                            if etag_header not in headers:
                                assertion_status = log.FAIL
                                log.assertion_log('line', "~ note: %s not found in headers, %s not supported by Account Service %s" % (etag_header, etag_header, json_payload['@odata.id']))
                                log.assertion_log('TX_COMMENT', rf_utility.json_string(headers))
                            #2. shall support atomic operations
                            if not any(self.allowable_method(op, headers) for op in atomic_operation ):
                                assertion_status = log.FAIL
                                log.assertion_log('line', "~ note: None of the atomic operations %s found in header of %s" % (atomic_operation, json_payload['@odata.id']) )
                                log.assertion_log('TX_COMMENT', rf_utility.json_string(headers))


                            #TODO
                            #else: test operations with etags..should be supported 
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    log.assertion_log(assertion_status, None)

    return (assertion_status)
#
## end Assertion 9.3.15


###################################################################################################
# Name: Assertion_9_3_18(self, log)   Privilege Model / Authorization                               
# Description:   A Role is a defined set of Privileges.   Therefore, two roles with the same 
#   privileges shall behave equivalently.
# Method: Create 3 users, one admin, one readonly and one operator, the set of privilages that are 
#   intersected should have same response for all three users
# Privileges:
#  ~ A privilege is a permission to perfcorm an operation (e.g. Read, Write) within a defined 
#   management domain (e.g. Configuring Users).
#  ~ The Redfish specification defines a set of "assigned privileges" in the AssignedPrivileges 
#   array in the Role resource.
# NOTE: Roles not found in redfish/v1/AccountService
###################################################################################################
def Assertion_9_3_18(self, log):
    log.AssertionID = '9.3.18'
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
            ## get Accounts and Roles collection from payload
            try :
                key = 'Roles'
                roles_collection = (json_payload[key])['@odata.id']
            except :
                assertion_status = log.FAIL
                log.assertion_log('line', "~ \'Roles\' expected but not found in the payload from GET %s" % (self.sut_toplevel_uris[root_link_key]['url']))
                log.assertion_log('line', "Due to the service error stated, POST user Account with privileges/roles and their behavior comparision cannot be tested")  
            else:
                try:
                    key = 'Accounts'
                    acc_collection = (json_payload[key])['@odata.id']
                except :
                    assertion_status = log.WARN
                    log.assertion_log('line', "~ \'Accounts\' expected but not found in the payload from GET %s" % (self.sut_toplevel_uris[root_link_key]['url']))
                    log.assertion_log('line', "Due to the service error stated, POST user Account with privileges/roles and their behavior comparision cannot be tested") 
                else:
                    ## Found the key in the payload, try a GET on the link for a response header
                    roles_payload, headers, status = self.http_GET(roles_collection, rq_headers, authorization)
                    assertion_status_ = self.response_status_check(roles_collection, status, log)      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                    if assertion_status_ != log.PASS: 
                        pass
                    else:
                        members = self.get_resource_members(roles_collection)
                        privileges = {}
                        for json_payload, headers in members:
                            privileges[json_payload['Id']] = json_payload['@odata.id']

                        #create number of users == privileges collection 
                        if not (bool(privileges)):
                            assertion_status = log.WARN
                            log.assertion_log('line', "~ note: List of privileges expected from %s, ~ not found" %(roles_payload['@odata.id']))
                            log.assertion_log('line', "Due to the service error stated, POST user Account with privileges/roles and their behavior comparision cannot be tested")  
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
                                assertion_status = log.WARN
                                log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for POST" % json_payload['@odata.id'])
                                log.assertion_log('line', rf_utility.json_string(headers))  
                                log.assertion_log('line', "Due to the service error stated, POST user Account with privileges/roles and their behavior comparision cannot be tested")  
                            else:                                  
                                for roles in privileges.iterkeys():                                                                             
                                    members = self.get_resource_members(acc_collection)
                                        #check if user already exists, if it does perfcorm a delete to clean up
                                    for json_payload, headers in members:
                                        if json_payload['UserName'] == 'testuser' + roles:       
                                            log.assertion_log('TX_COMMENT', "~ note: the %s account pre-exists... deleting it now in prep for creation" % json_payload['UserName'])            
                                            json_payload_, headers_, status_ = self.http_DELETE(json_payload['@odata.id'], rq_headers, authorization)
                                            assertion_status_ = self.response_status_check(json_payload['@odata.id'], status_, log, request_type = 'DELETE')      
                                            # manage assertion status
                                            assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                            if assertion_status_ != log.PASS:       
                                                break
                                            else: 
                                                log.assertion_log('TX_COMMENT', "~ note: DELETE %s PASS" % (json_payload['@odata.id']))
                                                break
                                    if(assertion_status == log.PASS) : # Ok to create the user now
                                        #creating new account 
                                        rq_body = {'UserName' : 'testuser' , 'Password' : 'testpass' , 'RoleId' : roles}               
                                        rq_headers['Content-Type'] = 'application/json'
                                        log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s' % (acc_collection, rq_body))  
                                        json_payload, headers, status = self.http_POST(acc_collection, rq_headers, rq_body, authorization)
                                        assertion_status_ = self.response_status_check(acc_collection, status, log, rf_utility.HTTP_CREATED, 'POST')      
                                        # manage assertion status
                                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                        if assertion_status_ != log.PASS: 
                                            log.assertion_log('TX_COMMENT', "~ note: Behavior for %s could not be tested" %(roles))
                                        else:
                                            priv_count -=1 
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

           #TODO: Compare behaviour of differnet users with same privilages                          
   
    log.assertion_log(assertion_status, None) 
    return (assertion_status)

## end Assertion 9.3.18

###################################################################################################
# Name: Assertion_9_3_19(self, log)   Privilege Model / Authorization                               
# Description:   This specification defines a set of pre-defined roles, one of which shall be 
#   assigned to a user when a user is created.
# Method: Create a user without any pre-defined role, should not pass, create with one, should pass
#   ~ The pre-defined roles shall be created as follows:
#   ~ Role Name  = "Administrator"
#      ~ AssignedPrivileges = Login, ConfigureManager, ConfigureUsers, ConfigureComponents, ConfigureSelf
#    ~ Role Name = "Operator"
#      ~ AssignedPrivileges = Login, ConfigureComponents, ConfigureSelf
#    ~ Role Name = "ReadOnly"
#      ~ AssignedPrivileges = Login, ConfigureSelf
###################################################################################################
def Assertion_9_3_19(self, log):
    log.AssertionID = '9.3.19'
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
            ## get Accounts and Roles collection from payload
            try :
                key = 'Roles'
                roles_collection = (json_payload[key])['@odata.id']

            except :
                assertion_status = log.FAIL
                log.assertion_log('line', "~ \'Roles\' expected but not found in the payload from GET %s" % (self.sut_toplevel_uris[root_link_key]['url']))
                log.assertion_log('line', "Due to the service error stated, POST user Account with privileges/roles cannot be tested") 
            else:
                try:
                    key = 'Accounts'
                    acc_collection = (json_payload[key])['@odata.id']
                except :
                    assertion_status = log.WARN
                    log.assertion_log('line', "~ \'Accounts\' expected but not found in the payload from GET %s" % (self.sut_toplevel_uris[root_link_key]['url']))
                    log.assertion_log('line', "Due to the service error stated, POST user Account with privileges/roles cannot be tested")  
    
                else: 
                    roles_payload, headers, status = self.http_GET(roles_collection, rq_headers, authorization)
                    assertion_status_ = self.response_status_check(roles_collection, status, log)      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                    if assertion_status_ != log.PASS: 
                        pass
                    else:
                        members = self.get_resource_members(roles_collection)
                        privileges = {}
                        for json_payload, headers in members:
                            privileges[json_payload['Id']] = json_payload['@odata.id']
                                           
                        if not (bool(privileges)):
                            assertion_status = log.WARN
                            log.assertion_log('line', "~ note: List of privileges expected from %s, ~ not found" %(roles_payload['@odata.id']))
                            log.assertion_log('line', "Due to the service error stated, POST user Account with privileges/roles cannot be tested") 
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
                                assertion_status = log.WARN
                                log.assertion_log('line', "~ note: the header returned from GET %s do not indicate support for POST" % json_payload['@odata.id'])
                                log.assertion_log('line', rf_utility.json_string(headers))  
                                log.assertion_log('line', "Due to the service error stated, POST user Account with privileges/roles cannot be tested") 
                            else:
                                #check if user already exists, if it does perfcorm a delete to clean up
                                members = self.get_resource_members(acc_collection)
                                for json_payload, headers in members:
                                    if json_payload['UserName'] == 'testuser':       
                                        log.assertion_log('TX_COMMENT', "~ note: the %s account pre-exists... deleting it now in prep for creation" % json_payload['UserName'])            
                                        json_payload_, headers_, status_ = self.http_DELETE(json_payload['@odata.id'], rq_headers, authorization)
                                        assertion_status_ = self.response_status_check(json_payload['@odata.id'], status_, log, request_type = 'DELETE')      
                                        # manage assertion status
                                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                        if assertion_status_ != log.PASS: 
                                            break
                                        else: 
                                            log.assertion_log('TX_COMMENT', "~ note: DELETE %s PASS" % (json_payload['@odata.id']))
                                            break

                                if(assertion_status == log.PASS) : # Ok to create the user now
                                    #creating new account try any/all keys
                                    for roles in privileges.iterkeys():
                                        rq_body = {'UserName': 'testuser', 'Password': 'testpass', 'RoleId' : roles}	
                                        log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s' % (acc_collection, rq_body))             
                                        json_payload, headers, status = self.http_POST(acc_collection, rq_headers, rq_body, authorization)
                                        assertion_status_ = self.response_status_check(acc_collection, status, log, rf_utility.HTTP_CREATED, 'POST')      
                                        # manage assertion status
                                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )
            
    log.assertion_log(assertion_status, None) 
    return (assertion_status)

## end Assertion 9.3.19

###################################################################################################
# Name: Assertion_9_3_20(self, log)   Privilege Model / Authorization                               
# Description:   
#   ~ The pre-defined roles shall be created as follows:
#   ~ Role Name  = "Administrator"
#      ~ AssignedPrivileges = Login, ConfigureManager, ConfigureUsers, ConfigureComponents, ConfigureSelf
#    ~ Role Name = "Operator"
#      ~ AssignedPrivileges = Login, ConfigureComponents, ConfigureSelf
#    ~ Role Name = "ReadOnly"
#      ~ AssignedPrivileges = Login, ConfigureSelf
###################################################################################################
def Assertion_9_3_20(self, log):
    log.AssertionID = '9.3.20'
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
            ## get Accounts and Roles collection from payload
            try :
                key = 'Roles'
                roles_collection = (json_payload[key])['@odata.id']

            except :
                assertion_status = log.FAIL
                log.assertion_log('line', "~ \'Roles\' expected but not found in the payload from GET %s" % (self.sut_toplevel_uris[root_link_key]['url']))
            else:
                try:
                    key = 'Accounts'
                    acc_collection = (json_payload[key])['@odata.id']
                except :
                    assertion_status = log.WARN
                    log.assertion_log('line', "~ \'Accounts\' expected but not found in the payload from GET %s" % (self.sut_toplevel_uris[root_link_key]['url']))   
                else:
                    ## Found the key in the payload, try a GET on the link for a response header
                        roles_payload, headers, status = self.http_GET(roles_collection, rq_headers, authorization)
                        assertion_status_ = self.response_status_check(roles_collection, status, log)      
                        # manage assertion status
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        if assertion_status_ != log.PASS: 
                            pass
                        else:
                           members = self.get_resource_members(roles_collection)
                           privileges = {}
                           for json_payload, headers in members:
                                privileges[json_payload['Id']] = json_payload['@odata.id']
                           
                           if not (bool(privileges)):
                               assertion_status = log.WARN
                               log.assertion_log('line', "~ note: List of privileges expected from %s, ~ not found" %(roles_payload['@odata.id']))
                           else:           
                               #check all roles are predefined
                               if privileges is not None:
                                   role = 'Administrator'
                                   if role not in privileges:
                                       assertion_status = log.FAIL
                                       log.assertion_log('line', "~ Role : %s not found in (%s)" % (role, roles_collection) )
                                   role = 'Operator'
                                   if role not in privileges:
                                       assertion_status = log.FAIL
                                       log.assertion_log('line', "~ Role : %s not found in (%s)" % (role, roles_collection) )
                                   role = 'ReadOnly'
                                   if role not in privileges:
                                       assertion_status = log.FAIL
                                       log.assertion_log('line', "~ Role : %s not found in (%s)" % (role, roles_collection) )

    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )                         
   
    log.assertion_log(assertion_status, None) 
    return (assertion_status)

## end Assertion 9.3.20

###################################################################################################
# Name: Assertion_9_3_21(self, log)   Privilege Model / Authorization     #TODO                          
# Description:   Implementations shall support all of the pre-defined roles.

# Method: Try them all, should support all
###################################################################################################
def Assertion_9_3_21(self, log):
    log.AssertionID = '9.3.21'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    log.assertion_log(assertion_status, None) 
    return (assertion_status)

## end Assertion 9.3.21

###################################################################################################
# Name: Assertion_9_3_22()   Privilege Model / Authorization    WIP                           
# Description:   The privilege array defined for the predefined roles shall not be modifiable.
###################################################################################################
def Assertion_9_3_22(self, log):
    log.AssertionID = '9.3.22'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    
    # get the collection of user accounts...
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
            ## get Accounts and Roles collection from payload
            try :
                key = 'Roles'
                roles_collection = (json_payload[key])['@odata.id']

            except :
                assertion_status = log.FAIL
                log.assertion_log('line', "~ \'Roles\' expected but not found in the payload from GET %s" % (self.Redfish_URIs['Account_Service']))

        #else check allowable_methods
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )

    log.assertion_log(assertion_status, None) 
    return (assertion_status)
## end Assertion 9.3.22

###################################################################################################
# Name: Assertion_9_3_23(self, log)   Privilege Model / Authorization   WIP                            
# Description: ETag Handling:
#  ~ Implementations shall enforce the same privilege model for ETag related activity as is enforced 
#   for the data being represented by the ETag.
#  ~ For example, when activity requiring privileged access to read data item represented by ETag 
#   requires the same privileged access to read the ETag.Implementations shall log authentication
#   requests including failures.
###################################################################################################
## end Assertion 9.3.23

###################################################################################################
# run(self, log):
# Takes sut obj and logger obj 
###################################################################################################
def run(self, log):
    #Section 9 Sessions
    assertion_status = Assertion_9_3_1(self, log)
    assertion_status = Assertion_9_3_1_1(self, log)  
    assertion_status = Assertion_9_3_1_2(self, log)  
    assertion_status = Assertion_9_3_1_3(self, log)        
    assertion_status = Assertion_9_3_1_4(self, log)              
    assertion_status = Assertion_9_3_2_1(self, log) # Calls Assertion 9_3_3_1() within the code                                  
    assertion_status = Assertion_9_3_2_2(self, log) # Calls Assertion 9_3_3_2() within the code                  
    assertion_status = Assertion_9_3_2_3(self, log) # Calls Assertion 9_3_3_3() within the code      
    # commenting out the following, service stops responding shortly after serveral wrong credential attempts.. 
    #assertion_status = Assertion_9_3_7(self, log)                
    assertion_status = Assertion_9_3_8(self, log)
    assertion_status = Assertion_9_3_11_1(self, log)
    assertion_status = Assertion_9_3_12(self, log)
    assertion_status = Assertion_9_3_13(self, log)
    assertion_status = Assertion_9_3_13_1(self, log)
    assertion_status = Assertion_9_3_15(self, log)     
    assertion_status = Assertion_9_3_18(self, log)         
    assertion_status = Assertion_9_3_19(self, log)
    assertion_status = Assertion_9_3_20(self, log)
