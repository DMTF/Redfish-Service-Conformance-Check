##################################################################################################
# File: TEST_manager.py 
# Description: Redfish service conformance check tool. This module contains assertions for 
# EventService
#
# Verified/operational Python revisions (Mac OS) :
#       3.4.3
#
# Initial code released : 09/2018
#   Robin Ronson ~ Texas Tech University
##################################################################################################
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
    from urllib import urlopen
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
import os
from collections import OrderedDict
import time

##################################################################################################
# Description: The value of this property shall be a link to a collection of type
# EthernetInterfaceCollection
# Name: Assertion_MANA111(self, log)
##################################################################################################
def Assertion_MANA111(self, log):

    log.AssertionID = 'MANA111'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    try:
        json_payload_get, headers, status = self.http_GET(self.sut_toplevel_uris['Managers']['url'], rq_headers, authorization)
        
        try:
            json_payload_get, headers, status = self.http_GET(json_payload_get['Members'][0]['@odata.id'], rq_headers, authorization)
            
            try:
                json_payload_get, headers, status = self.http_GET(json_payload_get['EthernetInterfaces']['@odata.id'], rq_headers, authorization)

                if json_payload_get['Name'] == 'Ethernet Network Interface Collection':
                    assertion_status = log.PASS        
                    return (assertion_status)

                else: 
                    assertion_status = log.FAIL        
                    log.assertion_log('line', "Ethernet Network Interface Collection not found. ")
                    return (assertion_status)

            except:
                assertion_status = log.WARN        
                log.assertion_log('line', "EthernetInterfaces property not found.")
                return (assertion_status)

        except:
            assertion_status = log.WARN        
            log.assertion_log('line', " No manager account is present.")
            return (assertion_status)

    except:
        assertion_status = log.WARN        
        log.assertion_log('line', "Managers property is absent.")
        return (assertion_status)

##################################################################################################
# Description: The value of this property shall be a link to a collection of type
# SerialInterfaceCollection
# Name: Assertion_MANA112(self, log)
##################################################################################################
def Assertion_MANA112(self, log):

    log.AssertionID = 'MANA112'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    try:
        json_payload_get, headers, status = self.http_GET(self.sut_toplevel_uris['Managers']['url'], rq_headers, authorization)
        
        try:
            json_payload_get, headers, status = self.http_GET(json_payload_get['Members'][0]['@odata.id'], rq_headers, authorization)
            
            try:
                json_payload_get, headers, status = self.http_GET(json_payload_get['SerialInterfaces']['@odata.id'], rq_headers, authorization)

                if json_payload_get['Name'] == 'Serial Interface Collection':
                    assertion_status = log.PASS        
                    return (assertion_status)

                else: 
                    assertion_status = log.FAIL        
                    log.assertion_log('line', "Serial Interface Collection not found. ")
                    return (assertion_status)

            except:
                assertion_status = log.WARN        
                log.assertion_log('line', "SerialInterfaces property not found.")
                return (assertion_status)

        except:
            assertion_status = log.WARN        
            log.assertion_log('line', " No manager account is present.")
            return (assertion_status)

    except:
        assertion_status = log.WARN        
        log.assertion_log('line', "Managers property is absent.")
        return (assertion_status)

