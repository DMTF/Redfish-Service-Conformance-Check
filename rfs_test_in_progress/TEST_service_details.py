#####################################################################################################
# File: rfs_check.py
# Description: Redfish service conformance check tool. This module contains implemented assertions for 
#   SUT.These assertions are based on operational checks on Redfish Service to verify that it conforms 
#   to the normative statements from the Redfish specification. 
#   See assertions in redfish-assertions.xlxs for assertions summary
#
# Licensed under the Apache license: http://www.apache.org/licenses/LICENSE-2.0
# Verified/operational Python revisions (Windows OS) :
#       2.7.10
#       3.4.3
#
# Initial code released : 01/2016 
#   Steve Krig      ~ Intel 
#   Fatima Saleem   ~ Intel
#   Priyanka Kumari ~ Texas Tech University
#  2015 Intel Corporation
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
# Name: Assertion_8_1_3(self, log)                                               
# Description: 
#   Client Event subscription creation    
# Assertion text: 
#   Services shall respond to a successful subscription with HTTP status 201 and set the HTTP 
#   Location header to the address of a new subscription resource.                                           
###################################################################################################              
def Assertion_8_1_3(self, log) :
 
    log.AssertionID = '8.1.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
    # get the configuration parameters for events related assertions from the config.json file
    Conformant_evt_rq_body = self.Conformant_evt_rq_body 
    Submit_Test_Event = self.Submit_Test_Event

    # build a uri for the local  event handler / http server
    client_ip_addr = socket.gethostbyname(socket.gethostname())
    evt_service_url = ('https://%s/' % client_ip_addr)

    ## Note: the service this code is being developed against does not recognize the "Protocol" 
    ##  Property in the POST body (although it is 'required on create') and will return HTTP BAD REQUEST 
    ##  if the POST contains this Property with extended status 'Property Unknown'
    # this is the body which seems to work for that particular service..
    NoProtocol_evt_rq_body = Conformant_evt_rq_body
    NoProtocol_evt_rq_body.pop('Protocol', None)

    ## choose one of above to drive the test -~ several subsequent assertions depend on this one passing...
    EventRequestBody = Conformant_evt_rq_body      
    #EventRequestBody = NoProtocol_evt_rq_body 
            
    # get the event service properties...
    root_link_key = 'EventService'
    if root_link_key in self.sut_toplevel_uris and self.sut_toplevel_uris[root_link_key]['url']:
        json_payload, headers, status = self.http_GET(self.sut_toplevel_uris[root_link_key]['url'], rq_headers, authorization)
        assertion_status_ = self.response_status_check(self.sut_toplevel_uris[root_link_key]['url'], status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
        if assertion_status_ != log.PASS: 
            pass
        # check if intended method is an allowable method for resource
        elif (self.allowable_method('POST', headers) == False):
            assertion_status = log.FAIL
            # POST is used to modify properties of the event service so it must be supported
            log.assertion_log('line', "~ the response headers for %s do not indicate support for POST" % self.sut_toplevel_uris[root_link_key]['url'])
        else:
            try:
                if (json_payload['Status']['State'] != 'Enabled'):
                    assertion_status = log.WARN
                    log.assertion_log('line', "~ Unable to verify assertion, GET %s : payload Status:State does not show that the Event Service is Enabled" % self.sut_toplevel_uris[root_link_key]['url'] )
            except:
                assertion_status = log.FAIL
                log.assertion_log('line', "~ GET %s : payload does not contain \'Status:State\'" % self.sut_toplevel_uris[root_link_key]['url'] )
                      
        if (assertion_status == log.PASS):
            try :
                evt_key = 'EventTypesForSubscription'
                evt_collection = (json_payload[evt_key])
            except :
                assertion_status = log.FAIL
                log.assertion_log('line', "~ \'%s\' not found in the payload from GET %s" % (evt_key, self.sut_toplevel_uris[root_link_key]['url']))
            try :
                key = 'Subscriptions'
                evt_subscriptions = (json_payload[key]['@odata.id'])
            except :
                assertion_status = log.FAIL
                log.assertion_log('line', "~ \'%s\' not found in the payload from GET %s" % (key, self.sut_toplevel_uris[root_link_key]['url']))

            if (assertion_status == log.PASS):
                # GET the Subscriptions URI and check that POST is supported
                json_payload, headers, status = self.http_GET(evt_subscriptions, rq_headers, authorization)
                assertion_status_ = self.response_status_check(evt_subscriptions, status, log)      
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                if assertion_status_ != log.PASS: 
                    pass                  
                else:
                    # check if intended method is an allowable method for resource
                    if (self.allowable_method('POST', headers) != True):
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ the response headers for %s do not indicate support for POST" % evt_subscriptions)
                        
                    elif not json_payload:
                        assertion_status = log.WARN
                        log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (evt_subscriptions))
                    else:
                        # save member count prior to subscribing ~ for verification of subscription success
                        try:
                            key = 'Members@odata.count'
                            member_count = json_payload[key]                      
                        except:
                            assertion_status = log.FAIL
                            log.assertion_log('line', "~ \'%s\' not found in the payload from GET %s" % (key, evt_subscriptions))

                    if (assertion_status == log.PASS):
                        # build a uri for the local  event handler / http server
                        client_ip_addr = socket.gethostbyname(socket.gethostname())
                        evt_service_url = ('https://%s/' % client_ip_addr)

                        ## as it turns out ~ the service this is being coded against has formatting rules for event 
                        ## service url which are outside of the content of the Redfish specification.  If these 
                        ## formatting rules are not followed ~ the service will fail the subscription/POST request with 
                        ## HTTP BAD REQUEST
                        ## 1. the url of the client http event handler must be visable via https (not http)
                        ## 2. the url must contain a '/' follwing the authority portion of the URL --
                        ##   for example: https://Bob.Darnit.com  generates a HTTP BAD REQUEST but https://Bob.Darnit.com/ does not
                        ## Note also: not related to URI that the service this code is being developed against does not recognize "Protocol" 
                        ##  in the POST body as a vaild parameter and will return HTT BAD REQUEST if the POST contains this

                        evt_subscribe_key = 'ResourceAdded'
                        if (evt_subscribe_key not in evt_collection):
                            assertion_status = log.FAIL 
                            log.assertion_log('line', "~ expected event type %s is not in %s" % (evt_subscribe_key, evt_key))                                  
                        else:       	
                            rq_headers['Content-Type'] = rf_utility.accept_type['json']
                            log.assertion_log('TX_COMMENT', 'Requesting POST on resource %s with request body %s' % (evt_subscriptions, EventRequestBody))  
                            # subscribe...
                            json_payload, headers, evt_create_status = self.http_POST(evt_subscriptions, rq_headers, EventRequestBody, authorization)
                            assertion_status_ = self.response_status_check(evt_subscriptions, status, log, rf_utility.HTTP_CREATED, 'POST')      
                            # manage assertion status
                            assertion_status = log.status_fixup(assertion_status,assertion_status_)
                            if assertion_status_ != log.PASS: 
                                pass
                                
                            else:
                                # get the uri of the subscription from the location header
                                try:
                                    key = 'location'
                                    evt_subscription_uri = headers[key]
                                    #store the successful subscription uri etc. for related Assertions
                                    # 8.1.4 and 8.1.5x
                                    self.Assertion8_1_3EventSubscriptionURI = evt_subscription_uri
                                    self.Assertion8_1_3EventSubscriptionJSON = EventRequestBody
                                    self.Assertion8_1_3EventSubscriptionPayload = json_payload                                                             
                                except:
                                    assertion_status = log.FAIL
                                    log.assertion_log('line', '~ the response headers do not contain the required \'%s\' header' % key)

                                if (assertion_status == log.PASS):
                                   # GET the Subscriptions URI and verify that subscription collections count has been incremented...
                                    json_payload, headers, status = self.http_GET(evt_subscriptions, rq_headers, authorization)
                                    assertion_status_ = self.response_status_check(evt_subscriptions , status, log)      
                                    # manage assertion status
                                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                                    if assertion_status_ != log.PASS: 
                                        pass
                                    elif not json_payload:
                                        assertion_status = log.WARN
                                        log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (evt_subscriptions))
                                    else:
                                        try:
                                            key = 'Members@odata.count'
                                            member_count2 = json_payload[key]
                                            if (member_count2 <= member_count):
                                                assertion_status = log.WARN
                                                log.assertion_log('line', "~ %s  %s not incremented as expected after POST of new event subscription" % (evt_subscriptions, key))              
                                        except:
                                            assertion_status = log.FAIL
                                            log.assertion_log('line', "~ \'%s\' not found in the payload from GET %s" % (key, evt_subscriptions))       
                                            
    else:
        assertion_status = log.WARN
        log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )                       

    log.assertion_log(assertion_status, None)

    return (assertion_status)
