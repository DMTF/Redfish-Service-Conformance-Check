##################################################################################################
# File: TEST_manager_account.py 
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
# Description: The value of this property shall be the password for this account.  
# The value shall be null for GET requests.
# Name: Assertion_MANA101(self, log)
##################################################################################################
def Assertion_MANA101(self, log):

    log.AssertionID = 'MANA101'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    try:
        json_payload_get, headers, status = self.http_GET(self.sut_toplevel_uris['AccountService']['url'], rq_headers, authorization)
        
        try:
            json_payload_get, headers, status = self.http_GET(json_payload_get['Accounts']['@odata.id'], rq_headers, authorization)

            try:
                json_payload_get, headers, status = self.http_GET(json_payload_get['Members'][0]['@odata.id'], rq_headers, authorization)

                if json_payload_get['Password'] == None:
                    assertion_status = log.PASS        
                    return (assertion_status)
                else:
                    assertion_status = log.FAIL        
                    log.assertion_log('line', "The value for password is not NULL.")
                    return (assertion_status)

            except:
                assertion_status = log.WARN        
                log.assertion_log('line', "No accounts are present.")
                return (assertion_status)

        except:
            assertion_status = log.WARN        
            log.assertion_log('line', "Accounts property is absent.")
            return (assertion_status)

    except:
        assertion_status = log.WARN        
        log.assertion_log('line', "AccountService property is absent.")
        return (assertion_status)


##################################################################################################
# Description: The value of this property shall be the password for this account.  
# The value of this property shall be the user name for this account.
# The value of this property shall be the ID of the Role resource that configured for this 
# account.  The service shall reject POST, PATCH, or PUT operations that provide a RoleId that 
# does not exist by returning HTTP 400 (Bad Request).
# Name: Assertion_MANA103(self, log)
##################################################################################################
def Assertion_MANA103(self, log):
    log.AssertionID = 'MANA103'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()
    # print(json.dumps(json_payload_get, sort_keys=True, indent=4)

    try:
        json_payload_get, headers, status = self.http_GET(self.sut_toplevel_uris['AccountService']['url'], rq_headers, authorization)
        
        try:
            json_payload_get_P, headers, status = self.http_GET(json_payload_get['Accounts']['@odata.id'], rq_headers, authorization)

            try:
                json_payload_get, headers, status = self.http_GET(json_payload_get_P['Members'][0]['@odata.id'], rq_headers, authorization)
                managerRoleId =  json_payload_get['RoleId']
                print(json.dumps(json_payload_get, sort_keys=True, indent=4))
                
                # Testing if the service shall reject PATCH operation that provide a RoleId that does not exist by returning HTTP 400 (Bad Request).

                rq_body = {'RoleId': False}
                json_payload_get_P, headers, status = self.http_PATCH(json_payload_get_P['Members'][0]['@odata.id'], rq_headers, rq_body, authorization)

                if status != 400:
                    assertion_status = log.FAIL        
                    log.assertion_log('line', "The service did not reject the PATCH operation that provided a RoleId that does not exist by returning HTTP 400 (Bad Request)" )
                    return (assertion_status)

                try:
                    json_payload_get, headers, status = self.http_GET(json_payload_get['Links']['Role']['@odata.id'], rq_headers, authorization)

                    if managerRoleId == json_payload_get['Id']:
                        assertion_status = log.PASS        
                        return (assertion_status)
                    else:
                        assertion_status = log.FAIL        
                        log.assertion_log('line', "The value of this property does not match the Id property of the role referenced in the Role resource referenced from Links")
                        return (assertion_status)

                except:
                    assertion_status = log.WARN        
                    log.assertion_log('line', "No accounts are present.")
                    return (assertion_status)

            except:
                assertion_status = log.WARN        
                log.assertion_log('line', "No accounts are present.")
                return (assertion_status)

        except:
            assertion_status = log.WARN        
            log.assertion_log('line', "Accounts property is absent.")
            return (assertion_status)

    except:
        assertion_status = log.WARN        
        log.assertion_log('line', "AccountService property is absent.")
        return (assertion_status)


# run(self, log):
# Takes sut obj and logger obj
###################################################################################################
def run(self, log):
    assertion_status = Assertion_MANA101(self,log)
    assertion_status = Assertion_MANA103(self,log)
