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
#
# Initial code released : 05/2018
#   Robin Thekkadathu Ronson ~ Texas Tech University
#####################################################################################################

###################################################################################################
# Name: Assertion_COMP139(self, log) : Assembly
# Assertion text:
# This value shall represent the Indicator LED is in an unknown state.  The service shall reject 
# PATCH or PUT requests containing this value by returning HTTP 400 (Bad Request).
###################################################################################################

import json
import string
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

# current spec followed for these assertions
REDFISH_SPEC_VERSION = "Version 1.2.2"

def Assertion_COMP139(self, log):
	
	log.AssertionID = 'COMP139'
	assertion_status = log.PASS
	log.assertion_log('BEGIN_ASSERTION', None)

	relative_uris = self.relative_uris
	authorization = 'on'
	rq_headers = self.request_headers()

	json_payload_get, headers, status = self.http_GET(
	    self.sut_toplevel_uris['ComputerSystem']['url'], rq_headers, authorization)

	try: 
		LEDStatus = json_payload_get['IndicatorLED']

		if LEDStatus == "Unknown": 	
			AccountServicetch_value = False
			rq_body = {patch_key: patch_value}
			json_payload, headers, status = self.http_PATCH(self.sut_toplevel_uris['AccountService']['url'],rq_headers, rq_body, authorization) 
		
		else: 
			


	except:
    		assertion_status = log.WARN
        	log.assertion_log('line', "~ \'IndicatorLED\' not found in the payload from GET %s" % (
	        '/redfish/v1/ComputerSystem'))
		return assertion_status