#
## end Assertion 8_1_3

###################################################################################################
# Name: Assertion_8_1_4(self, log)                                               
# Description: 
#   Client Event subscription deletion   ~ this should be run after Assertion 8.1.3 is run
# Assertion text: 
#  Clients shall terminate a subscription by sending an HTTP DELETE message to the URI of the 
#  subscription resource                                       
###################################################################################################              
def Assertion_8_1_4(self, log) :
 
    log.AssertionID = '8.1.4'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()

    if (self.Assertion8_1_3EventSubscriptionURI == None):
        assertion_status = log.WARN
        log.assertion_log('line', " The assertion 8.1.3 event subscription failed... no subscription to delete") 
    
    else: 
        # get the event service properties...
        root_link_key = 'EventService'
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
                try:
                    if (json_payload['Status']['State'] != 'Enabled'):
                        assertion_status = log.WARN
                        log.assertion_log('line', "~ GET %s : Status does not show the Event Service is Enabled" % (self.sut_toplevel_uris[root_link_key]['url'], status) )
                    
                except:
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ GET %s : payload does not contain \'Status:State\'" % (self.sut_toplevel_uris[root_link_key]['url'], status) )
                
                try :
                    key = 'Subscriptions'
                    evt_subscriptions = (json_payload[key]['@odata.id'])
                except :
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ \'%s\' not found in the payload from GET %s" % (key, self.sut_toplevel_uris[root_link_key]['url']))
        
                # GET the Subscriptions URI...
                json_payload, headers, status = self.http_GET(evt_subscriptions, rq_headers, authorization)
                assertion_status_ = self.response_status_check(evt_subscriptions , status, log)      
                # manage assertion status
                assertion_status = log.status_fixup(assertion_status,assertion_status_)
                if assertion_status_ != log.PASS: 
                    pass       
                elif not json_payload:
                    assertion_status = log.WARN
                    log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (evt_subscriptions))
                else:
                # ...save member count prior to removing the subscription ~ for verification of removal
                    try:
                        key = 'Members@odata.count'
                        member_count = json_payload[key]                       
                    except:
                        assertion_status = log.FAIL
                        log.assertion_log('line', "~ \'%s\' not found in the payload from GET %s" % (key, evt_subscriptions))              
             
                    # delete the subscription 
                    json_payload, headers, status = self.http_DELETE(self.Assertion8_1_3EventSubscriptionURI, rq_headers, authorization)
                    assertion_status_ = self.response_status_check(self.Assertion8_1_3EventSubscriptionURI , status, log, request_type = 'DELETE')      
                    # manage assertion status
                    assertion_status = log.status_fixup(assertion_status,assertion_status_)
                    if assertion_status_ != log.PASS: 
                        pass       
                    else:
                        # verify that subscription collections count has been decremented...
                        json_payload, headers, status = self.http_GET(evt_subscriptions, rq_headers, authorization)
                        assertion_status_ = self.response_status_check(evt_subscriptions, status, log)      
                        # manage assertion status
                        assertion_status = log.status_fixup(assertion_status,assertion_status_)
                        if assertion_status_ != log.PASS: 
                            pass       
                        elif not json_payload:
                            assertion_status = log.WARN
                            log.assertion_log('line', 'No response body returned for resource %s. This assertion for the resource could not be completed' % (evt_subscriptions))
                        else:
                            try:
                                key = 'Members@odata.count'
                                member_count2 = json_payload[key]
                                if (member_count2 >= member_count):
                                    assertion_status = log.FAIL
                                    log.assertion_log('line', "~ %s  %s not decremented as expected after POST of new event subscription" % (evt_subscriptions, key))              
                            except:
                                assertion_status = log.FAIL
                                log.assertion_log('line', "~ \'%s\' not found in the payload from GET %s" % (key, evt_subscriptions))    
                    
        else:
            assertion_status = log.WARN
            log.assertion_log('line', "~ Uri to resource: %s not found in redfish top level links: %s" % (root_link_key, self.sut_toplevel_uris) )                   

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 8_1_4

