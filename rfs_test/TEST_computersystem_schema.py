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

def patch_test(uri):
    authorization = 'on'
    rq_headers = self.request_headers()
    rq_body = {LEDStatus: 'Test'}
    json_payload, headers, status = self.http_PATCH(uri, rq_headers, rq_body, authorization)
    return status == 400

def put_test(uri):
    authorization = 'on'
    rq_headers = self.request_headers()
    rq_body = {LEDStatus: 'Test'}
    json_payload, headers, status = self.http_PUT(uri, rq_headers, rq_body, authorization)
    return status == 400

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

    root_link_key = 'Systems'
    relative_uris = self.relative_uris[root_link_key]['url']

    for relative_uri in relative_uris:

        json_payload, headers, status = self.http_GET(relative_uri, rq_headers, authorization)
        
        try:
            LEDStatus = json_payload_get['IndicatorLED']

            if LEDStatus == "Unknown":
                if !patch_test(relative_uri) or !put_test(relative_uri):
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ \'IndicatorLED\' Assertion Failed")
                    return assertion_status
            
            else:
                assertion_status = log.INFO
                log.assertion_log('line', "~ \'IndicatorLED\' is not in the Unknown State")
                return assertion_status
            
        except: 
            assertion_status = log.WARN
            log.assertion_log('line', "~ \'IndicatorLED\' not found in the payload from GET %s" % (relative_uri))
            return assertion_status

    assertion_status = log.PASS
        log.assertion_log('line', "~ \'IndicatorLED\' Assertion Passed " % (relative_uri))
        return assertion_status


###################################################################################################
# Name: Assertion_COMP140(self, log) : Assembly
# Assertion text:
# This value shall represent the Indicator LED is in a solid on state.  If this value is not 
# supported by the service, the service shall reject PATCH or PUT requests containing this value by 
# returning HTTP 400 (Bad Request). 
###################################################################################################

def Assertion_COMP140(self, log):
    log.AssertionID = 'COMP140'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    root_link_key = 'Systems'
    relative_uris = self.relative_uris[root_link_key]['url']

    for relative_uri in relative_uris:

        json_payload, headers, status = self.http_GET(relative_uri, rq_headers, authorization)
        
        try:
            LEDStatus = json_payload_get['IndicatorLED']

            if LEDStatus == "Lit":
                if !patch_test(relative_uri) or !put_test(relative_uri):
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ \'IndicatorLED\' Assertion Failed")
                    return assertion_status
            
            else:
                assertion_status = log.INFO
                log.assertion_log('line', "~ \'IndicatorLED\' is not in the On State")
                return assertion_status
            
        except: 
            assertion_status = log.WARN
            log.assertion_log('line', "~ \'IndicatorLED\' not found in the payload from GET %s" % (relative_uri))
            return assertion_status

    assertion_status = log.PASS
        log.assertion_log('line', "~ \'IndicatorLED\' Assertion Passed " % (relative_uri))
        return assertion_status


###################################################################################################
# Name: Assertion_COMP141(self, log) : Assembly
# Assertion text:
# This value shall represent the Indicator LED is in a blinking state where the LED is being 
# turned on and off in repetition.  If this value is not supported by the service, the service 
# shall reject PATCH or PUT requests containing this value by returning HTTP 400 (Bad Request).
###################################################################################################

def Assertion_COMP141(self, log):
    log.AssertionID = 'COMP141'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    root_link_key = 'Systems'
    relative_uris = self.relative_uris[root_link_key]['url']

    for relative_uri in relative_uris:

        json_payload, headers, status = self.http_GET(relative_uri, rq_headers, authorization)
        
        try:
            LEDStatus = json_payload_get['IndicatorLED']

            if LEDStatus == "Blinking":
                if !patch_test(relative_uri) or !put_test(relative_uri):
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ \'IndicatorLED\' Assertion Failed")
                    return assertion_status
            
            else:
                assertion_status = log.INFO
                log.assertion_log('line', "~ \'IndicatorLED\' is not in the Unknown State")
                return assertion_status
            
        except: 
            assertion_status = log.WARN
            log.assertion_log('line', "~ \'IndicatorLED\' not found in the payload from GET %s" % (relative_uri))
            return assertion_status

    assertion_status = log.PASS
        log.assertion_log('line', "~ \'IndicatorLED\' Assertion Passed " % (relative_uri))
        return assertion_status


###################################################################################################
# Name: Assertion_COMP142(self, log) : Assembly
# Assertion text:
# This value shall represent the Indicator LED is in a solid off state.  If this value is not 
# supported by the service, the service shall reject PATCH or PUT requests containing this value 
# by returning HTTP 400 (Bad Request).
###################################################################################################

def Assertion_COMP142(self, log):
    log.AssertionID = 'COMP142'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    root_link_key = 'Systems'
    relative_uris = self.relative_uris[root_link_key]['url']

    for relative_uri in relative_uris:

        json_payload, headers, status = self.http_GET(relative_uri, rq_headers, authorization)
        
        try:
            LEDStatus = json_payload_get['IndicatorLED']

            if LEDStatus == "Off":
                if !patch_test(relative_uri) or !put_test(relative_uri):
                    assertion_status = log.FAIL
                    log.assertion_log('line', "~ \'IndicatorLED\' Assertion Failed")
                    return assertion_status
            
            else:
                assertion_status = log.INFO
                log.assertion_log('line', "~ \'IndicatorLED\' is not in the Unknown State")
                return assertion_status
            
        except: 
            assertion_status = log.WARN
            log.assertion_log('line', "~ \'IndicatorLED\' not found in the payload from GET %s" % (relative_uri))
            return assertion_status

    assertion_status = log.PASS
        log.assertion_log('line', "~ \'IndicatorLED\' Assertion Passed " % (relative_uri))
        return assertion_status


def run(self, log):
     assertion_status = Assertion_COMP139(self, log)
     assertion_status = Assertion_COMP140(self, log)
     assertion_status = Assertion_COMP141(self, log)
     assertion_status = Assertion_COMP142(self, log)
