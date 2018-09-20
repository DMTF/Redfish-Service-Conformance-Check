opyright Notice:
# Copyright 2016-2018 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-C

##################################################################################################
# File: TEST_event_service.py 
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