###################################################################################################
# Name: Assertion_8_1_5(self, log)                                               
# Description: 
#   Client Event subscription creation ~ resp header checks    
# Assertion text: 
# On success, the "subscribe" action shall return with HTTP status 201 (CREATED) and the Location
# header in the response shall contain a URI giving the location of the newly created "subscription" 
# resource.                                   
###################################################################################################             
def Assertion_8_1_5(self, log) :
 
    log.AssertionID = '8.1.5'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()
   
    # the response headers were checked and 'location' of the subscription was stored during run of 8.1.3
    if (self.Assertion8_1_3EventSubscriptionURI == None):
        assertion_status = log.WARN
        log.assertion_log('line', " The assertion 8.1.3 event subscription failed... no subscription response headers to check") 

    log.assertion_log(assertion_status, None)

    return (assertion_status)
#
## end Assertion 8_1_5

###################################################################################################
# Name: EventAssertionPropertyCheck()                                              
# Description: supporting routine for event assertions -~ common code
#   given a event creation (reference) payload and check payload, verify that the 
#   keys and values in the check payload match the reference
###################################################################################################              
def EventAssertionPropertyCheck(creation_payload, check_payload, log):
    assertion_status = log.PASS
    # check for mismatch...
    for key in creation_payload.keys():
        if (key in check_payload):
            if (check_payload[key] != creation_payload[key]):
                assertion_status = log.FAIL
                log.assertion_log('line', "~ Event subscription Property \'%s\' : \'%s\' does not match what was specifed at Creation %s" % (key, check_payload[key], creation_payload[key]) )
               
        else: 
            assertion_status = log.WARN
            log.assertion_log('line', "~ The subscription does not contain \'%s\' Property specifed at Creation" % key )
            

    return(assertion_status)