##################################################################################################
# Description: The value of this property shall contain a reference to a resource of type 
# ManagerNetworkProtocol which represents the network services for this manager.
# Name: Assertion_MANA113(self, log)
##################################################################################################
def Assertion_MANA113(self, log):

    log.AssertionID = 'MANA113'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    try:
        json_payload_get, headers, status = self.http_GET(self.sut_toplevel_uris['Managers']['url'], rq_headers, authorization)
        
        try:
            json_payload_get, headers, status = self.http_GET(json_payload_get['Members'][0]['@odata.id'], rq_headers, authorization)
            
            try:
                json_payload_get, headers, status = self.http_GET(json_payload_get['NetworkProtocol']['@odata.id'], rq_headers, authorization)

                if json_payload_get['Name'] == 'Manager Network Protocol':
                    assertion_status = log.PASS        
                    return (assertion_status)

                else: 
                    assertion_status = log.FAIL        
                    log.assertion_log('line', "ManagerNetworkProtocol not found. ")
                    return (assertion_status)

            except:
                assertion_status = log.WARN        
                log.assertion_log('line', "ManagerNetworkProtocol property not found.")
                return (assertion_status)

        except:
            assertion_status = log.WARN        
            log.assertion_log('line', " No manager account is present.")
            return (assertion_status)

    except:
        assertion_status = log.WARN        
        log.assertion_log('line', "Managers property is absent.")
        return (assertion_status)

##################################################################################################
# Description: The value of this property shall contain a reference to a collection of type 
# LogServiceCollection which are for the use of this manager.
# Name: Assertion_MANA114(self, log)
##################################################################################################
def Assertion_MANA114(self, log):

    log.AssertionID = 'MANA114'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    try:
        json_payload_get, headers, status = self.http_GET(self.sut_toplevel_uris['Managers']['url'], rq_headers, authorization)
        
        try:
            json_payload_get, headers, status = self.http_GET(json_payload_get['Members'][0]['@odata.id'], rq_headers, authorization)
            
            try:
                json_payload_get, headers, status = self.http_GET(json_payload_get['LogServices']['@odata.id'], rq_headers, authorization)

                if json_payload_get['Name'] == 'Log Service Collection':
                    assertion_status = log.PASS        
                    return (assertion_status)

                else: 
                    assertion_status = log.FAIL        
                    log.assertion_log('line', "LogServiceCollection not found. ")
                    return (assertion_status)

            except:
                assertion_status = log.WARN        
                log.assertion_log('line', "Log Service Collection property not found.")
                return (assertion_status)

        except:
            assertion_status = log.WARN        
            log.assertion_log('line', " No manager account is present.")
            return (assertion_status)

    except:
        assertion_status = log.WARN        
        log.assertion_log('line', "Managers property is absent.")
        return (assertion_status)

##################################################################################################
# Description: The value of this property shall contain a reference to a collection of type 
# VirtualMediaCollection which are for the use of this manager.
# Name: Assertion_MANA115(self, log)
##################################################################################################
def Assertion_MANA115(self, log):

    log.AssertionID = 'MANA115'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    try:
        json_payload_get, headers, status = self.http_GET(self.sut_toplevel_uris['Managers']['url'], rq_headers, authorization)
        
        try:
            json_payload_get, headers, status = self.http_GET(json_payload_get['Members'][0]['@odata.id'], rq_headers, authorization)
            
            try:
                json_payload_get, headers, status = self.http_GET(json_payload_get['VirtualMedia']['@odata.id'], rq_headers, authorization)

                if json_payload_get['Name'] == 'Virtual Media Services':
                    assertion_status = log.PASS        
                    return (assertion_status)

                else: 
                    assertion_status = log.FAIL        
                    log.assertion_log('line', "Virtual Media Services not found. ")
                    return (assertion_status)

            except:
                assertion_status = log.WARN        
                log.assertion_log('line', "VirtualMedia property not found.")
                return (assertion_status)

        except:
            assertion_status = log.WARN        
            log.assertion_log('line', " No manager account is present.")
            return (assertion_status)

    except:
        assertion_status = log.WARN        
        log.assertion_log('line', "Managers property is absent.")
        return (assertion_status)




# run(self, log):
# Takes sut obj and logger obj
###################################################################################################
def run(self, log):
    assertion_status = Assertion_MANA111(self,log)
    assertion_status = Assertion_MANA112(self,log)
    assertion_status = Assertion_MANA113(self,log)
    assertion_status = Assertion_MANA114(self,log)
    assertion_status = Assertion_MANA115(self,log)
