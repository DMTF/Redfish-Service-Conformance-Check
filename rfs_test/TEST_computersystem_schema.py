# Copyright Notice:
# Copyright 2016-2018 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/master/LICENSE.md

#####################################################################################################
# File: TEST_ComputerSystem_schema.py
# Description: Redfish service conformance check tool. This module contains implemented assertions for
#   SUT.These assertions are based on operational checks on Redfish Service to verify that it conforms
#   to the normative statements from the Redfish specification.
#   See assertions in redfish-assertions.xlxs for assertions summary
#
# Verified/operational Python revisions (Ubuntu OS) :
#       3.5.2

# Initial code released : 05/2018
#   Robin Thekkadathu Ronson ~ Texas Tech University
#####################################################################################################

import json
import string
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

# Helper Functions

def patch_test(self, uri):
    authorization = 'on'
    rq_headers = self.request_headers()
    rq_body = {'IndicatorLED': 'Unknown'}
    json_payload, headers, status = self.http_PATCH(uri, rq_headers, rq_body, authorization)
    return status == 400

def put_test(self, uri):
    authorization = 'on'
    rq_headers = self.request_headers()
    rq_body = {'IndicatorLED': 'Unknown'}
    json_payload, headers, status = self.http_PUT(uri, rq_headers, rq_body, authorization)
    return status == 405

###################################################################################################
# Name: Assertion_COMP139(self, log) : Assembly
# Assertion text:
# This value shall represent the Indicator LED is in an unknown state.  The service shall reject 
# PATCH or PUT requests containing this value by returning HTTP 400 (Bad Request).
###################################################################################################

def Assertion_COMP139(self, log):
    log.AssertionID = 'COMP139'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    relative_uris = self.relative_uris 
   
    try:

        json_payload, headers, status = self.http_GET(relative_uris['Root Service_Systems'], rq_headers, authorization)
    
    except: 

        assertion_status = log.WARN
        log.assertion_log('line', "Resource %s, is not found." % (relative_uris['Root Service_Systems']))
        return assertion_status

    try:

        json_payload, headers, status = self.http_GET(json_payload['Members'][0]['@odata.id'], rq_headers, authorization)

    except: 

        assertion_status = log.WARN
        log.assertion_log('line', "No systems are found at resource %s" % (relative_uris['Root Service_Systems']))
        return assertion_status


    try:

       json_payload, headers, status = self.http_GET(json_payload['IndicatorLED'], rq_headers, authorization)

    except:

       assertion_status = log.WARN
       log.assertion_log('line', "Property IndicatorLED is not found.")
       return assertion_status


    json_payload, headers, status = self.http_GET(relative_uris['Root Service_Systems'], rq_headers, authorization)


    if patch_test(self, json_payload['Members'][0]['@odata.id']) and put_test(self, json_payload['Members'][0]['@odata.id']):

        assertion_status = log.PASS
        log.assertion_log('line', "Assertion Passed")
        return assertion_status

    else:

        assertion_status = log.FAIL
        log.assertion_log('line', "Assertion Failed")
        return assertion_status

def run(self, log):
    assertion_status = Assertion_COMP139(self, log)