###################################################################################################
# Name: Assertion_8_1_5_1()                                                
# Assertion text: 
#   The body of the response, if any, shall contain a representation of the subscription resource.                           
###################################################################################################              
def Assertion_8_1_5_1(self, log) :
 
    log.AssertionID = '8.1.5.1'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    # the URI of the successful event creation was stored during run of 8.1.3
    if (self.Assertion8_1_3EventSubscriptionURI == None):
        assertion_status = log.WARN
        log.assertion_log('line', " The assertion 8.1.3 event subscription failed... no subscription response body to check") 
    else:
        # check to see that the subscription response body contains all of the config parameters specified during creation
        assertion_status = EventAssertionPropertyCheck(self.Assertion8_1_3EventSubscriptionJSON, self.Assertion8_1_3EventSubscriptionPayload, log)
        if (assertion_status != log.PASS):
            assertion_status = log.FAIL

    log.assertion_log(assertion_status, None)

    return (assertion_status)
#
## end Assertion 8_1_5_1

###################################################################################################
# Name: Assertion_8_1_5_2(self, log)                                               
# Assertion text: 
#   Sending an HTTP GET to the subscription resource shall 
#   return the configuration of the subscription.                               
###################################################################################################              
def Assertion_8_1_5_2(self, log) :
 
    log.AssertionID = '8.1.5.2'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'

    rq_headers = self.request_headers()

    # the URI of the successful event creation was stored during run of 8.1.3
    if (self.Assertion8_1_3EventSubscriptionURI == None):
        assertion_status = log.WARN
        log.assertion_log('line', " The assertion 8.1.3 event subscription failed... no subscription configuration to GET") 

    else:
        # GET the subscription
        json_payload, headers, status = self.http_GET(self.Assertion8_1_3EventSubscriptionURI, rq_headers, authorization)
        assertion_status_ = self.response_status_check(self.Assertion8_1_3EventSubscriptionURI, status, log)      
        # manage assertion status
        assertion_status = log.status_fixup(assertion_status,assertion_status_)
            
        # check to see that the subscription contains all of the config parameters specified during creation
        assertion_status = EventAssertionPropertyCheck(self.Assertion8_1_3EventSubscriptionJSON, json_payload, log)

    log.assertion_log(assertion_status, None)
    return (assertion_status)
