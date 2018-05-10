# Copyright Notice:
# Copyright 2016-2018 Distributed Management Task Force, Inc. All rights reserved.
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

    root_link_key = 'Systems'    

    json_payload, headers, status = self.http_GET(self.sut_toplevel_uris[root_link_key]['url'], rq_headers, authorization)

    if status == 200: 
          try: 
            authorization = 'on'
            json_payload, headers, status = self.http_GET('/redfish/v1/Managers/MultiBladeBMC/LogServices/Log/Entries/', rq_headers, authorization)
            BootOptionEnabled = (json_payload['BootOptionEnabled'])

            if BootOptionEnabled: 
                #  Boot Option referenced in the Boot Order array found on the Computer System shall be skipped. (How can I check this ?)

          except: 
            assertion_status = log.WARN
            log.assertion_log('line', "~ \'BootOptionEnabled\' not found in the payload from GET %s" % (self.sut_toplevel_uris[root_link_key]['url']))
            
    else
        assertion_status = log.WARN
        log.assertion_log('line', "~ \'BootOptionEnabled\' not found in the payload from GET %s" % (self.sut_toplevel_uris[root_link_key]['url']))

    log.assertion_log(assertion_status, None)
    return (assertion_status)

## end Assertion_ACTI104

#Testing

def run(self, log):

    assertion_status = Assertion_ACTI104(self, log)


    

    
    

    
    



    
