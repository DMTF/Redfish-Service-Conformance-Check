# Copyright Notice:
# Copyright 2016-2018 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Service-Conformance-Check/blob/master/LICENSE.md

#####################################################################################################
# File: TEST_collectioncapabilities_schema.py
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
# Name: Assertion COLL103(self,log)
# Description:
# The value of this property shall be a reference to a Resource that matches the type for the given 
# collection and shall contain annotations that describe the properties allowed in the POST request.
###################################################################################################
def Assertion_COLL103(self,log) :
    log.AssertionID = 'COLL103'
    assertion_status = log.PASS
    log.assertion_log('BEGIN_ASSERTION', None)
    relative_uris = self.relative_uris
    print('Checking if all responses are in JSON')
    authorization = 'on'
    rq_headers = self.request_headers()

    for relative_uri in relative_uris:
        json_payload, headers, status = self.http_GET(relative_uris[relative_uri], rq_headers, authorization)

        if status == 200 :
            if not json_payload:
                print ('The response received is not in JSON %s'% json_payload)
                assertion_status = log.FAIL
        else :
            continue
    log.assertion_log(assertion_status, None)
    return (assertion_status)

#
## end Assertion BOOT102

# run(self, log):
# Takes sut obj and logger obj 
###################################################################################################
def run(self, log): 
      
    assertion_status = Assertion_COLL103(self,log)