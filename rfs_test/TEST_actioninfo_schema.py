# Copyright Notice:
# Copyright 2016-2019 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/master/LICENSE.md

#####################################################################################################
# File: TEST_actioninfo_schema.py
# Description: Redfish service conformance check tool. This module contains implemented assertions for
#   SUT.These assertions are based on operational checks on Redfish Service to verify that it conforms
#   to the normative statements from the Redfish specification.
#   See assertions in redfish-assertions.xlxs for assertions summary
#
# Verified/operational Python revisions (Windows OS) :
#       3.5.2
#
# Initial code released : 01/2018
#   Robin Thekkadathu Ronson ~ Texas Tech University
#####################################################################################################

import urllib3
import json
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from time import gmtime, strftime

accSerData = None

# current spec followed for these assertions
REDFISH_SPEC_VERSION = "Version 1.2.2"


###################################################################################################
# Name: Assertion_ACTI104(self, log) :Action Info                                          
# Assertion text: 
#This property shall return true if the parameter is required to be present to perform the 
#associated Action, and shall be false if the parameter is not required (optional) to perform the
#associated Action.
###################################################################################################
def Assertion_ACTI104(self,log) :
    log.AssertionID = 'ACTI104'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    relative_uris = self.relative_uris
    authorization = 'on'
    rq_headers = self.request_headers()

    try:

        json_payload, headers, status = self.http_GET(relative_uris['Root Service_Systems'], rq_headers, authorization)

    except:

        assertion_status = log.WARN
        log.assertion_log('line', "Resource, is not found or Root Service_Systems is not found in relative_uris")
        return assertion_status

    try:

        json_payload, headers, status = self.http_GET(json_payload['Members'][0]['@odata.id'], rq_headers, authorization)

    except:

        assertion_status = log.WARN
        log.assertion_log('line', "~  No systems are found at resource %s" % (relative_uris['Root Service_Systems']))
        return assertion_status
    
    try:
        
        ActionInfo = json_payload['Actions']['#ComputerSystem.Reset']['ActionInfo']
    
    except:

        assertion_status = log.WARN
        log.assertion_log('line', "~  No ActionInfo object found at ComputerSystem_#0")
        return assertion_status
   
    try: 
        
        Required = ActionInfo['Parameters'][0]['Required']
    
    except:
        
        assertion_status = log.WARN
        log.assertion_log('line', "~ Required Parameter not found inside of ActionInfo for ComputerSystem_#0")
        return assertion_status
  
    if Required: 
        # Performing an action without parametres when parameters are required.  
        rq_body = {
        }
        json_payload, headers, status = self.http_POST(self.sut_toplevel_uris[root_link_key + '/Actions/ComputerSystem.Reset']['url'], rq_headers, rq_body, authorization)

    if not status >= 400 and not status <= 599:  
        assertion_status = log.FAIL
        log.assertion_log('line', "Posting an action without parameter did not return an error status when the Required property was true")
        return assertion_status

    assertion_status = log.PASS
    log.assertion_log('line', "~ Assertion Passed")

    return assertion_status

## end Assertion_ACTI104

#Testing

def run(self, log):

    assertion_status = Assertion_ACTI104(self, log)


    

    
    

    
    



    
