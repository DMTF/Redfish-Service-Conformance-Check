# Copyright Notice:
# Copyright 2016-2018 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/master/LICENSE.md

#####################################################################################################
# File: TEST_event_service.py 
# Description: Redfish service conformance check tool. This module contains assertions for 
# EventService
#
# Verified/operational Python revisions (Mac OS) :
#       3.4.3
#
# Initial code released : 09/2018
#   Robin Ronson ~ Texas Tech University
#####################################################################################################
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
from collections import OrderedDict
import time

REDFISH_SPEC_VERSION = "Version 1.0.5"

#####################################################################################################
# Name: Assertion_EVEN110(self, log)
# Description: The value of this property shall be the number of retrys attempted for any given event 
# to the subscription destination before the subscription is terminated.  This retry is at the 
# service level, meaning the HTTP POST to the Event Destination was returned by the HTTP operation as 
# unsuccessful (4xx or 5xx return code) or an HTTP timeout occurred this many times before the Event 
# Destination subscription is terminated. 
#####################################################################################################
def Assertion_EVEN110(self, log) : # self here is service's instance..
    log.AssertionID = 'EVEN110'
    assertion_status =  log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)

    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()
    json_payload_get, headers, status = self.http_GET(self.sut_toplevel_uris['AccountService']['url'], rq_headers, authorization)

    ## Assertion verification logic goes here...

    #sample intermediate log string going to the text logfile and the xlxs file
    #log.assertion_log('line', "~ GET %s" % self.Redfish_URIs['Protocol_Version'])
    #sample intermediate log string to text logfile
    #log.assertion_log('tx_comment', "~ GET %s" % self.Redfish_URIs['Protocol_Version'])

    #Note: any assertion which FAILs or WARNs should place an explanation in the the reporting spreadsheet
    #be careful with volume of text here ~ needs to fit in a spreadsheet cell..
    #if (assertion_status != log.PASS):
        # this text will go only into the comment section of the xlxs assertion run spreadsheet
        log.assertion_log('XL_COMMENT', ('~ GET %s : %s %s' % (self.Redfish_URIs['Protocol_Version'], assertion_status, "a meaningful failure note")) )

    ## log completion status
    #log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion EVEN110 

# run(self, log):
# Takes sut obj and logger obj
###################################################################################################
def run(self, log):
    assertion_status = Assertion_EVEN110(self,log)
