# Copyright Notice:
# Copyright 2016-2018 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/master/LICENSE.md

#####################################################################################################
# File: TEST_bootoption_schema.py
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
# Name: Assertion BOOT102(self,log)
# Description:
# The value of this property shall indicate if the Boot Option is enabled.  If this property is 
# set to false, the Boot Option referenced in the Boot Order array found on the Computer System 
# shall be skipped. In the UEFI context, this property shall influence the Load Option Active flag 
# for the Boot Option.
###################################################################################################
def Assertion_BOOT102(self,log) :
    log.AssertionID = 'BOOT102'
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
            log_collection = (json_payload['Members'])

          except: 
            assertion_status = log.FAIL
            log.assertion_log('line', "Failure attempt was not logged in after failed login attempts reached the threshold referenced by AccountLockoutThreshold")
    else
        assertion_status = log.FAIL
        log.assertion_log('line', "The systems resource was not found.")

    log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion BOOT102

# run(self, log):
# Takes sut obj and logger obj 
###################################################################################################
def run(self, log): 
      
    assertion_status = Assertion_BOOT102(self,log)