#
## end Assertion 8_1_5_2

###################################################################################################
# Name: Assertion_8_4_3(self, log)                                               
# Assertion text: 
# The managed device must respond to M-SEARCH queries searching for Search Target (ST) of the
# Redfish Service from clients with the AL pointing to the Redfish service root URI.                          
###################################################################################################        
def Assertion_8_4_3(self, log) :
 
    log.AssertionID = '8.4.3'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    authorization = 'on'
    rq_headers = self.request_headers()

    SSDP_ADDR = "239.255.255.250";
    SSDP_PORT = 1900;
    SSDP_MX = 2;
    SSDP_ST = "URN:dmtf-org:service:redfish-rest:1"
    #SSDP_ST = "ssdp:all"

    relative_uris = self.relative_uris
    ## 
    # SSDP support is optional: check to see if the service supports/has SSDP enabled.
    # The property for SSDP is defined in the 'ManagerNetworkProtocol.xml' schema
    ##
    ServiceSupportsSSDP = False
     
    resource = 'NetworkProtocol'   
    for relative_uri in relative_uris:   
        if resource in relative_uri:
            r_url = relative_uris[relative_uri]
            # GET first
            json_payload, headers, status = self.http_GET(r_url, rq_headers, authorization)
            assertion_status_ = self.response_status_check(r_url, status, log)      
            # manage assertion status
            assertion_status = log.status_fixup(assertion_status,assertion_status_)
            if assertion_status_ != log.PASS: 
                pass       
            elif not json_payload:
                assertion_status = log.WARN 
                log.assertion_log('line', '~ unable to locate URI/payload for resource: %s nested in: %s' % (resource, r_url))
            else:
                # does the service support SSDP?
                try:
                    SSDPisEnabled = json_payload['SSDP']
                except:
                    log.assertion_log('line', '~ SSDP support is optional: this service does not appear to support SSDP')
                    log.assertion_log('line', '~ SSDP not found in payload from GET(%s) %s' % (r_url, rf_utility.json_string(json_payload)) )
    
                else:
                    try:
                        SSDPisEnabled = json_payload['SSDP']['ProtocolEnabled']
                    except:
                        log.assertion_log('line', 'GET(%s) payload: %s' % (r_url, rf_utility.json_string(json_payload)))
                        log.assertion_log('line', '~ ERROR: \'SSDP:ProtocolEnabled\' not found in payload') 
                        assertion_status = log.FAIL
    
                    else:       
                        if not SSDPisEnabled:
                            log.assertion_log('line', 'GET(%s) payload: %s' % (r_url, rf_utility.json_string(json_payload)))
                            log.assertion_log('line', '~  Note - SSDP appears to be Disabled : \'ProtocolEnabled(%s)\' is not \'true\'' % SSDPisEnabled)
                            assertion_status = log.WARN
                        else:
                            ServiceSupportsSSDP = True
                

            if(ServiceSupportsSSDP == True):

                ssdpRequestStr = "M-SEARCH * HTTP/1.1\r\n" + \
                            "MAN: \"ssdp:discover\"\r\n" + \
                            "HOST: %s:%d\r\n" % (SSDP_ADDR, SSDP_PORT) + \
                            "MX: %d\r\n" % (SSDP_MX) + \
                            "ST: %s\r\n" % (SSDP_ST) + "\r\n";

                log.assertion_log('line', '%s' % ssdpRequestStr)
     
                if (Python3 == True):
                    ssdpRequest = b'ssdpRequestStr'
                else:
                    ssdpRequest = ssdpRequestStr

                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(ssdpRequest, (SSDP_ADDR, SSDP_PORT))
                except:
                    exc_str = sys.exc_info()[0]
                    assertion_status = log.WARN
                    log.assertion_log('line', 'Socket error  %s' % exc_str) 

                try:
                    # wait for data to be returned on the M-Search for a few seconds...
                    few_seconds = 10
                    log.assertion_log('line', '...wating for m-search response for %d seconds...' % few_seconds) 
                    ready = select.select([sock], [], [], few_seconds)
                except:
                    exc_str = sys.exc_info()[0]
                    assertion_status = log.WARN
                    log.assertion_log('line', 'Socket/ready error  %s' % exc_str) 

                if (assertion_status == log.PASS):
                    if ready[0]:
                        data = sock.recv(4096)
                        log.assertion_log('line', 'Response received: %s' % data)

                        # check for the 'AL' response header -- is it pointing to the Redfish Service Root URI?
                        hdr = HTTPResponse.getheader('AL', default=None)
                        if (AL_hdr == None):
                            log.assertion_log('line', '\'AL\' header not found in m-search response')
                            assertion_status = log.FAIL
                        else:
                            log.assertion_log('line', '...m-search response received - \'AL\' header found = %s' % AL_hdr)

                            # do a get on the Redfish Service root uri...
                            json_payload, headers, status = self.http_GET(AL_hdr, rq_headers, authorization)
                            assertion_status_ = self.response_status_check(AL_hdr, status, log)      
                            # manage assertion status
                            assertion_status = log.status_fixup(assertion_status,assertion_status_)
                            
                    else:
                        log.assertion_log('line', '...No Response from the service...')
                        assertion_status  = log.FAIL

    log.assertion_log(assertion_status, None)

    return (assertion_status)
#
## end Assertion 8_4_3

###################################################################################################
# run(self, log):
# Takes sut obj and logger obj 
###################################################################################################
def run(self, log):
    # Create/Delete an event subscription: these assertions need to be run in series
    assertion_status = Assertion_8_1_3(self, log)
    if (assertion_status == log.PASS):
        try:
            # check 'location' in resp headers
            assertion_status = Assertion_8_1_5(self, log)
            # check to see if the subscription response body 'contains a represenation of the resource' created
            assertion_status = Assertion_8_1_5_1(self, log)
            # GET the uri of the newly created subscription
            assertion_status = Assertion_8_1_5_2(self, log)
        except:
            # catch rogue exceptions... be sure not to leave a rogue event subscription in place on the service...
            exc_str = sys.exc_info()[0]
            log.assertion_log('line', "~ Note: a Python exception %s occurred during event subscription verification" % exc_str)          
    # remove the event subscription
    assertion_status = Assertion_8_1_4(self, log)
    #
    ##  End Create/Delete an event subscription       
    # M-Search - note as of 6/16 a service has not been found to  run this on which reports support for SSDP
    assertion_status = Assertion_8_4_3(self, log)               